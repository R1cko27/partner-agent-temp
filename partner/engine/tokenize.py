"""Токенизация и лёгкое стемминг-нормализация для ников и запросов.

Ники в датасете содержат латиницу, кириллицу, CJK, тайский и эмодзи, поэтому
токенизатор работает по Unicode-классам, а не по ASCII-регуляркам.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, List

# Пунктуация и символы -> пробел. Сохраняем буквы/цифры любых алфавитов.
_PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_WS_RE = re.compile(r"\s+", re.UNICODE)

# Окончания, которые часто встречаются в русских запросах ("игрока", "серверы").
# Список намеренно короткий: агрессивный стемминг ломает ники вроде "Platin".
_RU_SUFFIXES = (
    "ами", "ями", "ого", "его", "ому", "ему", "ыми", "ими",
    "ах", "ях", "ов", "ев", "ей", "ой", "ый", "ий", "ая", "яя",
    "ое", "ее", "ые", "ие", "ам", "ям", "ом", "ем", "ую", "юю",
    "а", "я", "ы", "и", "у", "ю", "е", "о", "ь",
)

# Частые служебные слова: не помогают ни BM25, ни fuzzy-сопоставлению ников.
STOPWORDS = {
    "и", "в", "во", "на", "не", "что", "как", "кто", "где", "это", "по", "с",
    "со", "из", "за", "для", "от", "до", "или", "а", "но", "же", "ли", "бы",
    "мне", "меня", "мой", "моя", "есть", "был", "была", "были", "быть",
    "покажи", "найди", "скажи", "дай", "список", "все", "всё", "всех",
    "сколько", "какой", "какая", "какие", "каких", "который", "которая",
    "данные", "данных", "информация", "информацию", "про", "о", "об",
    "the", "a", "an", "of", "to", "in", "is", "are", "what", "who", "list",
    "show", "find", "me", "please", "all", "and", "or", "for", "with",
}


def normalize(text: str) -> str:
    """NFKC + casefold: приводит полноширинные символы и регистр к одному виду."""
    if not text:
        return ""
    return unicodedata.normalize("NFKC", text).casefold()


def clean_text(text: str) -> str:
    """Нормализованная строка, где пунктуация заменена пробелами."""
    normalized = normalize(text)
    without_punct = _PUNCT_RE.sub(" ", normalized)
    return _WS_RE.sub(" ", without_punct).strip()


def stem(token: str) -> str:
    """Очень лёгкий стеммер: срезает типичные русские окончания и английское -s."""
    if len(token) < 5:
        return token
    if re.fullmatch(r"[0-9]+", token):
        return token

    for suffix in _RU_SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[: -len(suffix)]

    if token.endswith("s") and not token.endswith("ss") and len(token) >= 4:
        return token[:-1]
    return token


def tokenize(
    text: str,
    *,
    drop_stopwords: bool = False,
    apply_stem: bool = True,
    unique: bool = True,
) -> List[str]:
    """Возвращает токены в порядке появления.

    `unique=False` нужен индексатору: BM25 считает частоты, поэтому повторы
    токенов должны сохраняться.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []
    tokens: List[str] = []
    seen = set()
    for raw in cleaned.split(" "):
        if not raw:
            continue
        if drop_stopwords and raw in STOPWORDS:
            continue
        token = stem(raw) if apply_stem else raw
        if not token:
            continue
        if unique:
            if token in seen:
                continue
            seen.add(token)
        tokens.append(token)
    return tokens


def query_terms(text: str) -> List[str]:
    """Токены запроса: без служебных слов и без стемминга там, где он вреден.

    Стемминг применяем, но сравниваем также с исходной формой — это делает
    поиск ников устойчивым к виду запроса.
    """
    cleaned = clean_text(text)
    if not cleaned:
        return []
    out: List[str] = []
    seen = set()
    for raw in cleaned.split(" "):
        if not raw or raw in STOPWORDS:
            continue
        for candidate in (raw, stem(raw)):
            if candidate and candidate not in seen:
                seen.add(candidate)
                out.append(candidate)
    return out


def dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out
