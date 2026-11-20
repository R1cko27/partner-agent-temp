"""Совместимость с ограниченными Windows-песочницами.

В некоторых средах (например, агентская песочница с урезанным токеном) нельзя
записать права доступа на только что созданный каталог: `tempfile.mkdtemp`
делает `chmod(0o700)`, получает «отказано в доступе» и падает. Из-за этого
ломаются pip, huggingface_hub и загрузка моделей эмбеддингов.

Модуль проверяет, работает ли стандартный механизм, и только если нет —
подменяет создание временных путей на безопасный вариант через `os.makedirs`
(каталог наследует права родителя). На обычной машине патч не включается.
"""

from __future__ import annotations

import os
import tempfile
import uuid
from typing import Optional

_APPLIED = False


def _temp_root() -> str:
    return tempfile.gettempdir()


def _safe_mkdtemp(
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
    dir: Optional[str] = None,
) -> str:
    base = dir or _temp_root()
    os.makedirs(base, exist_ok=True)
    for _ in range(50):
        name = f"{prefix or 'tmp'}{uuid.uuid4().hex[:10]}{suffix or ''}"
        path = os.path.join(base, name)
        try:
            os.makedirs(path, exist_ok=False)
            return path
        except FileExistsError:
            continue
    raise FileExistsError(f"не удалось создать временный каталог в {base}")


def _safe_mkstemp(
    suffix: Optional[str] = None,
    prefix: Optional[str] = None,
    dir: Optional[str] = None,
    text: bool = False,
) -> tuple[int, str]:
    base = dir or _temp_root()
    os.makedirs(base, exist_ok=True)
    for _ in range(50):
        name = f"{prefix or 'tmp'}{uuid.uuid4().hex[:10]}{suffix or ''}"
        path = os.path.join(base, name)
        flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | (getattr(os, "O_BINARY", 0) if not text else 0)
        try:
            fd = os.open(path, flags)
            return fd, path
        except FileExistsError:
            continue
    raise FileExistsError(f"не удалось создать временный файл в {base}")


def _probe() -> bool:
    """Проверяет, можно ли писать в каталог, созданный штатным mkdtemp."""
    try:
        path = tempfile.mkdtemp(prefix="probe-")
    except (PermissionError, OSError):
        return False
    try:
        probe_file = os.path.join(path, "probe.txt")
        with open(probe_file, "w", encoding="utf-8") as handle:
            handle.write("ok")
        return True
    except (PermissionError, OSError):
        return False
    finally:
        try:
            for name in os.listdir(path):
                os.remove(os.path.join(path, name))
            os.rmdir(path)
        except OSError:
            pass


def ensure_workable_tempdir() -> bool:
    """Включает совместимый режим, если штатный не работает. Возвращает True при патче."""
    global _APPLIED
    if _APPLIED:
        return True
    if _probe():
        return False

    tempfile.mkdtemp = _safe_mkdtemp  # type: ignore[assignment]
    tempfile.mkstemp = _safe_mkstemp  # type: ignore[assignment]

    _real_chmod = os.chmod

    def _soft_chmod(path, mode, *args, **kwargs):
        try:
            return _real_chmod(path, mode, *args, **kwargs)
        except (PermissionError, OSError):
            return None

    os.chmod = _soft_chmod  # type: ignore[assignment]
    if hasattr(tempfile, "_os"):
        tempfile._os.chmod = _soft_chmod  # type: ignore[attr-defined]

    _APPLIED = True
    return True
