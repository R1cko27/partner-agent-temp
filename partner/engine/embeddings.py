"""Эмбеддинги для векторного поиска.

DeepSeek API не предоставляет эмбеддингов, поэтому векторы считаются локально:

1. `fastembed` + `paraphrase-multilingual-MiniLM-L12-v2` (ONNX, 384 измерения) —
   мультиязычная модель: русские вопросы ищутся по английским названиям карт;
2. запасной вариант — встроенная ONNX-модель ChromaDB (all-MiniLM-L6-v2);
3. если ничего не загрузилось — работаем только на BM25 (деградация без ошибок).

Векторы нормализуются к единичной длине, поэтому косинусное расстояние Chroma
совпадает с евклидовым порядком рангов при любой версии коллекции.
"""

from __future__ import annotations

import math
import os
from pathlib import Path
from typing import Iterable, List, Optional, Sequence


def _normalize(vector: Sequence[float]) -> List[float]:
    norm = math.sqrt(sum(float(value) * float(value) for value in vector))
    if not norm:
        return [0.0] * len(vector)
    return [float(value) / norm for value in vector]


class Embedder:
    def __init__(
        self,
        model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        cache_dir: Optional[Path] = None,
        enabled: bool = True,
    ) -> None:
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.backend = "none"
        self.dim = 0
        self._model = None
        self._chroma_ef = None
        self.error: Optional[str] = None

        if not enabled:
            self.error = "dense-поиск отключён настройкой RAG_USE_DENSE=0"
            return
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("HF_HOME", str(self.cache_dir))
        self._init_model()

    def _init_model(self) -> None:
        try:
            from fastembed import TextEmbedding

            kwargs = {"model_name": self.model_name}
            if self.cache_dir:
                kwargs["cache_dir"] = str(self.cache_dir / "fastembed")
            self._model = TextEmbedding(**kwargs)
            probe = list(self._model.embed(["проверка"]))
            self.dim = len(probe[0])
            self.backend = "fastembed"
            return
        except Exception as exc:  # noqa: BLE001
            self.error = f"fastembed недоступен: {exc}"
            self._model = None

        try:
            from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

            self._chroma_ef = ONNXMiniLM_L6_V2()
            probe = self._chroma_ef(["probe"])
            self.dim = len(probe[0])
            self.backend = "onnx-minilm"
            return
        except Exception as exc:  # noqa: BLE001
            self.error = f"{self.error}; ONNX-фолбэк недоступен: {exc}"
            self._chroma_ef = None

    @property
    def available(self) -> bool:
        return self.backend != "none" and self.dim > 0

    def embed_documents(self, texts: Sequence[str], batch_size: int = 32) -> List[List[float]]:
        if not texts or not self.available:
            return []
        if self.backend == "fastembed" and self._model is not None:
            vectors = list(self._model.embed(list(texts), batch_size=batch_size))
            return [_normalize(list(map(float, vector))) for vector in vectors]
        if self._chroma_ef is not None:
            vectors = self._chroma_ef(list(texts))
            return [_normalize(list(map(float, vector))) for vector in vectors]
        return []

    def embed_query(self, text: str) -> List[float]:
        vectors = self.embed_documents([text])
        return vectors[0] if vectors else []

    def describe(self) -> str:
        if not self.available:
            return f"dense: выключен ({self.error or 'нет модели'})"
        return f"dense: {self.backend} · {self.model_name} · dim={self.dim}"
