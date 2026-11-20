"""Определение языка вопроса — простым подсчётом письменностей.

Нужно для двух вещей:

1. ответ и служебные фразы должны быть на языке пользователя, а не всегда на
   русском;
2. кэш ответов не должен отдавать русский ответ на английский вопрос: одни и
   те же вопросы на разных языках близки по эмбеддингам, и без проверки языка
   пользователь получил бы ответ не на своём языке.
"""

from __future__ import annotations

import re

_CYRILLIC_RE = re.compile(r"[\u0400-\u04FF]")
_CJK_RE = re.compile(r"[\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF]")
_LATIN_RE = re.compile(r"[A-Za-z]")

# Короткие служебные фразы на языке пользователя.
FALLBACKS = {
    "ru": "Не удалось сформулировать ответ. Уточните вопрос, пожалуйста.",
    "zh": "暂时无法生成回答，请把问题说得更具体一些。",
    "latin": "Couldn't generate an answer. Please clarify your question.",
}

# Локализованные названия блоков контекста (модель видит их в сообщении).
CONTEXT_HEADERS = {
    "ru": {
        "context": "КОНТЕКСТ (уже загружено из базы — инструменты для этих сущностей не нужны):",
        "summary": "СВОДКА ПО СЕРВЕРАМ И АКТИВНОСТИ:",
        "alias": "Сленг: «{alias}» → {name}",
        "server": "Сервер «{alias}» → {name}" ,
    },
    "zh": {
        "context": "上下文（已从数据库加载，无需为这些实体调用工具）：",
        "summary": "服务器与活跃度汇总：",
        "alias": "俗称：「{alias}」→ {name}",
        "server": "服务器「{alias}」→ {name}",
    },
    "latin": {
        "context": "CONTEXT (already loaded from the database — no tools needed for these entities):",
        "summary": "SERVER AND ACTIVITY SUMMARY:",
        "alias": "Slang: \u00ab{alias}\u00bb → {name}",
        "server": "Server \u00ab{alias}\u00bb → {name}",
    },
}


def detect_lang(text: str) -> str:
    """'ru', 'zh' или 'latin' — по преобладающей письменности."""
    text = text or ""
    cyrillic = len(_CYRILLIC_RE.findall(text))
    cjk = len(_CJK_RE.findall(text))
    latin = len(_LATIN_RE.findall(text))
    if cyrillic and cyrillic >= max(cjk, latin):
        return "ru"
    if cjk and cjk >= latin:
        return "zh"
    if latin:
        return "latin"
    return "ru"


def fallback_text(lang: str) -> str:
    return FALLBACKS.get(lang, FALLBACKS["latin"])


# Прямая директива языка — ставится последней строкой промпта, чтобы
# русскоязычный контекст не перебивал язык вопроса.
LANGUAGE_RULES = {
    "ru": "Отвечай по-русски.",
    "zh": "用中文回答，即使用户的问题涉及俄语名称。",
    "latin": (
        "Answer in English (the user asked in English). "
        "Do not answer in Russian, even though the context below is in Russian."
    ),
}


def language_rule(lang: str) -> str:
    return LANGUAGE_RULES.get(lang, LANGUAGE_RULES["latin"])


def headers(lang: str) -> dict:
    return CONTEXT_HEADERS.get(lang, CONTEXT_HEADERS["latin"])


def sanitize_text(text: str, lang: str = "") -> str:
    """Убирает случайные CJK-вставки из не-китайского ответа.

    Модель иногда вставляет один-два иероглифа в русскую фразу. Если
    пользователь действительно пишет по-китайски, текст не трогаем.
    """
    value = str(text or "")
    if not value or lang == "zh":
        return value
    if not _CJK_RE.search(value):
        return value
    cleaned = _CJK_RE.sub("", value)
    if _CYRILLIC_RE.search(value) or _LATIN_RE.search(value):
        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
        cleaned = re.sub(r"\s+([,.;:!?])", r"\1", cleaned)
    return cleaned
