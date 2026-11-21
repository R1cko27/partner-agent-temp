"""Кеш векторов фрагментов: чтобы не пересчитывать эмбеддинги заново.

Каждая запись — «id фрагмента → (хеш текста, вектор)». При сборке вектор
переиспользуется, если id и хеш текста совпали: значит фрагмент не изменился.

Ключ кеша (stamp) включает модель эмбеддингов и параметры нарезки. Если они
поменялись, кеш считается невалидным целиком: смешивать векторы разных моделей
нельзя — поиск начнёт выдавать правдоподобный, но неверный результат.

Хранится рядом с индексом:
  vectors.npz        — ids, hashes, vectors (float32)
  vectors.meta.json  — версия, stamp, размерность, число записей
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = 1


class VectorCache:
    def __init__(self, path: Path, stamp: str) -> None:
        self.path = Path(path)
        self.stamp = stamp
        self._items: Dict[str, Tuple[str, Any]] = {}
        self._dirty = False

    # --- загрузка и сохранение -------------------------------------------
    @classmethod
    def load(cls, path: Path, stamp: str) -> "VectorCache":
        cache = cls(path, stamp)
        meta_path = cache.path / "vectors.meta.json"
        data_path = cache.path / "vectors.npz"
        if not (meta_path.is_file() and data_path.is_file()):
            return cache
        try:
            import numpy as np

            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if meta.get("version") != VERSION or meta.get("stamp") != stamp:
                return cache
            payload = np.load(data_path, allow_pickle=False)
            ids = payload["ids"]
            hashes = payload["hashes"]
            vectors = payload["vectors"]
            for index in range(len(ids)):
                cache._items[str(ids[index])] = (str(hashes[index]), vectors[index])
        except Exception:  # noqa: BLE001 - битый кеш просто игнорируем
            cache._items = {}
        return cache

    def save(self) -> bool:
        if not self._items:
            return False
        try:
            import numpy as np

            ids = list(self._items.keys())
            hashes = [self._items[key][0] for key in ids]
            vectors = np.asarray([self._items[key][1] for key in ids], dtype="float32")
            self.path.mkdir(parents=True, exist_ok=True)
            # Пишем во временный файл и подменяем атомарно: оборванная сборка
            # не должна оставить повреждённый vectors.npz — теперь это
            # единственное хранилище плотных векторов.
            target = self.path / "vectors.npz"
            temp = self.path / "vectors.tmp.npz"
            np.savez_compressed(
                temp,
                ids=np.array(ids, dtype="U"),
                hashes=np.array(hashes, dtype="U64"),
                vectors=vectors,
            )
            os.replace(temp, target)
            meta = {
                "version": VERSION,
                "stamp": self.stamp,
                "dim": int(vectors.shape[1]) if vectors.ndim == 2 else 0,
                "count": len(ids),
                "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            (self.path / "vectors.meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            self._dirty = False
            return True
        except Exception:  # noqa: BLE001 - кеш не должен ломать сборку
            return False

    # --- доступ -----------------------------------------------------------
    def get(self, chunk_id: str, text_hash: str) -> Optional[Any]:
        item = self._items.get(chunk_id)
        if item is None:
            return None
        if item[0] != text_hash:
            return None
        return item[1]

    def put(self, chunk_id: str, text_hash: str, vector: Any) -> None:
        self._items[chunk_id] = (text_hash, vector)
        self._dirty = True

    def keep_only(self, ids: Iterable[str]) -> int:
        """Убирает из кеша записи, которых больше нет в базе."""
        allowed = set(ids)
        stale = [key for key in self._items if key not in allowed]
        for key in stale:
            del self._items[key]
            self._dirty = True
        return len(stale)

    def __len__(self) -> int:
        return len(self._items)
