"""Векторное хранилище на ChromaDB (persistent, локально).

Коллекция хранит текст чанка и метаданные, поэтому поиск можно отдать Chroma,
а не держать второй массив текстов. Векторы передаются явно (см. embeddings.py):
это отвязывает хранилище от конкретной embedding-функции и версии Chroma.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

COLLECTION = "s2ze_kb"


def _plain_vector(vector: Any) -> List[float]:
    """Вектор в виде обычных float: Chroma не принимает np.float32 в метаданных."""
    try:
        import numpy as np

        return np.asarray(vector, dtype="float32").reshape(-1).tolist()
    except Exception:  # noqa: BLE001
        return [float(value) for value in vector]


class VectorStore:
    def __init__(self, path: Path | str, collection: str = COLLECTION) -> None:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(self.path),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )
        self.name = collection
        self.collection = self._get_or_create()

    def _get_or_create(self):
        try:
            return self.client.get_or_create_collection(
                name=self.name, metadata={"hnsw:space": "cosine"}
            )
        except Exception:  # разные версии Chroma по-разному принимают metadata
            return self.client.get_or_create_collection(name=self.name)

    # --- запись ---------------------------------------------------------
    def reset(self) -> None:
        try:
            self.client.delete_collection(self.name)
        except Exception:
            pass
        self.collection = self._get_or_create()

    def add(
        self,
        chunks: Sequence[Any],
        embeddings: Sequence[Sequence[float]],
        batch_size: int = 256,
    ) -> int:
        if not chunks or not embeddings:
            return 0
        added = 0
        for start in range(0, len(chunks), batch_size):
            batch_chunks = chunks[start:start + batch_size]
            batch_vectors = embeddings[start:start + batch_size]
            if not batch_chunks or not batch_vectors:
                continue
            self.collection.add(
                ids=[chunk.id for chunk in batch_chunks],
                documents=[chunk.text for chunk in batch_chunks],
                embeddings=[_plain_vector(vector) for vector in batch_vectors],
                metadatas=[self._metadata(chunk) for chunk in batch_chunks],
            )
            added += len(batch_chunks)
        return added

    @staticmethod
    def _metadata(chunk: Any) -> Dict[str, Any]:
        meta: Dict[str, Any] = {
            "doc_id": str(chunk.doc_id),
            "kind": str(chunk.kind),
            "title": str(chunk.title)[:500],
            "source": str(chunk.source)[:500],
            "index": int(chunk.index),
        }
        if chunk.entities:
            meta["entities"] = json.dumps(chunk.entities, ensure_ascii=False)[:1000]
        return meta

    def upsert(
        self,
        chunks: Sequence[Any],
        embeddings: Sequence[Sequence[float]],
        batch_size: int = 256,
    ) -> int:
        """Добавляет и обновляет записи: для инкрементальной сборки.

        Реализовано как delete + add: `collection.upsert` в части версий Chroma
        падает на валидации метаданных, а `add` работает стабильно.
        """
        if not chunks or not embeddings:
            return 0
        ids = [chunk.id for chunk in chunks]
        for start in range(0, len(ids), 500):
            try:
                self.collection.delete(ids=ids[start:start + 500])
            except Exception:  # noqa: BLE001 — старых записей может не быть
                pass
        return self.add(chunks, embeddings, batch_size)

    def delete_ids(self, ids: Sequence[str], batch_size: int = 500) -> int:
        clean = [str(item) for item in ids if item]
        removed = 0
        for start in range(0, len(clean), batch_size):
            batch = clean[start:start + batch_size]
            try:
                self.collection.delete(ids=batch)
                removed += len(batch)
            except Exception:  # noqa: BLE001
                continue
        return removed

    def all_vectors(self, batch_size: int = 1000) -> List[Tuple[str, Any]]:
        """Выгружает все векторы: нужен для первичного заполнения кеша."""
        result: List[Tuple[str, Any]] = []
        total = self.count()
        offset = 0
        while offset < total:
            try:
                page = self.collection.get(
                    include=["embeddings"], limit=batch_size, offset=offset
                )
            except Exception:  # noqa: BLE001
                break
            ids = list(page.get("ids") or [])
            embeddings = page.get("embeddings")
            if embeddings is None or len(ids) == 0:
                break
            for chunk_id, vector in zip(ids, embeddings):
                result.append((chunk_id, vector))
            offset += len(ids)
        return result

    # --- чтение ---------------------------------------------------------
    def count(self) -> int:
        try:
            return int(self.collection.count())
        except Exception:
            return 0

    def query(
        self,
        embedding: Sequence[float],
        k: int = 20,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float]]:
        """Возвращает [(chunk_id, score)] по убыванию близости (1 - distance)."""
        if not embedding:
            return []
        try:
            result = self.collection.query(
                query_embeddings=[list(embedding)],
                n_results=max(1, int(k)),
                where=where,
                include=["distances"],
            )
        except Exception:
            return []
        ids = (result.get("ids") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        return [
            (chunk_id, 1.0 - float(distance))
            for chunk_id, distance in zip(ids, distances)
        ]

    def get_texts(self, ids: Iterable[str]) -> Dict[str, str]:
        ids = list(ids)
        if not ids:
            return {}
        try:
            result = self.collection.get(ids=ids, include=["documents"])
        except Exception:
            return {}
        return {
            chunk_id: document or ""
            for chunk_id, document in zip(result.get("ids", []), result.get("documents", []))
        }


class NumpyVectorStore:
    """Плотный поиск по vectors.npz: замена Chroma, если та недоступна."""

    supports_where = False

    def __init__(self, path: Path) -> None:
        import numpy as np

        payload = np.load(path, allow_pickle=False)
        self.path = Path(path)
        self.ids = [str(item) for item in payload["ids"]]
        matrix = np.asarray(payload["vectors"], dtype="float32")
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        self.matrix = matrix / np.maximum(norms, 1e-8)
        self._np = np

    def count(self) -> int:
        return len(self.ids)

    def all_vectors(self):
        return [(chunk_id, self.matrix[index]) for index, chunk_id in enumerate(self.ids)]

    def query(
        self,
        embedding: Sequence[float],
        k: int = 20,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[str, float]]:
        if not embedding or not self.ids:
            return []
        query = self._np.asarray(embedding, dtype="float32").reshape(-1)
        norm = float(self._np.linalg.norm(query))
        if norm <= 0:
            return []
        query = query / norm
        scores = self.matrix @ query
        # where не поддерживаем: метаданных в npz нет, поэтому отдаём больше
        # кандидатов, а фильтр по типам применяет ретривер.
        take = max(1, int(k)) * (3 if where else 1)
        top = self._np.argsort(-scores)[:take]
        return [(self.ids[int(index)], float(scores[int(index)])) for index in top]


def open_vector_store(path: Path | str, collection: str = COLLECTION):
    """Chroma, а при её недоступности — чтение векторов из npz рядом с индексом."""
    try:
        return VectorStore(path, collection)
    except Exception:  # noqa: BLE001
        base = Path(path).parent
        candidates = [base / "vectors.npz", base / "index" / "vectors.npz", Path(path) / "vectors.npz"]
        cache = next((item for item in candidates if item.is_file()), None)
        if cache is not None:
            try:
                return NumpyVectorStore(cache)
            except Exception:  # noqa: BLE001
                return None
        return None
