"""Конфигурация Partner-Agent: пути, .env и настройки модели."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("PARTNER_DATA_DIR", ROOT / "data"))
STORAGE_DIR = Path(os.environ.get("PARTNER_STORAGE_DIR", ROOT / "storage"))
WEB_DIR = ROOT / "partner" / "web"

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-flash"
DEFAULT_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_TRUE = {"1", "true", "yes", "on", "y", "да"}
_FALSE = {"0", "false", "no", "off", "n", "нет"}


def load_dotenv(path: Path = ROOT / ".env") -> Dict[str, str]:
    """Загружает .env. Переменные окружения приоритетнее файла."""
    values: Dict[str, str] = {}
    if not path.is_file():
        return values

    try:
        from dotenv import dotenv_values  # type: ignore

        for key, value in dotenv_values(path).items():
            if value is not None:
                values[key] = value
    except Exception:  # pragma: no cover - fallback без python-dotenv
        try:
            text = path.read_text(encoding="utf-8-sig")
        except OSError:
            return values
        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key.startswith("export "):
                key = key[len("export "):].strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            values[key] = value

    for key, value in values.items():
        os.environ.setdefault(key, value)
    return values


def _get(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


def _get_int(name: str, default: int) -> int:
    try:
        return int(_get(name, str(default)))
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    try:
        return float(_get(name, str(default)))
    except ValueError:
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    raw = _get(name)
    if not raw:
        return default
    lowered = raw.lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    return default


@dataclass
class Settings:
    company_name: str = "Компания-партнёр"
    api_key: str = ""
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    provider: str = "deepseek"
    ollama_base_url: str = "http://127.0.0.1:11434/v1"
    ollama_model: str = "qwen2.5:3b-instruct"
    temperature: float = 0.2
    max_tokens: int = 1400
    fast_max_tokens: int = 350
    local_max_tokens: int = 300
    thinking: bool = True
    log_prompts: bool = False
    log_tokens: bool = False
    auto_context: bool = True
    top_k: int = 6
    max_steps: int = 3
    host: str = "127.0.0.1"
    port: int = 8001

    data_dir: Path = DATA_DIR
    storage_dir: Path = STORAGE_DIR
    embed_model: str = DEFAULT_EMBED_MODEL
    use_dense: bool = True
    chunk_size: int = 900
    chunk_overlap: int = 120

    answer_cache: bool = True
    answer_cache_threshold: float = 0.93
    answer_cache_ttl_days: int = 7
    answer_cache_max_entries: int = 500

    used_env_file: bool = field(default=False, repr=False)

    @classmethod
    def load(cls, env_file: Optional[Path] = None, use_dotenv: bool = True) -> "Settings":
        env_file = env_file or (ROOT / ".env")
        used = False
        if use_dotenv:
            used = env_file.is_file() and bool(load_dotenv(env_file))

        return cls(
            company_name=_get("PARTNER_COMPANY", "Компания-партнёр"),
            api_key=_get("DEEPSEEK_API_KEY"),
            base_url=_get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            model=_get("DEEPSEEK_MODEL", DEFAULT_MODEL),
            provider=(_get("LLM_PROVIDER", "deepseek").strip().lower() or "deepseek"),
            ollama_base_url=_get(
                "OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1"
            ).rstrip("/"),
            ollama_model=_get("OLLAMA_MODEL", "qwen2.5:3b-instruct"),
            temperature=_get_float("LLM_TEMPERATURE", 0.2),
            max_tokens=_get_int("LLM_MAX_TOKENS", 3000),
            fast_max_tokens=max(200, _get_int("FAST_MAX_TOKENS", 700)),
            local_max_tokens=max(150, _get_int("LOCAL_MAX_TOKENS", 450)),
            thinking=_get_bool("DEEPSEEK_THINKING", True),
            log_prompts=_get_bool("LOG_PROMPTS", True),
            log_tokens=_get_bool("LOG_TOKENS", True),
            auto_context=_get_bool("AUTO_CONTEXT", True),
            top_k=max(1, _get_int("RAG_TOP_K", 6)),
            max_steps=max(2, _get_int("AGENT_MAX_STEPS", 6)),
            host=_get("APP_HOST", "127.0.0.1"),
            port=_get_int("APP_PORT", 8001),
            data_dir=Path(_get("PARTNER_DATA_DIR", str(DATA_DIR))),
            storage_dir=Path(_get("PARTNER_STORAGE_DIR", str(STORAGE_DIR))),
            embed_model=_get("EMBED_MODEL", DEFAULT_EMBED_MODEL),
            use_dense=_get_bool("RAG_USE_DENSE", True),
            chunk_size=max(200, _get_int("RAG_CHUNK_SIZE", 900)),
            chunk_overlap=max(0, _get_int("RAG_CHUNK_OVERLAP", 120)),
            answer_cache=_get_bool("ANSWER_CACHE", True),
            answer_cache_threshold=min(
                0.99, max(0.5, _get_float("ANSWER_CACHE_THRESHOLD", 0.93))
            ),
            answer_cache_ttl_days=max(0, _get_int("ANSWER_CACHE_TTL_DAYS", 7)),
            answer_cache_max_entries=max(10, _get_int("ANSWER_CACHE_MAX_ENTRIES", 500)),
            used_env_file=used,
        )

    # --- производные пути и режимы --------------------------------------
    @property
    def has_api_key(self) -> bool:
        return bool(self.api_key)

    @property
    def is_local(self) -> bool:
        return self.provider in ("ollama", "local")

    @property
    def effective_model(self) -> str:
        return self.ollama_model if self.is_local else self.model

    @property
    def effective_base_url(self) -> str:
        return self.ollama_base_url if self.is_local else self.base_url

    @property
    def llm_ready(self) -> bool:
        return self.is_local or self.has_api_key

    @property
    def index_dir(self) -> Path:
        return self.storage_dir / "index"

    @property
    def chroma_dir(self) -> Path:
        return self.storage_dir / "chroma"

    @property
    def db_path(self) -> Path:
        return self.storage_dir / "chat.db"

    @property
    def sources_file(self) -> Path:
        return self.data_dir / "company" / "urls.txt"

    @property
    def profile_file(self) -> Path:
        return self.data_dir / "company" / "profile.json"


DATA_STAMP_PATHS = ("company", "company/profile.json", "company/urls.txt")


def data_stamp(data_dir: Path) -> str:
    """Отпечаток актуальности материалов: кэш ответов не переживает обновление."""
    newest = 0.0
    for relative in DATA_STAMP_PATHS:
        path = Path(data_dir) / relative
        try:
            newest = max(newest, path.stat().st_mtime)
        except OSError:
            continue
    return str(int(newest))
