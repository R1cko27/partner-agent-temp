"""Профиль компании: всё предметное поведение ассистента в одном JSON.

Код не знает ни названия компании, ни требуемой структуры ответа, ни тона.
Всё это лежит в `data/company/agent.json` (или в секции `agent` файла
`profile.json`) и превращается в `AgentProfile`:

* персона и аудитория, тон;
* структура ответа: заголовки, списки, таблицы, длина;
* политика цитат и блок «Источники»;
* фокус и запретные темы;
* fallback и призыв к действию (CTA);
* язык ответа (auto или фиксированный);
* глоссарий терминов;
* лимиты поиска и токенов — «быстро/экономно/глубоко» настраивается без кода;
* список включённых инструментов;
* брендинг интерфейса: заголовок, подзаголовок, примеры, аватар.

Любое поле необязательно: отсутствующие значения берутся из нейтральных
умолчаний, поэтому ассистент работает и без конфига.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_TOOLS = [
    "plan",
    "search_knowledge",
    "company_profile",
    "find_product",
    "find_person",
    "find_faq",
    "kb_stats",
    "offer_followups",
    "ask_clarification",
]

# Как компания называет свои сущности: «продукт» или «решение», «сотрудник»
# или «эксперт». Подписи используются в карточках и в контексте модели.
DEFAULT_LABELS = {
    "company": "Компания",
    "product": "Продукт",
    "person": "Сотрудник",
    "faq": "Вопрос",
    "news": "Новость",
    "sources": "Источники",
}

# Пресеты «быстро / сбалансированно / глубоко»: один ключ вместо набора лимитов.
PRESETS: Dict[str, Dict[str, Any]] = {
    "fast": {
        "retrieval": {"top_k": 4, "context_hits": 2, "excerpt_chars": 350},
        "limits": {"max_tokens": 1000, "fast_max_tokens": 300, "local_max_tokens": 250, "max_steps": 2},
    },
    "balanced": {
        "retrieval": {"top_k": 6, "context_hits": 3, "excerpt_chars": 500},
        "limits": {"max_tokens": 1600, "fast_max_tokens": 400, "local_max_tokens": 300, "max_steps": 3},
    },
    "deep": {
        "retrieval": {"top_k": 8, "context_hits": 4, "excerpt_chars": 700},
        "limits": {"max_tokens": 2200, "fast_max_tokens": 550, "local_max_tokens": 400, "max_steps": 6},
    },
}


def _as_int(value: Any, default: int, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def _as_float(value: Any, default: float, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def _as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on", "да"}
    if value is None:
        return default
    return bool(value)


def _as_list(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return [str(item).strip() for item in value if str(item).strip()]


def _views(value: Any) -> Dict[str, List[str]]:
    """Разбор retrieval.views: {имя режима: [исключённые kind]}."""
    if not isinstance(value, dict):
        return {}
    return {
        str(name): _as_list(kinds)
        for name, kinds in value.items()
        if str(name).strip()
    }


def _view_by_mode(value: Any) -> Dict[str, str]:
    """Разбор retrieval.view_by_mode: {режим ответа: имя режима просмотра}."""
    if not isinstance(value, dict):
        return {}
    result: Dict[str, str] = {}
    for mode, name in value.items():
        mode_key = str(mode).strip().lower()
        name_key = str(name).strip()
        if mode_key and name_key:
            result[mode_key] = name_key
    return result


def _kind_weights(value: Any) -> Dict[str, float]:
    """Разбор retrieval.kind_weights: {тип фрагмента: вес}."""
    if not isinstance(value, dict):
        return {}
    result: Dict[str, float] = {}
    for kind, weight in value.items():
        try:
            number = float(weight)
        except (TypeError, ValueError):
            continue
        if 0.1 <= number <= 3.0:
            result[str(kind)] = number
    return result


@dataclass
class Persona:
    role: str = "ИИ-ассистент компании {company}"
    audience: str = "клиенты и сотрудники компании"
    tone: str = "деловой и доброжелательный, без канцелярита"


@dataclass
class Style:
    heading: bool = True
    max_bullets: int = 3
    allow_tables: bool = True
    max_sentences: int = 2
    observations: int = 0


@dataclass
class Citations:
    required: bool = True
    style: str = "inline"  # inline | section | both | none
    section_title: str = "Источники"


@dataclass
class Topics:
    focus: List[str] = field(default_factory=list)
    avoid: List[str] = field(default_factory=list)


@dataclass
class Retrieval:
    top_k: int = 6
    context_hits: int = 3
    excerpt_chars: int = 500
    # Режимы просмотра базы: имя → типы фрагментов, которые не ищем.
    views: Dict[str, List[str]] = field(default_factory=dict)
    view: str = ""
    view_by_mode: Dict[str, str] = field(default_factory=dict)
    # Чистка выдачи от повторов и бюджет контекста.
    dedupe: bool = True
    max_per_doc: int = 2
    dedupe_threshold: float = 0.75
    context_budget_chars: int = 6000
    # Приоритет типов фрагментов при слиянии каналов поиска.
    kind_weights: Dict[str, float] = field(default_factory=dict)
    # Приоритет самих каналов: bm25, dense, entity.
    channel_weights: Dict[str, float] = field(default_factory=dict)
    # Типы фрагментов второго уровня: подключаются, когда карточек не хватило.
    secondary_kinds: List[str] = field(default_factory=list)


@dataclass
class Limits:
    max_tokens: int = 1600
    fast_max_tokens: int = 400
    local_max_tokens: int = 420
    max_steps: int = 3


@dataclass
class Branding:
    title: str = "Ассистент компании"
    accent: str = ""
    brand: str = "partner agent"
    avatar: str = "AI"
    heading: str = "Чем помочь?"
    subtitle: str = "Спросите о компании, продуктах и условиях работы."
    placeholder: str = "Спросите о компании…"
    examples: List[str] = field(default_factory=list)
    typing_examples: List[str] = field(default_factory=list)


@dataclass
class AgentProfile:
    company_name: str = ""
    persona: Persona = field(default_factory=Persona)
    style: Style = field(default_factory=Style)
    citations: Citations = field(default_factory=Citations)
    rules: List[str] = field(default_factory=list)
    context: List[str] = field(default_factory=list)
    topics: Topics = field(default_factory=Topics)
    labels: Dict[str, str] = field(default_factory=lambda: dict(DEFAULT_LABELS))
    fallback: str = (
        "В материалах компании этого нет. Уточните вопрос или запросите данные "
        "у представителя компании."
    )
    cta: Dict[str, str] = field(default_factory=dict)
    language: str = "auto"
    glossary: Dict[str, str] = field(default_factory=dict)
    retrieval: Retrieval = field(default_factory=Retrieval)
    limits: Limits = field(default_factory=Limits)
    modes: Dict[str, str] = field(default_factory=dict)
    tools: List[str] = field(default_factory=lambda: list(DEFAULT_TOOLS))
    branding: Branding = field(default_factory=Branding)
    preset: str = "balanced"

    # --- публичная часть для интерфейса ---------------------------------
    def to_public(self) -> Dict[str, Any]:
        return {
            "company": self.company_name,
            "language": self.language,
            "citations": self.citations.required,
            "modes": {"default": self.modes.get("default", "thinking")},
            "branding": {
                "title": self.branding.title,
                "brand": self.branding.brand,
                "avatar": self.branding.avatar,
                "heading": self.branding.heading,
                "subtitle": self.branding.subtitle,
                "placeholder": self.branding.placeholder,
                "examples": self.branding.examples,
                "typing_examples": self.branding.typing_examples,
                "accent": self.branding.accent,
            },
        }


def _merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in (overlay or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def load_agent_config(data_dir: Path) -> Dict[str, Any]:
    """Секция `agent` из profile.json + agent.json (второй приоритетнее)."""
    data_dir = Path(data_dir)
    config: Dict[str, Any] = {}

    profile_path = data_dir / "company" / "profile.json"
    if profile_path.is_file():
        try:
            payload = json.loads(profile_path.read_text(encoding="utf-8-sig"))
            if isinstance(payload, dict) and isinstance(payload.get("agent"), dict):
                config = _merge(config, payload["agent"])
        except (OSError, json.JSONDecodeError):
            pass

    agent_path = data_dir / "company" / "agent.json"
    if agent_path.is_file():
        try:
            payload = json.loads(agent_path.read_text(encoding="utf-8-sig"))
            if isinstance(payload, dict):
                config = _merge(config, payload)
        except (OSError, json.JSONDecodeError):
            pass

    return config


def _profile_name(data_dir: Path) -> str:
    """Название компании из profile.json (если в agent.json его нет)."""
    path = Path(data_dir) / "company" / "profile.json"
    if not path.is_file():
        return ""
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return ""
    if not isinstance(payload, dict):
        return ""
    return str(payload.get("name") or payload.get("company") or "").strip()


def build_profile(
    data_dir: Path,
    company_name: str = "",
    limits: Optional[Dict[str, Any]] = None,
) -> AgentProfile:
    """Читает конфиг и собирает профиль; отсутствующие поля — умолчания."""
    config = load_agent_config(data_dir)
    merged_limits = _merge(limits or {}, config.get("limits") or {})

    persona_raw = config.get("persona") or {}
    style_raw = config.get("style") or {}
    citations_raw = config.get("citations") or {}
    topics_raw = config.get("topics") or {}
    retrieval_raw = config.get("retrieval") or {}
    branding_raw = config.get("branding") or {}
    modes_raw = config.get("modes") or {}
    tools_raw = config.get("tools")

    name = str(config.get("company") or company_name or _profile_name(data_dir) or "").strip()

    profile = AgentProfile(
        company_name=name,
        persona=Persona(
            role=str(persona_raw.get("role") or Persona.role),
            audience=str(persona_raw.get("audience") or Persona.audience),
            tone=str(persona_raw.get("tone") or Persona.tone),
        ),
        style=Style(
            heading=_as_bool(style_raw.get("heading"), True),
            max_bullets=_as_int(style_raw.get("max_bullets"), 6, 2, 12),
            allow_tables=_as_bool(style_raw.get("allow_tables"), True),
            max_sentences=_as_int(style_raw.get("max_sentences"), 4, 1, 10),
            observations=_as_int(style_raw.get("observations"), 2, 0, 5),
        ),
        citations=Citations(
            required=_as_bool(citations_raw.get("required"), True),
            style=str(citations_raw.get("style") or "inline").lower(),
            section_title=str(citations_raw.get("section_title") or "Источники"),
        ),
        rules=_as_list(config.get("rules")),
        context=_as_list(config.get("context")),
        topics=Topics(
            focus=_as_list(topics_raw.get("focus")),
            avoid=_as_list(topics_raw.get("avoid")),
        ),
        fallback=str(config.get("fallback") or AgentProfile.fallback),
        cta={
            str(key): str(value)
            for key, value in (config.get("cta") or {}).items()
            if str(value).strip()
        },
        language=str(config.get("language") or "auto").lower(),
        glossary={
            str(key): str(value)
            for key, value in (config.get("glossary") or {}).items()
            if str(value).strip()
        },
        retrieval=Retrieval(
            top_k=_as_int(retrieval_raw.get("top_k"), 6, 2, 12),
            context_hits=_as_int(retrieval_raw.get("context_hits"), 3, 1, 6),
            excerpt_chars=_as_int(retrieval_raw.get("excerpt_chars"), 500, 200, 1200),
            views=_views(retrieval_raw.get("views")),
            view=str(retrieval_raw.get("view") or ""),
            view_by_mode=_view_by_mode(retrieval_raw.get("view_by_mode")),
            dedupe=_as_bool(retrieval_raw.get("dedupe"), True),
            max_per_doc=_as_int(retrieval_raw.get("max_per_doc"), 2, 1, 5),
            dedupe_threshold=_as_float(retrieval_raw.get("dedupe_threshold"), 0.75, 0.3, 0.99),
            context_budget_chars=_as_int(
                retrieval_raw.get("context_budget_chars"), 6000, 1000, 20000
            ),
            kind_weights=_kind_weights(retrieval_raw.get("kind_weights")),
            channel_weights=_kind_weights(retrieval_raw.get("channel_weights")),
            secondary_kinds=_as_list(retrieval_raw.get("secondary_kinds")),
        ),
        limits=Limits(
            max_tokens=_as_int(merged_limits.get("max_tokens"), 2500, 300, 8000),
            fast_max_tokens=_as_int(merged_limits.get("fast_max_tokens"), 600, 150, 2000),
            local_max_tokens=_as_int(merged_limits.get("local_max_tokens"), 420, 120, 1200),
            max_steps=_as_int(merged_limits.get("max_steps"), 5, 2, 10),
        ),
        modes={
            "default": str(modes_raw.get("default") or "thinking").lower(),
        },
        tools=([tool for tool in _as_list(tools_raw) if tool in DEFAULT_TOOLS]
               if tools_raw is not None else list(DEFAULT_TOOLS)),
        branding=Branding(
            title=str(branding_raw.get("title") or Branding.title),
            brand=str(branding_raw.get("brand") or Branding.brand),
            avatar=str(branding_raw.get("avatar") or Branding.avatar)[:3],
            heading=str(branding_raw.get("heading") or Branding.heading),
            subtitle=str(branding_raw.get("subtitle") or Branding.subtitle),
            placeholder=str(branding_raw.get("placeholder") or Branding.placeholder),
            examples=_as_list(branding_raw.get("examples"))[:6],
            typing_examples=_as_list(branding_raw.get("typing_examples"))[:20],
            accent=str(branding_raw.get("accent") or ""),
        ),
    )

    profile.persona.role = profile.persona.role.replace("{company}", name or "компании")
    if not profile.branding.title or profile.branding.title == Branding.title:
        profile.branding.title = f"Ассистент {name}" if name else profile.branding.title
    return profile
