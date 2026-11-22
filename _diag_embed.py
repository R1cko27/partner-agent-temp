"""Диагностика: почему индекс собрался без векторов."""
from __future__ import annotations

import sys

from partner.config import Settings
from partner.engine.embeddings import Embedder

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

settings = Settings.load()
print("used_env_file:", settings.used_env_file)
print("use_dense:", settings.use_dense)
print("embed_model:", settings.embed_model)
print("chunk_size/overlap:", settings.chunk_size, settings.chunk_overlap)

embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
print("available:", embedder.available)
print("describe:", getattr(embedder, "describe", lambda: "—")())
print("error:", getattr(embedder, "error", "—"))
