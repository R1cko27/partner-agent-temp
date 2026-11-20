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
                embeddings=[list(vector) for vector in batch_vectors],
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
