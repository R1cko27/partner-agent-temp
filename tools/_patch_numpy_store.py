"""Фолбэк плотного поиска без Chroma: чтение vectors.npz напрямую.

Нужен, когда Chroma не может открыть базу (повреждение, блокировка файла,
ошибка code 14). Векторы уже лежат в `storage/index/vectors.npz`, поэтому
поиск работает по ним через numpy.
"""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

STORE = pathlib.Path("partner/engine/vectorstore.py")
RETRIEVER = pathlib.Path("partner/domain/retriever.py")
INGEST = pathlib.Path("ingest.py")

NUMPY_STORE = '''

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
        index_dir = Path(path).parent
        cache = index_dir / "vectors.npz"
        if cache.is_file():
            try:
                return NumpyVectorStore(cache)
            except Exception:  # noqa: BLE001
                return None
        return None
'''


def patch_store() -> None:
    text = STORE.read_text(encoding="utf-8")
    if "class NumpyVectorStore" in text:
        print("хранилище: фолбэк уже добавлен")
        return
    if "from pathlib import Path" not in text:
        text = text.replace("import json\n", "import json\nfrom pathlib import Path\n", 1)
    text = text.rstrip() + "\n" + NUMPY_STORE
    STORE.write_text(text, encoding="utf-8")
    print("хранилище: добавлен NumpyVectorStore и open_vector_store")


def patch_retriever() -> None:
    text = RETRIEVER.read_text(encoding="utf-8")
    if "open_vector_store" not in text:
        text = text.replace(
            "from ..engine.vectorstore import VectorStore",
            "from ..engine.vectorstore import VectorStore, open_vector_store",
        )
        text = text.replace(
            "vectors = VectorStore(chroma_dir)",
            "vectors = open_vector_store(chroma_dir)",
        )
        print("ретривер: использует open_vector_store")
    old = """        return self.vectors.query(vector, k=limit, where=self._where())"""
    new = """        raw = self.vectors.query(vector, k=limit, where=self._where())
        excluded = set(self._exclude_kinds)
        if excluded:
            raw = [
                (chunk_id, score)
                for chunk_id, score in raw
                if str((self._by_id.get(chunk_id) or {}).get("kind") or "") not in excluded
            ]
        return raw[:limit]"""
    if old in text and "excluded = set(self._exclude_kinds)" not in text:
        text = text.replace(old, new)
        print("ретривер: фильтр типов после плотного поиска")
    RETRIEVER.write_text(text, encoding="utf-8")


def patch_ingest() -> None:
    text = INGEST.read_text(encoding="utf-8")
    if "open_vector_store" in text:
        print("ingest: уже использует open_vector_store")
        return
    text = text.replace(
        "from partner.engine.vectorstore import VectorStore",
        "from partner.engine.vectorstore import VectorStore, open_vector_store",
    )
    old = "        vectors = VectorStore(settings.chroma_dir)"
    new = (
        "        vectors = open_vector_store(settings.chroma_dir)\n"
        "        if vectors is not None and getattr(vectors, \"supports_where\", True) is False:\n"
        "            log(\"  ! Chroma недоступна — векторы читаются из vectors.npz\")"
    )
    if old in text:
        text = text.replace(old, new)
        print("ingest: переход на open_vector_store")
    INGEST.write_text(text, encoding="utf-8")


def main() -> int:
    patch_store()
    patch_retriever()
    patch_ingest()
    return 0


if __name__ == "__main__":
    sys.exit(main())
