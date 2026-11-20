"""Запись отладочных логов в консоль и в файл в корне проекта.

Каждый вызов `write_log()` печатает строку в stdout (видно в консоли сервера)
и дописывает её в файл `LOG_FILE` (по умолчанию `agent.log` в корне проекта).
Файл не даёт вырасти бесконечно: при превышении лимита он переименовывается
в `agent.log.1` (одна резервная копия).

Запись ошибок файловой системы не роняет запрос к модели — логи это диагностика,
а не критический путь.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Optional

# partner/engine/logbook.py → корень проекта partner-agent
ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOG_NAME = "agent.log"
MAX_BYTES = 5 * 1024 * 1024

_lock = threading.Lock()


def log_path() -> Optional[Path]:
    """Путь к файлу лога из LOG_FILE; пустое значение отключает файл."""
    raw = os.environ.get("LOG_FILE")
    if raw is None:
        raw = DEFAULT_LOG_NAME
    raw = raw.strip()
    if not raw:
        return None
    path = Path(raw).expanduser()
    return path if path.is_absolute() else ROOT / path


def _rotate_if_needed(path: Path) -> None:
    try:
        if path.is_file() and path.stat().st_size >= MAX_BYTES:
            backup = path.with_suffix(path.suffix + ".1")
            if backup.exists():
                backup.unlink()
            path.rename(backup)
    except OSError:
        pass


def write_log(text: str) -> None:
    """Печатает строку в консоль и дописывает в файл лога."""
    try:
        print(text, flush=True)
    except (UnicodeEncodeError, OSError):
        # Консоль с однобайтовой кодировкой не должна ронять сборку индекса.
        pass
    path = log_path()
    if path is None:
        return
    try:
        with _lock:
            path.parent.mkdir(parents=True, exist_ok=True)
            _rotate_if_needed(path)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(text.rstrip("\n") + "\n")
    except OSError:
        pass
