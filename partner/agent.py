"""Агент Partner-Agent: поиск по базе знаний компании и ответ со ссылками."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence

from .domain.retriever import Retriever, SearchHit  
from .engine.answers import AnswerCache
from .engine.complexity import heuristic_mode, parse_mode
from .engine.lang import detect_lang, fallback_text, sanitize_text
from .engine.llm import DeepSeekClient, LLMError, ToolCall
from .engine.judge import Judge, context_warning
from .engine.logbook import write_log
from .engine.tokenize import query_terms
from .followups import FollowupPlanner
from .config import Settings
from .domain.agent_profile import AgentProfile, build_profile
from .prompts import build_fast_prompt, build_system_prompt, tools_for

MAX_HISTORY_MESSAGES = 12


def _clip(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "…"
    

def _compact(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Убирает пустые поля — экономит токены в ответах инструментов."""
    return {
        key: value
        for key, value in payload.items()
        if value not in (None, "", [], {}, 0)
    }


def _url_host(value: str) -> str:
    """Хост публичного источника: для клиентского режима вместо пути к файлу."""
    text = (value or "").strip()
    if not text.startswith(("http://", "https://")):
        return ""
    return text.split("//", 1)[-1].split("/", 1)[0]


# Как пользователи называют продукты: запрос расширяем каноническим именем.
_ALIASES = {
    "мэ": "NGFW",
    "межсетевой экран": "NGFW",
    "веб-экран": "WAF",
    "веб экран": "WAF",
    "файрвол": "NGFW",
    "фаервол": "NGFW",
    "тг": "Telegram",
    "телеграм": "Telegram",
    "телега": "Telegram",
    "вк": "VK",
    "вконтакте": "VK",
    "хабр": "Habr",
    "коллектор": "log-collector",
    "ugmc": "Management Center",
    "центральная консоль": "Management Center",
}

# Какие карточки отвечают на перечисления: городá, платформы, курсы, продукты.
_TOPIC_SOURCES = (
    (("кластер", "отказоустойчив", "vrrp"), ("products/dcfw", "klasterizaciya")),
    (("лицензи", "ugmc", "management center", "управлен"), ("products/management-center", "products/dcfw", "licenzirovanie")),
    (("журнал", "syslog", "лог"), ("products/log-analyzer", "syslog")),
    (("сертификат", "фстэк", "реестр"), ("faq/certification", "registry-entry")),
    (("экзамен", "курс", "обучен", "академ"), ("faq/education", "products/waf", "ekzamen", "academy")),
    (("ldap", "коннектор", "сопоставл"), ("products/log-analyzer", "pol6zovateli")),
    (("платформ", "аппаратн", "модел"), ("docs/versions-and-platforms", "docs/hardware")),
    (("механизм", "аутентификац", "авторизац"), ("products/dcfw", "glossar")),
    (("численност", "сотрудник", "клиент", "проект", "масштаб"), ("about/company",)),
    (("trap", "snmp", "мониторинг"), ("products/dcfw", "funkcional6nye")),
    (("основан", "год", "истори", "2006"), ("about/history",)),
    (("node-sync", "delivery-mode", "vrid", "кластер"), ("products/dcfw",)),
    (("экзамен", "курс", "академи", "ug.", "стоимость обучения"),
     ("about/usergate_academy_prices", "about/academy", "faq/education")),
    (("адрес", "телефон", "офис", "контакт"), ("about/contacts", "faq/contacts")),
    (("lacp", "агрегир", "бонд", "канал"), ("products/ngfw", "products/swg")),
    (("x10", "характеристик", "пропускн", "температур", "портов", "din", "ip30"),
     ("docs/hardware", "products/usergate-x10")),
)

_LIST_HINTS = (
    (("город", "офис", "адрес"), ("about/contacts",)),
    (("платформ", "аппаратн", "модел"), ("docs/versions-and-platforms",)),
    (("курс", "обучен", "академ", "экзамен"), ("faq/education",)),
    (("фгос", "вуз", "колледж", "подготовк"), ("vuzah", "faq/education")),
    (("продукт", "экосистем", "summa", "линейк"), ("faq/products", "about/ecosystem")),
)

_INJECTION_RE = re.compile(
    r"(игнорируй|игнорировать|отмени|отменить|выведи\s+(свой\s+)?(системн|промпт|инструкц)"
    r"|ты\s+теперь|представь,?\s+что\s+ты|покажи\s+(историю|чуж)|base64|расшифруй\s+и\s+выполни)",
    re.I,
)


def _asks_certificate(question: str) -> bool:
    """Вопрос про сертификат конкретного продукта."""
    text = (question or "").lower()
    return "сертификат" in text and any(
        word in text for word in ("waf", "siem", "client", "dcfw", "swg", "ngfw")
    )


def _looks_like_injection(question: str) -> bool:
    """Попытка сменить правила: поиск по базе такому запросу не нужен."""
    return bool(_INJECTION_RE.search(question or ""))


def _sanitize_excerpt(text: str) -> str:
    """Убирает из выдержки строки-повеления: материал — это данные, не инструкции."""
    cleaned = []
    for line in (text or "").splitlines():
        if re.search(r"(?i)(игнорируй|отмени|выполни|обязан|инструкция для|system:|assistant:)", line):
            cleaned.append("…")
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


# Новости и телеграм полезны только для «что нового / когда вышло».
# Для остальных вопросов документация и карточки точнее.
_NEWS_MARKERS = (
    "новост", "анонс", "что нового", "когда выш", "вышел", "вышла", "выпуст", "дата выхода",
    "релиз", "обновлен", "пресс-релиз", "вебинар", "мероприят",
    "конференц", "премия", "итоги года",
)

# Вопросы-перечисления: «какие типы», «перечисли», «список». Для них ответ
# должен называть все элементы из материалов, а не один пример.
_ENUM_RE = re.compile(
    r"(какие|каких|перечисли|назови|список|все)\b[^?.]{0,40}?"
    r"(тип|верси|продукт|город|офис|модел|услуг|возможност|компонент|этап|платформ)\w*",
    re.I,
)
_ENUM_BLOCKLIST = {
    "это", "эти", "все", "всё", "его", "их", "она", "они", "оно",
    "такие", "такой", "также", "например", "которые", "который",
}
_ENUM_MARKERS = ("перечисли", "список", "все виды", "какие ещё", "назови")


def _is_enumeration(question: str) -> bool:
    text = (question or "").lower()
    return any(marker in text for marker in _ENUM_MARKERS) or bool(_ENUM_RE.search(text))


def _list_items_from(text: str, limit: int = 12) -> List[str]:
    """Элементы списка из фрагмента: строки таблицы и хвосты после двоеточия.

    Нужно для перечислений: модели отдаём готовый перечень, а не «в материалах
    что-то перечислено», иначе она называет один-два пункта.
    """
    items: List[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        clean = value.strip(" .;:—-«»\"'|")
        if not clean or len(clean) < 2 or len(clean) > 60:
            return
        if clean.lower() in seen or clean.lower() in {"город", "адрес", "индекс", "платформа"}:
            return
        seen.add(clean.lower())
        items.append(clean)

    for line in (text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith("|") and stripped.count("|") >= 2:
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if cells and not set(cells[0]) <= set("-: "):
                add(cells[0])
        elif ":" in stripped:
            tail = stripped.split(":", 1)[1]
            for part in tail.split(";"):
                add(part)
    for item in _enumeration_items(text):
        add(item)
    return items[:limit]


def _enumeration_items(text: str) -> List[str]:
    """Элементы перечисления из фрагмента: хвост после двоеточия, делённый по ; и ,"""
    items: List[str] = []
    for sentence in re.split(r"(?<=[.!?])\s+", text or ""):
        if ":" not in sentence:
            continue
        tail = sentence.split(":", 1)[1]
        for part in re.split(r";|\s+и\s+|,\s+", tail):
            clean = part.strip(" .;:—-«»\"'")
            clean = re.sub(r"^и\s+", "", clean)
            words = clean.split()
            if not clean or not (1 <= len(words) <= 6) or len(clean) < 5:
                continue
            # Описательные придатки («позволяющий задать настройки») — не элемент списка.
            if re.match(
                r"(позволя|обеспечива|предназнач|котор|что|чтобы|при|для|если)", clean, re.I
            ):
                continue
            # Служебные слова — не элемент перечисления.
            if clean.lower() in _ENUM_BLOCKLIST:
                continue
            if all(word.lower() in _ENUM_BLOCKLIST for word in words):
                continue
            if "http" in clean or clean.isdigit():
                continue
            items.append(clean)
    return items


# Маркеры определения: помогают отличить описание функции от списка событий.
_DEFINITION_CUES = ("это ", "позволяет", "используется", "предназначен", "представляет")


def _definition_score(text: str, token: str) -> int:
    """Насколько фрагмент похож на определение термина, а не на список событий.

    Определение начинается с термина и объясняет его («UserID — функциональность,
    благодаря которой…»). В справочниках событий термин встречается десятки раз
    внутри перечислений, и без штрафа они выигрывают.
    """
    low = text.lower()
    position = low.find(token)
    if position < 0:
        return -1
    score = 2 if position < 300 else 0
    window = low[max(0, position - 80): position + 400]
    score += sum(1 for cue in _DEFINITION_CUES if cue in window)
    if low.count(token) > 6:
        score -= 3
    return score

# Отсылка к документации без ссылки рядом: «описано в документации».
_DOC_REF_RE = re.compile(
    r"(в документации|в документацию|на портале документации|в руководстве"
    r"|описано в документации|описан в документации|см\.\s*документац"
    r"|подробнее в документации|по документации)",
    re.I,
)

DOMAIN_ONLY_RE = re.compile(
    r"(?<!//)\b(?:[a-z0-9-]+\.)*(?:usergate\.com|usergate\.ru)/[^\s)\]>»«\"',;]*"
)
CODE_GUARD_RE = re.compile(r"\bUG\.[A-Za-z0-9._]{2,}")
PRICE_GUARD_RE = re.compile(r"\b\d[\d\s]{2,}\s?₽")


ANSWER_URL_RE = re.compile(r"https?://[^\s)\]>»«\"']+")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")


def _norm_url(value: str) -> str:
    return (value or "").strip().rstrip("/.,;:»\"'").lower()


def _sentence_around(text: str, start: int, end: int, limit: int = 400) -> str:
    """Предложение вокруг ссылки — для проверки, о чём оно."""
    left = max(0, start - limit)
    right = min(len(text), end + limit)
    window = text[left:right]
    offsets = [window.rfind(mark, 0, start - left) for mark in (".", "\n", "!", "?")]
    begin = max(offsets) + 1 if max(offsets) >= 0 else 0
    ends = [pos for pos in (window.find(mark, end - left) for mark in (".", "\n", "!", "?")) if pos >= 0]
    stop = min(ends) + 1 if ends else len(window)
    return window[begin:stop]


def _clean_followups(values: Any, limit: int = 8) -> List[str]:
    """Аккуратные кнопки-продолжения: без пустых, дублей и простыней."""
    if isinstance(values, str):
        values = [values]
    items: List[str] = []
    seen = set()
    for value in values or []:
        text = " ".join(str(value).split()).strip(" -—•")
        if not text or len(text) > 90:
            continue
        if text[-1] not in "?？":
            text += "?"
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(text)
    return items[:limit]


def _clean_options(values: Any, limit: int = 3) -> List[str]:
    if isinstance(values, str):
        values = [values]
    items: List[str] = []
    seen = set()
    for value in values or []:
        text = " ".join(str(value).split()).strip(" -—•")
        if not text or len(text) > 80:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(text)
        if len(items) >= limit:
            break
    return items


def _clean_clarification_item(item: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(item, dict):
        return None
    question = " ".join(str(item.get("question") or "").split()).strip()
    options = _clean_options(item.get("options"))
    if not question or len(question) > 220 or len(options) < 2:
        return None
    placeholder = " ".join(str(item.get("placeholder") or "").split()).strip()
    return {
        "question": question,
        "options": options[:3],
        "placeholder": placeholder[:80] or "Свой вариант",
    }


def _clean_clarification(args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(args, dict):
        return None
    questions: List[Dict[str, Any]] = []
    raw = args.get("questions")
    if isinstance(raw, list):
        for item in raw[:10]:
            cleaned = _clean_clarification_item(item)
            if cleaned:
                questions.append(cleaned)
    # Обратная совместимость со старым форматом одного вопроса.
    if not questions:
        legacy = _clean_clarification_item(args)
        if legacy:
            questions.append(legacy)
    if not questions:
        return None
    intro = " ".join(str(args.get("intro") or "").split()).strip()[:240]
    summary = intro or "Уточнение: " + " · ".join(
        item["question"] for item in questions
    )
    first = questions[0]
    return {
        "questions": questions,
        "intro": intro,
        "summary": summary,
        "allow_custom": True,
        "question": first["question"],
        "options": first["options"],
        "placeholder": first["placeholder"],
    }


def _followups_from_calls(calls: Any) -> List[str]:
    for call in calls or []:
        if not isinstance(call, dict) or call.get("name") != "offer_followups":
            continue
        args = call.get("arguments") or {}
        if isinstance(args, dict):
            return _clean_followups(args.get("items"))
    return []


_SOURCE_FILE_RE = re.compile(r"`[^`\n]+\.(?:md|txt|pdf|docx|html?|json)`", re.I)
_SOURCE_CODE_RE = re.compile(r"\s*`[^`\n]+`")
_SOURCE_PAREN_WORDS_RE = re.compile(
    r"\s*\([^()\n]*(?:FAQ|faq|источник|материал|баз[аеы]|документ|файл|раздел|карточк)"
    r"[^()\n]*\)",
    re.I,
)
_SOURCE_PAREN_CODE_RE = re.compile(r"\s*\([^()\n]*`[^`\n]+`[^()\n]*\)")
_SOURCE_PAREN_RE = re.compile(
    r"\s*\((?:[^()\n]*?\.(?:md|txt|pdf|docx|html?|json))\)", re.I
)
_SOURCE_LINE_RE = re.compile(r"(?im)^\s*Источник(?:и)?\s*:.*(?:\n|$)")


_CLIENT_PHRASES = [
    (re.compile(r"(?i)\bпо материалам компании\b"), "по нашим данным"),
    (re.compile(r"(?i)\bпо материалам\b"), "по нашим данным"),
    (re.compile(r"(?i)\bв материалах\b"), ""),
    (re.compile(r"(?i)\bв документах\b"), ""),
    (re.compile(r"(?i)\bв источниках\b"), ""),
    (re.compile(r"(?i)\bиз материалов\b"), "из наших данных"),
    (re.compile(r"(?i)\bматериалами\b"), ""),
    (re.compile(r"(?i)\bматериалы\b"), ""),
    (re.compile(r"(?i)\bматериалов\b"), ""),
    (re.compile(r"(?i)\bматериале\b"), ""),
    (re.compile(r"(?i)\bматериал\b"), ""),
    (re.compile(r"(?i)\bв материалах компании\b"), "у нас"),
    (re.compile(r"(?i)\bв базе(?: знаний)?\b"), ""),
    (re.compile(r"(?i)\bпо данным базы\b"), "по нашим данным"),
    (re.compile(r"(?i)\bв выгрузке\b"), "в данных"),
    (re.compile(r"(?i)\bиз материалов компании\b"), "из наших данных"),
]


def _strip_source_keys(value: Any) -> Any:
    """Убирает из данных инструмента поля source/sources в клиентском режиме."""
    if isinstance(value, dict):
        drop = {"source", "sources", "source_path", "file"}
        if "text" in value:  # фрагмент поиска: убираем и его заголовок
            drop |= {"title", "kind", "id"}
        return {
            key: _strip_source_keys(item)
            for key, item in value.items()
            if key not in drop
        }
    if isinstance(value, list):
        return [_strip_source_keys(item) for item in value]
    return value


_TABLE_SEP_RE = re.compile(r"^\|?[\s:|-]+\|?$")


_INLINE_SEP_RE = re.compile(r"(?:\|\s*:?-{2,}:?\s*)+\|")


_HEADER_TAIL_RE = re.compile(r"^(.*?)(\|\s*[^|\n]{2,60}\|\s*[^|\n]{2,60}\|)\s*$")


def _repair_ragged_tables(text: str) -> str:
    """Чинит таблицы, у которых нет строки-разделителя.

    Модель иногда заканчивает абзац заголовком «| a | b |» и печатает строки
    через «||», без «|---|». Собираем из этого нормальную таблицу.
    """
    if "||" not in text and "|---" not in text:
        return text

    prepared: List[str] = []
    for line in (text or "").split("\n"):
        if "||" in line:
            line = re.sub(r"\s*\|\|\s*", " |\n| ", line)

        parts = line.split("\n")
        for index, part in enumerate(parts):
            match = _HEADER_TAIL_RE.match(part) if part.count("|") >= 3 and "---" not in part else None
            if match and match.group(1).strip():
                cells = [cell for cell in match.group(2).split("|") if cell.strip()]
                prepared.append(match.group(1).strip())
                prepared.append("| " + " | ".join(cell.strip() for cell in cells) + " |")
                prepared.append("|" + "|".join(["---"] * len(cells)) + "|")
                continue
            if part.startswith("| "):
                if not part.rstrip().endswith("|"):
                    part = part.rstrip() + " |"
            prepared.append(part)
    return "\n".join(prepared)


def _split_inline_table(text: str) -> str:
    """Модель иногда печатает таблицу одной строкой: «| a | b | |---| | 1 | 2 |».

    Находим разделитель, по нему определяем число колонок, а всё остальное
    раскладываем на строки.
    """
    out: List[str] = []
    for line in (text or "").split("\n"):
        match = _INLINE_SEP_RE.search(line)
        if not match or line.count("|") < 4:
            out.append(line)
            continue
        prefix = line[: match.start()].strip()
        separator = match.group(0)
        body = line[match.end():].strip()
        columns = separator.count("---")
        if columns < 2:
            out.append(line)
            continue
        header_cells = [cell.strip() for cell in prefix.rstrip("|").split("|")]
        header = header_cells[-columns:]
        if len(header) < columns:
            out.append(line)
            continue
        before = prefix.rstrip("|").split("|")[: len(header_cells) - columns]
        if before and " ".join(before).strip(" |"):
            out.append(" ".join(part.strip() for part in before if part.strip()))
        out.append("| " + " | ".join(header) + " |")
        out.append("|" + "|".join(["---"] * columns) + "|")
        chunks = re.split(r"\|\s*\|", body.strip("|"))
        # если в строках больше ячеек, чем в разделителе, таблица шире:
        # заголовок дополняем пустыми ячейками слева.
        widest = max(
            (len([cell for cell in chunk.split("|") if cell.strip()]) for chunk in chunks),
            default=columns,
        )
        if widest > columns:
            columns = widest
            header = [""] * (columns - len(header)) + header
        for chunk in chunks:
            row = [cell.strip() for cell in chunk.split("|")]
            if not any(cell for cell in row):
                continue
            row += [""] * (columns - len(row))
            out.append("| " + " | ".join(row[:columns]) + " |")
    return "\n".join(out)




def _align_table_columns(text: str) -> str:
    """Выравнивает число колонок в таблице по самой широкой строке."""
    lines = (text or "").split("\n")
    out: List[str] = []
    block: List[str] = []

    def flush() -> None:
        if not block:
            return
        rows = [line for line in block if line.strip().startswith("|")]
        width = max((len([c for c in row.strip().strip("|").split("|")]) for row in rows), default=0)
        for line in block:
            if not line.strip().startswith("|"):
                out.append(line)
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if set("".join(cells)) <= set("-: "):
                out.append("|" + "|".join(["---"] * width) + "|")
                continue
            if line is block[0]:
                cells = [""] * (width - len(cells)) + cells
            else:
                cells += [""] * (width - len(cells))
            out.append("| " + " | ".join(cells[:width]) + " |")
        block.clear()

    for line in lines:
        if line.strip().startswith("|"):
            block.append(line)
            continue
        flush()
        out.append(line)
    flush()
    return "\n".join(out)


def _is_separator_row(cells: List[str]) -> bool:
    joined = "".join(cell.replace(":", "").strip() for cell in cells)
    return bool(joined) and set(joined) <= {"-"}


def _fix_table_blocks(text: str) -> str:
    """Собирает таблицу в один блок и убирает лишние разделители.

    Правила:
    1. пустые строки внутри таблицы удаляются — иначе markdown рвёт её на части;
    2. строка из одних «---» остаётся только одна, сразу после заголовка;
    3. все строки выравниваются по самой широкой;
    4. если разделителя нет — он добавляется.
    """
    lines = (text or "").split("\n")
    out: List[str] = []
    block: List[str] = []

    def flush() -> None:
        if not block:
            return
        rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in block]
        data = [row for row in rows if not _is_separator_row(row)]
        if not data:
            block.clear()
            return
        if out and out[-1].strip():
            out.append("")
        width = max(len(row) for row in data)
        header = data[0] + [""] * (width - len(data[0]))
        out.append("| " + " | ".join(header) + " |")
        out.append("|" + "|".join(["---"] * width) + "|")
        for row in data[1:]:
            cells = row + [""] * (width - len(row))
            out.append("| " + " | ".join(cells) + " |")
        block.clear()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            block.append(stripped)
            continue
        if not stripped and block:
            # пустая строка внутри таблицы не закрывает блок
            continue
        flush()
        out.append(line)
    flush()
    return "\n".join(out)


def _close_table_gaps(text: str) -> str:
    """Убирает пустые строки внутри таблицы: иначе markdown рвёт её на части."""
    lines = str(text or "").splitlines()
    out = []
    for index, line in enumerate(lines):
        if line.strip():
            out.append(line)
            continue
        prev = next((l for l in reversed(out) if l.strip()), "")
        nxt = ""
        for candidate in lines[index + 1:]:
            if candidate.strip():
                nxt = candidate
                break
        if prev.strip().startswith("|") and nxt.strip().startswith("|"):
            continue
        out.append(line)
    return "\n".join(out)


def _normalize_tables(text: str) -> str:
    """Приводит любую таблицу к корректному markdown.

    Порядок: разбираем склеенные строки, разбиваем ряды по "||",
    затем собираем блок: одна шапка, один разделитель, ровные колонки.
    """
    if not text or "|" not in text:
        return text
    # Заголовок таблицы, приклеенный к концу абзаца: «…подсетями. | | NGFW | WAF |»
    text = re.sub(r"([.!?])\s+(\|)", r"\1\n\n\2", text)
    # Шапка, приклеенная к концу абзаца: «…приложение. || NGFW | WAF |»
    text = re.sub(
        r"([.!?])\s*\|\|\s*([^|\n]{1,60}?)\s*\|\s*([^|\n]{1,60}?)\s*\|",
        r"\1\n\n| Критерий | \2 | \3 |\n|---|---|---|",
        text,
    )
    text = _split_inline_table(text)
    text = _repair_table_headers(text)
    text = re.sub(r"\s*\|\|\s*", " |\n| ", text)
    text = _close_table_gaps(text)
    text = _normalize_table_shape(text)
    # Одинокий «|» — остаток недописанной таблицы, в ответе он не нужен.
    text = re.sub(r"(?m)^\s*\|\s*$\n?", "", text)
    return _fix_table_blocks(text)


_OTHER_LANG_RE = re.compile(
    r"in english|english please|answer in|по-английски|на английском|на китайском",
    re.I,
)
_SOURCES_HEAD_RE = re.compile(r"(?im)^\s*(#{1,4}\s*)?(источники|sources)\s*:?\s*$")


def _wants_other_language(question: str) -> bool:
    """Пользователь явно попросил ответить не по-русски."""
    return bool(_OTHER_LANG_RE.search(question or ""))


def _strip_sources_heading(text: str) -> str:
    """Убирает «### Источники»: список источников интерфейс показывает сам."""
    cleaned = _SOURCES_HEAD_RE.sub("", text or "")
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


_DOUBLE_PREP_RE = re.compile(r"(?i)\bна\s+на\s+(портале|странице|сайте)")


_PAREN_URL_RE = re.compile(r"\((https?://[^)\s]+)\)")
_PAREN_MD_LINK_RE = re.compile(r"\(\[([^\]]+)\]\((https?://[^)\s]+)\)\)")

_PAREN_HOST_RE = re.compile(
    r"\(((?:[a-z0-9-]+\.)+(?:ru|com|org|net|io)(?:/[^)\s]*)?)\)", re.I
)


_PAREN_MD_LINK_RE = re.compile(r"\(\[([^\]]+)\]\((https?://[^)\s]+)\)\)")
_PAREN_HOST_RE = re.compile(
    r"\(((?:[a-z0-9-]+\.)+(?:ru|com|org|net|io)(?:/[^)\s]*)?)\)", re.I
)
_PAREN_URL_RE = re.compile(r"\((https?://[^)\s]+)\)")


_PAREN_LINK_RE = re.compile(
    r"\(\[[^\]]+\]\((https?://[^)\s]+)\)"
    r"|\((https?://[^)\s]+)\)"
    r"|\(((?:[a-z0-9-]+\.)+(?:ru|com|org|net|io)(?:/[^)\s]*)?)\)",
    re.I,
)


_PAREN_LINK_RE = re.compile(
    r"\(\[[^\]]+\]\((https?://[^)\s]+)\)"
    r"|\((https?://[^)\s]+)\)"
    r"|\(((?:[a-z0-9-]+\.)+(?:ru|com|org|net|io)(?:/[^)\s]*)?)\)",
    re.I,
)


_PAREN_LINK_RE = re.compile(
    r"\(\[[^\]]+\]\((https?://[^)\s]+)\)" r"\)"
    r"|\((https?://[^)\s]+)\)"
    r"|\(((?:[a-z0-9-]+\.)+(?:ru|com|org|net|io)(?:/[^)\s]*)?)\)",
    re.I,
)


_WRAPPED_MD_LINK_RE = re.compile(
    r"\(\[[^\]]+\]\((https?://[^)\s]+)\)\)"
)
_PLAIN_MD_LINK_RE = re.compile(r"\[[^\]]+\]\(https?://[^)\s]+\)")
_PAREN_URL_RE = re.compile(r"\((https?://[^)\s]+)\)")
_PAREN_HOST_RE = re.compile(
    r"\(((?:[a-z0-9-]+\.)+(?:ru|com|org|net|io)(?:/[^)\s]*)?)\)", re.I
)


def _footnote_links(text: str, limit: int = 6) -> str:
    """«(ссылка)» → «[1](ссылка)», номера ведут сразу на страницу.

    Готовые ссылки «[текст](url)» остаются нетронутыми: иначе появлялась
    конструкция вида «[текст][1](url)», которая ломала разметку.
    """
    if not text or "(" not in text:
        return text

    shown: Dict[str, int] = {}

    def mark(url: str) -> str:
        key = url.strip()
        if not key.startswith("http"):
            key = "https://" + key
        if key not in shown:
            if len(shown) >= limit:
                return ""
            shown[key] = len(shown) + 1
        return f"[{shown[key]}]({key})"

    # 1. ссылка, целиком обёрнутая в скобки, — тоже примечание
    text = _WRAPPED_MD_LINK_RE.sub(lambda m: mark(m.group(1)), text)

    # 2. остальные готовые ссылки прячем, чтобы не разрезать их скобкой
    keep: List[str] = []

    def hide(match: re.Match) -> str:
        keep.append(match.group(0))
        return f"\u0002{len(keep) - 1}\u0002"

    text = _PLAIN_MD_LINK_RE.sub(hide, text)

    # 3. голые адреса и домены в скобках
    text = _PAREN_URL_RE.sub(lambda m: mark(m.group(1)), text)
    text = _PAREN_HOST_RE.sub(lambda m: mark(m.group(1)), text)

    # 4. возвращаем готовые ссылки
    return re.sub(r"\u0002(\d+)\u0002", lambda m: keep[int(m.group(1))], text)


def _structure_answer(text: str) -> str:
    """Дробит длинные абзацы: не больше 2–3 предложений в блоке."""
    if not text:
        return text

    def split_block(block: str, limit: int = 3) -> List[str]:
        block = block.strip()
        if len(block) < 260:
            return [block]
        sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", block) if part.strip()]
        if len(sentences) < limit + 1:
            return [block]
        chunks: List[str] = []
        buffer: List[str] = []
        for sentence in sentences:
            buffer.append(sentence)
            if len(buffer) >= 2:
                chunks.append(" ".join(buffer))
                buffer = []
        if buffer:
            chunks.append(" ".join(buffer))
        return chunks

    blocks = [block for block in re.split(r"\n{2,}", text) if block.strip()]
    out: List[str] = []
    for block in blocks:
        stripped = block.strip()
        if stripped.startswith(("#", "|", "-", "*", ">")) or stripped.count("\n") > 1:
            out.append(stripped)
            continue
        out.extend(split_block(stripped))
    return "\n\n".join(out)


def _client_text(text: str) -> str:
    """Убирает из ответа служебные ссылки на файлы, когда включён клиентский режим."""
    cleaned = text or ""
    for pattern, replacement in _CLIENT_PHRASES:
        cleaned = pattern.sub(replacement, cleaned)
    cleaned = _SOURCE_PAREN_WORDS_RE.sub("", cleaned)
    cleaned = _SOURCE_PAREN_CODE_RE.sub("", cleaned)
    cleaned = _SOURCE_FILE_RE.sub("", cleaned)
    cleaned = _SOURCE_PAREN_RE.sub("", cleaned)
    cleaned = _SOURCE_CODE_RE.sub("", cleaned)
    cleaned = _SOURCE_LINE_RE.sub("", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([.,;:!?])", r"\1", cleaned)
    # «… и.» после удаления цитаты
    cleaned = re.sub(r"\s+(?:и|или|а|но)\s*([.,;:!?])", r"\1", cleaned)
    # После вырезанной ссылки остаётся «переменную:.» или «текст :.» — чистим.
    cleaned = re.sub(r":\s*([.,;])", r"\1", cleaned)
    cleaned = re.sub(r"\s+:\s*", ": ", cleaned)
    cleaned = re.sub(r"\[\s*\]", "", cleaned)
    cleaned = re.sub(r"\(\s*\)", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(
        r"(?m)(^|\n\n)(по нашим данным)",
        lambda match: match.group(1) + "По нашим данным",
        cleaned,
    )
    return cleaned.strip()


def _empty_usage() -> Dict[str, int]:
    return {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def _merge_usage(total: Dict[str, int], usage: Optional[Dict[str, Any]]) -> None:
    if not usage:
        return
    total["calls"] += 1
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        try:
            total[key] += int(usage.get(key) or 0)
        except (TypeError, ValueError):
            continue


def _short_query(question: str) -> str:
    """Убирает служебные слова: запасной запрос для поиска."""
    words = re.findall(r"[\w-]{4,}", question or "")
    stop = {
        "какие", "какой", "какая", "каких", "что", "чем", "где", "когда",
        "сколько", "есть", "как", "для", "про", "или", "при", "это",
        "нужно", "можно", "ли", "входит", "поддерживаются", "отличается",
    }
    return " ".join(word for word in words if word.lower() not in stop)[:200]


class PartnerAgent:
    def __init__(
        self,
        retriever: Retriever,
        settings: Settings,
        client: Optional[DeepSeekClient] = None,
        cache: Optional[AnswerCache] = None,
        profile: Optional[AgentProfile] = None,
    ) -> None:
        self.retriever = retriever
        self.settings = settings
        self.client = client
        self.cache = cache
        self.stats = retriever.stats()
        self._mode_cache: dict[str, tuple[str, str, str]] = {}
        # Карта «файл материала → публичная ссылка»: чтобы в ответе были ссылки,
        # а не имена файлов (собирается tools/build_source_links.py).
        self._source_links: Dict[str, str] = self._load_source_links()
        # Тексты найденных фрагментов по ссылке: для проверки приписывания.
        self._source_texts: Dict[str, str] = {}
        self._news_excluded = False
        self._judge = Judge(client) if (client is not None and settings.judge_enabled) else None
        self.profile = profile or build_profile(
            settings.data_dir,
            company_name=self.stats.get("company") or settings.company_name,
            limits={
                "max_tokens": settings.max_tokens,
                "fast_max_tokens": settings.fast_max_tokens,
                "local_max_tokens": settings.local_max_tokens,
                "max_steps": settings.max_steps,
            },
        )
        self.company = self.profile.company_name or self.stats.get("company") or "компания"
        self.tools = tools_for(self.profile)
        # Кнопки-продолжения: только то, что привязано к вопросу (см. followups.py).
        self._followup_planner = FollowupPlanner(retriever)
        self._followup_planner.warm()

    # --- инструменты ----------------------------------------------------
    def _tool_plan(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        steps = [str(step).strip() for step in (args.get("steps") or []) if str(step).strip()]
        return {
            "result": {"ok": True, "steps": steps},
            "summary": f"план из {len(steps)} шагов" if steps else "план",
            "sources": [],
            "plan": {"steps": steps[:6], "reasoning": str(args.get("reasoning") or "")[:600]},
        }

    def _tool_search_knowledge(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        query = str(args.get("query") or "").strip()
        top_k = max(1, min(int(args.get("top_k") or self.settings.top_k), 10))
        hits = self.retriever.search(query, k=top_k)
        payload = {
            "query": query,
            "chunks": [
                _compact(
                    {
                        "title": hit.chunk.get("title"),
                        "kind": hit.chunk.get("kind"),
                        "source": hit.chunk.get("source"),
                        "text": _clip(str(hit.chunk.get("text") or ""), 700),
                    }
                )
                for hit in hits
            ],
        }
        sources = [hit.to_source() for hit in hits]
        summary = f"фрагментов: {len(hits)}" if hits else "ничего не найдено"
        return {"result": payload, "summary": summary, "sources": sources}

    def _tool_company_profile(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        if _looks_like_injection(question):
            # Инъекция: инструмент не отдаёт карточку, отказать обязана модель.
            return {
                "result": {"found": False, "refused": True},
                "summary": "запрос пытается изменить инструкции — карточка не отдаётся",
                "sources": [],
            }
        company = self.retriever.company()
        if not company:
            return {"result": {"found": False}, "summary": "карточка компании не заполнена", "sources": []}
        payload = _compact(
            {
                "name": company.get("name"),
                "site": company.get("site"),
                "industry": company.get("industry"),
                "description": _clip(str(company.get("description") or ""), 800),
                "products": company.get("products"),
                "contacts": company.get("contacts"),
                "source": company.get("source"),
            }
        )
        sources = []
        if company.get("source"):
            sources = [
                {
                    "id": "company",
                    "title": f"Компания {company.get('name')}",
                    "kind": "company",
                    "score": 1.0,
                    "why": ["profile"],
                    "excerpt": _clip(str(company.get("description") or ""), 200),
                    "source": company["source"],
                }
            ]
        return {"result": payload, "summary": f"карточка {company.get('name')}", "sources": sources}

    def _tool_find_product(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        query = str(args.get("query") or "").strip()
        records = self.retriever.find_product(query, limit=5)
        payload = {
            "products": [
                _compact(
                    {
                        "name": record.get("name"),
                        "description": _clip(str(record.get("description") or ""), 400),
                        "source": record.get("source"),
                    }
                )
                for record in records
            ]
        }
        return {
            "result": payload,
            "summary": f"продуктов: {len(records)}" if records else "продукт не найден",
            "sources": [],
        }

    def _tool_find_person(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        query = str(args.get("query") or "").strip()
        records = self.retriever.find_person(query, limit=5)
        payload = {
            "people": [
                _compact(
                    {
                        "name": record.get("name"),
                        "role": record.get("role"),
                        "source": record.get("source"),
                    }
                )
                for record in records
            ]
        }
        return {
            "result": payload,
            "summary": f"сотрудников: {len(records)}" if records else "сотрудник не найден",
            "sources": [],
        }

    def _tool_find_faq(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        query = str(args.get("query") or "").strip()
        records = self.retriever.find_faq(query, limit=5)
        payload = {
            "faq": [
                _compact(
                    {
                        "question": record.get("question"),
                        "answer": _clip(str(record.get("answer") or ""), 500),
                        "source": record.get("source"),
                    }
                )
                for record in records
            ]
        }
        return {
            "result": payload,
            "summary": f"вопросов: {len(records)}" if records else "в FAQ не найдено",
            "sources": [],
        }

    def _tool_ask_clarification(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        clarification = _clean_clarification(args)
        if not clarification:
            return {
                "result": {"error": "нужно 2–10 вопросов с вариантами"},
                "summary": "уточнение не сформировано",
                "sources": [],
            }
        return {
            "result": clarification,
            "clarification": clarification,
            "summary": "уточняющий вопрос клиенту",
            "sources": [],
        }

    def _tool_offer_followups(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        items = _clean_followups(args.get("items"))
        summary = (
            f"предложил продолжить: {len(items)}"
            if items
            else "продолжение не предложено"
        )
        return {
            "result": {"items": items, "count": len(items)},
            "summary": summary,
            "sources": [],
        }

    def _tool_kb_stats(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        stats = dict(self.stats)
        stats.pop("kinds", None)
        return {"result": stats, "summary": f"фрагментов: {stats.get('chunks')}", "sources": []}

    def _execute(self, call: ToolCall, question: str = "") -> Dict[str, Any]:
        try:
            args = json.loads(call.arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        if not isinstance(args, dict):
            args = {}
        handlers = {
            "plan": self._tool_plan,
            "search_knowledge": self._tool_search_knowledge,
            "company_profile": self._tool_company_profile,
            "find_product": self._tool_find_product,
            "find_person": self._tool_find_person,
            "find_faq": self._tool_find_faq,
            "kb_stats": self._tool_kb_stats,
            "offer_followups": self._tool_offer_followups,
            "ask_clarification": self._tool_ask_clarification,
        }
        handler = handlers.get(call.name)
        if handler is None:
            return {"result": {"error": f"неизвестный инструмент {call.name}"}, "summary": "ошибка", "sources": []}
        try:
            return handler(args, question)
        except Exception as exc:  # noqa: BLE001
            return {"result": {"error": str(exc)}, "summary": f"ошибка инструмента: {exc}", "sources": []}

    # --- контекст -------------------------------------------------------

    @staticmethod
    def _short_query(question: str) -> str:
        """Убирает служебные слова: запасной запрос для поиска."""
        words = re.findall(r"[\w-]{4,}", question or "")
        stop = {
            "какие", "какой", "какая", "каких", "что", "чем", "где", "когда",
            "сколько", "есть", "как", "для", "про", "или", "при", "это",
            "нужно", "можно", "ли", "входит", "поддерживаются", "отличается",
        }
        return " ".join(word for word in words if word.lower() not in stop)[:200]


    def _auto_context(
        self,
        question: str,
        show_notes: bool = True,
        hits: Optional[int] = None,
        catalog: bool = False,
    ) -> tuple[str, List[Dict[str, Any]]]:
        self._current_question = question
        if not self.settings.auto_context:
            return "", []
        lines: List[str] = [
            "",
            "КОНТЕКСТ (уже загружено — инструменты не нужны):"
            if show_notes
            else "СПРАВКА (факты для ответа):",
        ]
        company = self.retriever.company()
        if company:
            lines.append(
                "Компания: "
                + ", ".join(
                    part
                    for part in (
                        str(company.get("name") or ""),
                        str(company.get("industry") or ""),
                        str(company.get("site") or ""),
                    )
                    if part
                )
            )
            if company.get("description"):
                lines.append("Описание: " + _clip(str(company["description"]), 500))

        if catalog:
            lines.append("Каталог программ:")
            for record in self.retriever.products():
                name = str(record.get("name") or "").strip()
                description = _clip(str(record.get("description") or ""), 240)
                if name:
                    lines.append(f"- {name}: {description}")
        for record in self.retriever.find_product(question, limit=2):
            lines.append(f"Продукт: {record.get('name')} — {_clip(str(record.get('description') or ''), 300)}")
        for record in self.retriever.find_person(question, limit=2):
            role = f" ({record.get('role')})" if record.get("role") else ""
            lines.append(f"Сотрудник: {record.get('name')}{role}")

        glossary = self.retriever.find_term(question, limit=2)

        base_hits = hits or self.profile.retrieval.context_hits
        if _is_enumeration(question) or re.search(
            r"перечисли|список|какие .*существу|все (?:главы|журналы|курсы|платформы)",
            question,
            re.I,
        ):
            base_hits = max(base_hits, 6)
        hits = self._search_hits(question, k=base_hits)
        # Вопрос о контактах: карточка контактов важнее любых совпадений по словам.
        if re.search(r"адрес|офис|офисы|контакт|находит|где вы|как добраться", question, re.I):
            contact_hits = [
                hit
                for hit in self.retriever.search(question + " адрес офиса контакты", k=6)
                if "contacts" in str(hit.chunk.get("source") or "")
            ]
            if contact_hits:
                known = {id(hit) for hit in contact_hits}
                hits = contact_hits[:2] + [hit for hit in hits if id(hit) not in known]
        hits = self._drop_foreign_platforms(question, hits)
        if re.search(r"оглавлен|главы|глава|содержани|руководств", question, re.I):
            try:
                toc_hits = [
                    hit
                    for hit in self.retriever.search(question + " оглавление руководства главы", k=8)
                    if "manual-tocs" in str(hit.chunk.get("source") or "")
                ]
                if toc_hits:
                    known = {id(hit) for hit in toc_hits}
                    hits = toc_hits[:2] + [hit for hit in hits if id(hit) not in known]
            except Exception:  # noqa: BLE001
                pass
        if re.search(r"\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\b", question):
            # Вопрос по имени человека: поднимаем фрагменты, где имя встречается.
            try:
                name = re.search(r"\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\b", question).group(0)
                person_hits = [
                    hit
                    for hit in self.retriever.search(name, k=6)
                    if name.lower().split()[0] in str(hit.chunk.get("text") or "").lower()
                    and name.lower().split()[1] in str(hit.chunk.get("text") or "").lower()
                ]
                if person_hits:
                    known = {id(hit) for hit in person_hits}
                    hits = person_hits[:2] + [hit for hit in hits if id(hit) not in known]
            except Exception:  # noqa: BLE001
                pass
        if re.search(r"адрес|офис|контакт|находит|где вы", question, re.I):
            # Официальный адрес из портала документации — прямо в контекст,
            # чтобы модель не объявляла его отсутствующим.
            try:
                for cand in self.retriever.search("121087 Береговой проезд офис Москва", k=6):
                    src = str(cand.chunk.get("source") or "")
                    text = str(cand.chunk.get("text") or "")
                    if ("kontakty" in src or "contacts" in src) and "121087" in text:
                        facts = " ".join(text.split())
                        lines.append("ОФИЦИАЛЬНЫЕ ДАННЫЕ (подтверждено сайтом): " + facts[:600])
                        break
            except Exception:  # noqa: BLE001
                pass
        if len(hits) < 3:
            extra_hits = self._search_hits(_short_query(question), k=base_hits)
            known = {id(hit.chunk.get("id")) for hit in hits}
            for extra in extra_hits:
                if id(extra.chunk.get("id")) not in known:
                    hits.append(extra)
        if _asks_certificate(question):
            lines.append(
                "СЕРТИФИКАТ: в материалах подтверждён только сертификат UserGate NGFW "
                "(№ 3905, 4-й уровень доверия). На другие продукты он не переносится: "
                "если для WAF, SIEM, Client или DCFW номера в контексте нет — так и скажи."
            )
        if _is_enumeration(question):
            # Собираем полный перечень из закреплённых и приоритетных фрагментов:
            # модель получает готовый список и не сокращает его до примера.
            enum_source = " ".join(
                str(hit.chunk.get("text") or "") for hit in hits[:8]
            )
            enum_items = _list_items_from(enum_source)
            hint = (
                "ВОПРОС-ПЕРЕЧИСЛЕНИЕ: перечисли ВСЕ элементы из списка ниже, "
                "не сокращая до одного примера."
            )
            if enum_items:
                hint += " Полный перечень из материалов: " + ", ".join(enum_items) + "."
            lines.append(hint)
        sources: List[Dict[str, Any]] = []
        # Жёсткий бюджет контекста: даже при длинных фрагментах промпт не раздувается.
        if any(word in (question or "").lower() for word in ("академ", "экзамен", "преподавател")):
            official_text = _official_facts_text()
            if official_text:
                lines.append("ОФИЦИАЛЬНЫЕ ДАННЫЕ (приоритет): " + _clip(official_text, 2200))

        budget = self.profile.retrieval.context_budget_chars
        used = sum(len(line) for line in lines)
        # Термин из глоссария — самый точный ответ на «что такое X».
        for entry in glossary:
            definition = str(entry.get("definition") or "").strip()
            if not definition:
                continue
            source = str(entry.get("source") or "")
            link = self._link_for(source)
            excerpt = _clip(definition, 400)
            room = budget - used
            if room <= 120:
                break
            if len(excerpt) > room:
                excerpt = _clip(excerpt, room)
            if show_notes:
                header = (
                    f"[Термин: {entry.get('term')} · {link}]"
                    if link
                    else f"[Термин: {entry.get('term')} · {source}]"
                )
            else:
                host = _url_host(link)
                header = f"Факт ({host}):" if host else "Факт:"
            block = f"{header}\n                {excerpt}"
            lines.append(block)
            used += len(block)
            if link:
                self._source_texts[_norm_url(link)] = definition
            sources.append(
                {
                    "id": f"glossary:{(entry.get('term') or '').strip()}",
                    "title": str(entry.get("term") or ""),
                    "kind": "glossary",
                    "score": 1.0,
                    "why": ["glossary"],
                    "excerpt": excerpt,
                    "source": source,
                    "url": link,
                }
            )
        # Порядок в контексте: закреплённые фрагменты, затем таблицы, затем остальное.
        # Таблица, обрезанная посередине, теряет смысл, поэтому такие фрагменты
        # получают больший лимит и попадают в контекст раньше остальных.
        ordered_hits = sorted(
            hits,
            key=lambda item: (
                0 if "pinned" in getattr(item, "why", []) else 1,
                0 if "|---" in str(item.chunk.get("text") or "") else 1,
            ),
        )
        seen_texts: set = set()
        for hit in ordered_hits:
            text = str(hit.chunk.get("text") or "")
            if not text:
                continue
            # Полные текстовые дубли (один фрагмент из двух каналов) — пропускаем.
            normalized = re.sub(r"\s+", " ", text.lower()).strip()
            if normalized in seen_texts:
                continue
            seen_texts.add(normalized)
            if show_notes:
                link = self._link_for(str(hit.chunk.get("source") or ""))
                header = (
                    f"[{hit.chunk.get('title')} · {link}]"
                    if link
                    else f"[{hit.chunk.get('title')} · {hit.chunk.get('source')}]"
                )
            else:
                host = _url_host(self._link_for(str(hit.chunk.get("source") or "")))
                header = f"Факт ({host}):" if host else "Факт:"
            limit_chars = self.profile.retrieval.excerpt_chars
            if "pinned" in getattr(hit, "why", []):
                limit_chars = max(limit_chars, 1100)
            if "|---" in text or "\n|" in text:
                # Таблицу отдаём целиком: обрезанная, она теряет смысл.
                limit_chars = max(limit_chars, 1500)
            excerpt = _clip(_sanitize_excerpt(text), limit_chars)
            room = budget - used
            if room <= 120:
                break
            if len(excerpt) > room:
                excerpt = _clip(excerpt, room)
            block = f"{header}\n                {excerpt}"
            lines.append(block)
            used += len(block)
            record = hit.to_source()
            link = self._link_for(str(record.get("source") or ""))
            record["url"] = link
            if link:
                # Текст фрагмента для проверки приписывания; клиенту не передаётся.
                self._source_texts[_norm_url(link)] = text
            if not show_notes:
                # В клиентском режиме не показываем внутренние пути к файлам:
                # только публичный хост или нейтральная подпись.
                host = _url_host(link)
                record["source"] = host or "материалы компании"
            sources.append(record)
        text_block = "\n".join(lines)
        # Судья проверяет сам контекст: если фактов не хватает, модель получает
        # явный запрет выдумывать вместо того, чтобы заполнять пробелы.
        if self._judge is not None and sources:
            expect_absent = not any(
                str(item.get("kind") or "") not in ("news",) for item in sources
            )
            verdict = self._judge.judge_context(question, text_block, expect_absent=expect_absent)
            warning = context_warning(verdict)
            if warning:
                write_log(f"  ! судья контекста: {verdict.comment or 'недостаточно фактов'}")
                lines.append(warning)
                text_block = "\n".join(lines)
        return text_block, sources

    @staticmethod
    def _context_key(history: Optional[Sequence[Dict[str, Any]]]) -> str:
        if not history:
            return ""
        parts = []
        for item in list(history)[-8:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = str(item.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                parts.append(f"{role}:{content}")
        if not parts:
            return ""
        return hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()[:16]

    def _should_offer_followups(self, question: str, answer: str) -> bool:
        text = (answer or "").strip()
        if len(text) < 140:
            return False
        return True

    def _suggest_followups(
        self,
        question: str,
        answer: str,
        sources: Optional[Sequence[Dict[str, Any]]] = None,
        staff: bool = False,
        lang: str = "ru",
        keep: Optional[Sequence[str]] = None,
    ) -> List[str]:
        """Продолжения, привязанные к вопросу (см. partner/followups.py).

        `staff` — сотрудник ли спрашивает. Сотруднику нужны рабочие вопросы
        (соседние сборки, изменения, канал поддержки), а не «сколько стоит».
        `keep` — уже одобренные кнопки, которые план только добирает.
        """
        try:
            items = self._followup_planner.plan(
                question,
                answer,
                sources or [],
                staff=staff,
                lang=lang,
                keep=keep or (),
            )
        except Exception:  # noqa: BLE001 - кнопки не должны ронять ответ
            return []
        return _clean_followups(items)

    def _review_followups(
        self,
        items: Optional[Sequence[str]],
        question: str,
        answer: str,
        sources: Optional[Sequence[Dict[str, Any]]] = None,
        staff: bool = False,
        lang: str = "ru",
    ) -> List[str]:
        """Проверяет кнопки модели: оставляет только привязанные к вопросу."""
        if not items:
            return []
        try:
            kept = self._followup_planner.review(
                list(items), question, answer, sources or [], staff=staff, lang=lang
            )
        except Exception:  # noqa: BLE001
            return _clean_followups(items)
        return _clean_followups(kept)

    # --- проверка ссылок в ответе ---------------------------------------
    def _verified_answer(self, answer: str, sources: Sequence[Dict[str, Any]]) -> str:
        """Проверяет, что ссылки в ответе действительно подтверждают утверждение.

        Две проверки:
        1. ссылка должна быть среди найденных источников — иначе это выдумка;
        2. предложение со ссылкой должно пересекаться по словам с текстом этого
           источника — иначе модель приписала факт не той странице.
        """
        allowed: Dict[str, str] = {}
        for item in sources or []:
            text = ""
            for key in ("url", "source"):
                value = str(item.get(key) or "")
                if not value.startswith("http"):
                    continue
                norm = _norm_url(value)
                text = self._source_texts.get(norm, "")
                allowed[norm] = text
        # Адрес может стоять прямо в тексте фрагмента (например, ссылка на канал
        # в карточке контактов) — такой адрес тоже подтверждён материалом.
        for norm, text in self._source_texts.items():
            allowed.setdefault(norm, text)
            for found in ANSWER_URL_RE.findall(text):
                allowed.setdefault(_norm_url(found), text)

        def known(url: str) -> Optional[str]:
            norm = _norm_url(url)
            if not norm:
                return None
            # Официальные площадки компании: ссылки на них не выдуманы,
            # даже если страницы нет в списке источников.
            host = _url_host(url)
            if host and (
                host.endswith("usergate.com")
                or host in {"t.me", "vk.com", "habr.com", "youtube.com", "rutube.ru"}
            ):
                return norm
            if norm in allowed:
                return norm
            for candidate in allowed:
                if norm.startswith(candidate) or candidate.startswith(norm):
                    return candidate
            return None

        def supported(sentence: str, url: str) -> bool:
            key = known(url)
            if key is None:
                # Для «голой» ссылки достаточно совпадения хоста: путь может быть
                # другим разделом того же сайта, и вырезать его из фразы нельзя.
                host = _url_host(url)
                if host and any(host == _url_host(item) for item in allowed):
                    return True
                return False
            chunk_text = allowed.get(key) or ""
            if not chunk_text:
                return True                     # нечем сверять — не мешаем
            stripped = sentence.strip().strip("-—•*").strip()
            if stripped.startswith(("http://", "https://")):
                return True                     # строка списка источников, не утверждение
            tokens = {
                token for token in re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", sentence)
                if token.lower() not in {"http", "https", "www", "com", "html", "ru"}
            }
            tokens |= {number for number in re.findall(r"\d{2,}", sentence)}
            if not tokens:
                return True
            body = chunk_text.lower()
            return all(token.lower() in body for token in tokens)

        dropped: List[str] = []

        def markdown_repl(match: re.Match) -> str:
            label, url = match.group(1), match.group(2)
            sentence = _sentence_around(match.string, match.start(), match.end())
            if supported(sentence, url):
                return match.group(0)
            dropped.append(url)
            # Путь к файлу вместо ссылки клиенту не показываем.
            if re.fullmatch(r"[\w./-]+\.(md|txt|json|csv)", label.strip()):
                return ""
            return label

        text = MARKDOWN_LINK_RE.sub(markdown_repl, answer)

        def bare_repl(match: re.Match) -> str:
            url = match.group(0)
            sentence = _sentence_around(match.string, match.start(), match.end())
            if supported(sentence, url):
                return url
            dropped.append(url)
            return ""

        text = ANSWER_URL_RE.sub(bare_repl, text)

        # Адрес без схемы («docs.usergate.com/xxx») тоже не должен пережить
        # проверку, если такого пути нет среди источников.
        def domain_repl(match: re.Match) -> str:
            url = match.group(0)
            if known(url) is not None:
                return url
            dropped.append(url)
            return "на портале документации"

        # Сначала прячем уже принятые ссылки, иначе проверка доменов без схемы
        # вырезает их середину и оставляет «https://docs.на портале».
        kept_urls: List[str] = []

        def _hide(match: re.Match) -> str:
            kept_urls.append(match.group(0))
            return f"\u0000U{len(kept_urls) - 1}\u0000"

        text = ANSWER_URL_RE.sub(_hide, text)
        text = DOMAIN_ONLY_RE.sub(domain_repl, text)
        text = re.sub(r"\u0000U(\d+)\u0000", lambda m: kept_urls[int(m.group(1))], text)
        # Схема, оставшаяся от вырезанного адреса, даёт «https://на портале».
        text = re.sub(r"https?://(?=на портале)", "", text)
        text = re.sub(r"https?://(?=страниц)", "", text)
        text = _DOUBLE_PREP_RE.sub(r"на \1", text)
        if dropped:
            write_log(f"  ! убраны неподтверждённые ссылки: {len(dropped)}")
            text = re.sub(r"(?m)^\s*[-—•*]\s*$\n?", "", text)   # пустые пункты списка
            text = re.sub(r"\(\s*\)", "", text)                 # пустые скобки от ссылок
            text = re.sub(r"\((?:Источник|источник|ссылка)\s*:?\s*\)", "", text)
            text = re.sub(r"\s+\((?:Источник|источник)\s*:?\s*\)", "", text)
            text = re.sub(r"\*\*\s*\*\*", "", text)             # пустое выделение
            text = re.sub(r"(?<=\*\*)\s+(?=\S)", " ", text)
            text = re.sub(r"\s+([.,;:])", r"\1", text)
            text = re.sub(r"[ \t]{2,}", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
        # Коды программ и цены, которых нет в источниках, — выдумка модели.
        if self._source_texts:
            body = " ".join(self._source_texts.values()).lower()
            # Пробелы внутри цен и кодов не должны давать ложных срабатываний.
            body_compact = re.sub(r"[\s\u00a0]", "", body)
            invented_values: List[str] = []

            def _guard(pattern: re.Pattern):
                def repl(match: re.Match) -> str:
                    value = match.group(0)
                    if re.sub(r"[\s\u00a0]", "", value.lower()) in body_compact:
                        return value
                    invented_values.append(value)
                    return ""

                return repl

            text = CODE_GUARD_RE.sub(_guard(CODE_GUARD_RE), text)
            text = PRICE_GUARD_RE.sub(_guard(PRICE_GUARD_RE), text)
            if invented_values:
                text = re.sub(r"\s{2,}", " ", text)
                text = re.sub(r"\s+([.,;:])", r"\1", text)
                write_log(f"  ! убраны неподтверждённые коды и цены: {len(invented_values)}")

        # К каждому сертификату — ссылка на реестр, а не одна общая.
        if "сертификат" in text.lower() and "registry-entry" not in text:
            text = re.sub(
                r"(сертификат[^.\n]{0,140}?№\s*\d{3,4})",
                r"\1 (https://usergate.com/registry-entry)",
                text,
                count=2,
                flags=re.I,
            )

        text = _strip_sources_heading(_normalize_tables(text)).strip()
        # Точка в конце: обрезанная ссылка оставляла фразу без завершения.
        if text and text[-1].isalnum():
            text += "."
        return text

    # --- выбор режима ---------------------------------------------------
    # --- поиск с повторными попытками ------------------------------------
    def _coverage(self, question: str, hits: Sequence[SearchHit]) -> float:
        """Доля слов вопроса, которые встречаются в найденных фрагментах."""
        terms = {term for term in query_terms(question) if len(term) >= 3}
        if not terms:
            return 1.0
        body = " ".join(str(hit.chunk.get("text") or "").lower() for hit in hits[:4])
        return len({term for term in terms if term in body}) / len(terms)

    def _rare_probe_terms(self, question: str) -> List[str]:
        """Редкие термины вопроса, которых нет в карточках.

        «UserID» или «BATV» в карточках не встречаются, поэтому общий поиск
        топит их в новостях. Для таких слов делаем отдельную точечную попытку.
        """
        cards: List[str] = [
            str(item.get("question") or "") for item in self.retriever.entities.get("faq") or []
        ]
        cards += [str(item.get("name") or "") for item in self.retriever.products()]
        cards_text = " ".join(cards).lower()
        terms: List[str] = []
        for token in query_terms(question):
            if len(token) < 3 or not re.fullmatch(r"[a-z0-9]+", token):
                continue
            if token in cards_text:
                continue
            terms.append(token)
        return terms[:2]

    def _decomposition_probes(self, question: str) -> List[str]:
        """Подзапросы из одного вопроса: слова парами и части по «и» / «или».

        «Какие типы кластеров поддерживает DCFW» распадается на «типы кластеров»,
        «кластеров dcfw», цельные слова — это вытаскивает вторую половину
        перечисления, которую слитная фраза не находит.
        """
        words = [word for word in query_terms(question) if len(word) >= 3]
        probes: List[str] = []
        if len(words) >= 2:
            probes.append(" ".join(words))
            for index in range(len(words) - 1):
                pair = f"{words[index]} {words[index + 1]}"
                if pair not in probes:
                    probes.append(pair)
        for part in re.split(r"\s+и\s+|,\s*|\s+или\s+", question):
            clean = " ".join(word for word in query_terms(part) if len(word) >= 3)
            if clean and clean not in probes:
                probes.append(clean)
        # Синонимы: «МЭ», «веб-экран», «тг» ищутся по каноническому названию.
        lowered = (question or "").lower()
        for alias, canonical in _ALIASES.items():
            if alias in lowered and canonical not in probes:
                probes.append(canonical)
        return probes[:5]

    _VERSION_RE = re.compile(r"\b\d+\.\d+(?:\.\d+)?(?:[xX])?\b")

    def _asks_versions(self, question: str) -> bool:
        return bool(re.search(r"\bверси|версия|версии|версий|релиз", (question or "").lower()))

    def _version_hits(self, question: str) -> List[SearchHit]:
        """Вопросы о версиях: поднимаем карточку версий и страницы совместимости.

        Поиск по словам «какие версии WAF» цепляет FAQ про бесплатную версию,
        а нужная таблица версий лежит в курируемой карточке и почти не содержит
        общих слов запроса.
        """
        if not self._asks_versions(question):
            return []
        tokens = [t for t in query_terms(question) if len(t) >= 3]
        products = [name for name in ("waf", "ngfw", "dcfw", "swg", "siem", "client") if name in tokens]
        # Карточка версий — первым делом: в ней таблица по всем продуктам.
        card = self.retriever.chunks_by_source("versions-and-platforms", limit=2)
        probes = ["Версии продуктов и аппаратные платформы", "версии продуктов документация"]
        probes += [f"{name} версии документация" for name in products[:2]]
        seen: set[str] = set()
        found: List[tuple] = [(3, hit) for hit in card]
        for probe in probes:
            for hit in self.retriever.search(probe, k=5):
                chunk_id = str(hit.chunk.get("id"))
                if chunk_id in seen:
                    continue
                text = str(hit.chunk.get("text") or "")
                if not self._VERSION_RE.search(text):
                    continue
                source = str(hit.chunk.get("source") or "")
                # карточки версий и совместимости — в первую очередь
                priority = 2 if ("versions-and-platforms" in source or "sovmestimost" in source) else 1
                seen.add(chunk_id)
                found.append((priority, hit))
        found.sort(key=lambda pair: pair[0], reverse=True)
        return [hit for _priority, hit in found[:2]]

    def _enumeration_hits(self, question: str) -> List[SearchHit]:
        """Для перечислений подтягиваем карточку-список по теме вопроса."""
        if not _is_enumeration(question):
            return []
        lowered = (question or "").lower()
        found: List[SearchHit] = []
        seen: set[str] = set()
        for keywords, sources in _LIST_HINTS:
            if not any(word in lowered for word in keywords):
                continue
            for pattern in sources:
                chunks = self.retriever.chunks_by_source(pattern, limit=8)
                # Приоритет фрагменту, где ключевое слово стоит в заголовке раздела
                # или есть таблица: список офисов лежит в разделе «Офисы».
                def list_score(hit: SearchHit) -> int:
                    head = str(hit.chunk.get("text") or "")[:200].lower()
                    score = sum(1 for word in keywords if word in head)
                    if "|---" in head:
                        score += 2
                    return score

                matched = sorted(
                    (hit for hit in chunks if list_score(hit) > 0),
                    key=list_score,
                    reverse=True,
                )
                for hit in (matched or chunks)[:2]:
                    chunk_id = str(hit.chunk.get("id"))
                    if chunk_id in seen:
                        continue
                    seen.add(chunk_id)
                    found.append(hit)
        return found[:3]

    def _product_card_hits(self, question: str) -> List[SearchHit]:
        """Карточка упомянутого продукта: в ней версии, кластеры и параметры."""
        mentioned = [str(item.get("name") or "") for item in self.retriever.find_product(question, limit=2)]
        if not mentioned:
            return []
        found: List[SearchHit] = []
        seen: set[str] = set()
        terms = [term for term in query_terms(question) if len(term) >= 4]
        for name in mentioned:
            slug = "".join(ch for ch in name.lower() if ch.isalnum() or ch in "-_")
            if not slug:
                continue
            chunks = self.retriever.chunks_by_source(f"products/{slug}", limit=20)

            def card_overlap(hit: SearchHit) -> int:
                text = str(hit.chunk.get("text") or "").lower()
                head = text[:90]
                score = sum(1 for term in terms if term in text)
                score += 3 * sum(1 for term in terms if term[:5] in head)
                return score

            for hit in sorted(chunks, key=card_overlap, reverse=True):
                if card_overlap(hit) == 0 and terms:
                    continue
                chunk_id = str(hit.chunk.get("id"))
                if chunk_id in seen:
                    continue
                seen.add(chunk_id)
                found.append(hit)
        return found[:2]

    def _topic_hits(self, question: str) -> List[SearchHit]:
        """Тематические карточки: кластеры, журналы, сертификация."""
        lowered = (question or "").lower()
        terms = [term for term in query_terms(question) if len(term) >= 5]
        found: List[SearchHit] = []
        seen: set[str] = set()
        # Аппаратные вопросы: характеристики лежат в таблицах даташита,
        # поэтому берём именно табличные фрагменты, а не первые по словам.
        if any(word in lowered for word in ("x10", "порт", "интерфейс", "пропускн", "производительн", "gb")):
            # Если назван код платформы — берём её документы целиком, без
            # требования табличных разделителей: в OCR-даташитах их нет.
            codes = [
                token for token in query_terms(question)
                if token in {"b50", "c100", "c150", "c151", "d200", "d250", "d500",
                             "e1000", "e1010", "e3000", "e3010", "f8000", "f8010",
                             "fg", "x1", "x10"}
            ]
            for code in codes[:2]:
                platform_hits = [
                    hit
                    for hit in self.retriever.chunks_by_source(f"docs/hardware/{code}", limit=40)
                    if any(marker in str(hit.chunk.get("text") or "")
                           for marker in ("SFP", "Гбит", "Мбит", "порт", "Процессор", "температур"))
                ]
                platform_hits.sort(
                    key=lambda item: (
                        0 if "datasheet" in str(item.chunk.get("source") or "") else 1,
                        -sum(
                            1
                            for marker in ("SFP", "Гбит", "Мбит", "Процессор")
                            if marker in str(item.chunk.get("text") or "")
                        ),
                    )
                )
                for hit in platform_hits[:3]:
                    chunk_id = str(hit.chunk.get("id"))
                    if chunk_id not in seen:
                        seen.add(chunk_id)
                        found.append(hit)
            tables = [
                hit
                for hit in self.retriever.chunks_by_source("docs/hardware", limit=40)
                if "|---" in str(hit.chunk.get("text") or "")
                and any(
                    marker in str(hit.chunk.get("text") or "")
                    for marker in ("RJ-45", "Мбит", "Процессор", "ГГц", "SFP+")
                )
            ]
            for hit in tables[:3]:
                chunk_id = str(hit.chunk.get("id"))
                if chunk_id not in seen:
                    seen.add(chunk_id)
                    found.append(hit)

        for keywords, sources in _TOPIC_SOURCES:
            if not any(word in lowered for word in keywords):
                continue
            for pattern in sources:
                chunks = self.retriever.chunks_by_source(pattern, limit=20)

                def overlap(hit: SearchHit) -> int:
                    text = str(hit.chunk.get("text") or "").lower()
                    head = text[:90]
                    score = sum(1 for term in terms if term in text)
                    # Совпадение с заголовком раздела важнее упоминания в тексте.
                    score += 3 * sum(1 for term in terms if term[:5] in head)
                    return score

                for hit in sorted(chunks, key=overlap, reverse=True):
                    if overlap(hit) == 0 and terms:
                        continue
                    chunk_id = str(hit.chunk.get("id"))
                    if chunk_id in seen:
                        continue
                    seen.add(chunk_id)
                    found.append(hit)
        return found[:2]

    def candidates(self, question: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Кандидаты поиска до сборки контекста — для контроля судьёй.

        Позволяет отличить провал поиска (факта нет в кандидатах) от провала
        отбора (факт есть, но не попал в контекст) и от провала генерации.
        """
        if _looks_like_injection(question):
            return []
        result: List[Dict[str, Any]] = []
        for hit in self._search_hits(question, max(limit, 6))[:limit]:
            text = str(hit.chunk.get("text") or "")
            result.append(
                {
                    "id": hit.chunk.get("id"),
                    "kind": hit.chunk.get("kind"),
                    "title": hit.chunk.get("title"),
                    "source": hit.chunk.get("source"),
                    "score": round(float(hit.score), 4),
                    "excerpt": _clip(text, 300),
                }
            )
        return result

    _PRODUCT_WORDS = ("ngfw", "waf", "dcfw", "swg", "siem", "client", "ucmc", "ugmc")
    _PLATFORM_RE = re.compile(
        r"\b(b50|c100|c150|c151|d200|d250|d500|e1000|e1010|e3000|e3010|"
        r"f8000|f8010|fg|x1|x10)\b",
        re.I,
    )

    def _drop_foreign_platforms(
        self, question: str, hits: Sequence[SearchHit]
    ) -> List[SearchHit]:
        """Вопрос про продукт не должен подмешивать даташиты платформ.

        Иначе сертификат или характеристики чужой модели попадают в ответ про
        WAF или SIEM: в даташитах те же слова «сертификат», «порты», «версия».
        """
        lowered = (question or "").lower()
        if self._PLATFORM_RE.search(lowered):
            return list(hits)
        if not any(word in lowered for word in self._PRODUCT_WORDS):
            return list(hits)
        filtered = [
            hit for hit in hits
            if "docs/hardware" not in str(hit.chunk.get("source") or "")
        ]
        return filtered or list(hits)

    def _search_hits(self, question: str, k: int) -> List[SearchHit]:
        """Четыре попытки до отказа: вопрос → редкий термин → подзапросы → слова."""
        hits = list(self.retriever.search(question, k=k))
        if not hits and self._news_excluded:
            # Ничего не нашли без новостей — разрешаем их как последний шанс.
            self.retriever.set_view([kind for kind in self._view_exclude("thinking") if kind != "news"])
            hits = list(self.retriever.search(question, k=k))

        # Вопросы о версиях: карточка версий важнее похожих по словам карточек FAQ.
        version_hits = self._version_hits(question)
        if version_hits:
            known_versions = {hit.chunk.get("id") for hit in version_hits}
            hits = version_hits + [hit for hit in hits if hit.chunk.get("id") not in known_versions]

        # Карточки-списки и карточка продукта: там таблицы и перечни.
        for extra in (
            self._enumeration_hits(question),
            self._product_card_hits(question),
            self._topic_hits(question),
        ):
            if not extra:
                continue
            known_extra = {hit.chunk.get("id") for hit in extra}
            for hit in extra:
                if "pinned" not in hit.why:
                    hit.why.append("pinned")
            hits = extra + [hit for hit in hits if hit.chunk.get("id") not in known_extra]

        # Точечная попытка по редкому термину: фрагмент обязан его содержать,
        # а определения ценим выше списков событий и настроек.
        for token in self._rare_probe_terms(question):
            candidates: Dict[str, tuple[int, SearchHit]] = {}
            for probe in (token, f"{token} позволяет", f"{token} используется"):
                for hit in self.retriever.search(probe, k=4):
                    text = str(hit.chunk.get("text") or "").lower()
                    if token not in text:
                        continue
                    weight = _definition_score(text, token)
                    chunk_id = str(hit.chunk.get("id"))
                    if chunk_id not in candidates or weight > candidates[chunk_id][0]:
                        candidates[chunk_id] = (weight, hit)
            if candidates:
                ranked = [
                    hit
                    for _weight, hit in sorted(
                        candidates.values(), key=lambda pair: pair[0], reverse=True
                    )
                ]
                known = {hit.chunk.get("id") for hit in hits}
                hits = [hit for hit in ranked[:2] if hit.chunk.get("id") not in known] + hits
                break

        if self._coverage(question, hits) >= 0.6:
            return hits[: max(k, 6)]

        # Декомпозиция: подзапросы по парам слов и по частям вопроса.
        seen_ids = {hit.chunk.get("id") for hit in hits}
        for probe in self._decomposition_probes(question):
            for hit in self.retriever.search(probe, k=3):
                if hit.chunk.get("id") in seen_ids:
                    continue
                seen_ids.add(hit.chunk.get("id"))
                hits.append(hit)

        probes: List[str] = []
        words = [term for term in query_terms(question) if len(term) >= 3]
        if words:
            probes.append(" ".join(words))
        for record in self.retriever.find_product(question, limit=1):
            name = str(record.get("name") or "").strip()
            if name:
                probes.append(f"{name} {' '.join(words)}")

        seen = {hit.chunk.get("id") for hit in hits}
        for probe in probes:
            if not probe.strip():
                continue
            for hit in self.retriever.search(probe, k=3):
                if hit.chunk.get("id") in seen:
                    continue
                seen.add(hit.chunk.get("id"))
                hits.append(hit)
            if self._coverage(question, hits) >= 0.6:
                break

        # Переранжирование: если термин стоит в начале фрагмента, это чаще
        # заголовок раздела или определение, а не упоминание в перечислении.
        terms = [term for term in query_terms(question) if len(term) >= 4]
        if terms:
            def lead_rank(hit: SearchHit) -> int:
                # Закреплённые фрагменты (карточки-списки, таблицы даташита)
                # не должны опускаться переранжированием по началу текста.
                if "pinned" in hit.why:
                    return -1000
                head = str(hit.chunk.get("text") or "")[:250].lower()
                return -sum(1 for term in terms if term in head)

            hits.sort(key=lead_rank)
        return hits[: max(k, 6)]

    # --- ссылки в тексте -------------------------------------------------
    def _sources_without_cited(
        self, sources: List[Dict[str, Any]], answer: str
    ) -> List[Dict[str, Any]]:
        """Убирает из списка источников те ссылки, что уже есть в тексте.

        Тестировщик заметил дублирование: адрес назван в ответе и повторён в
        блоке «Источники». Оставляем хотя бы один источник, чтобы блок не пустел.
        """
        if not sources:
            return sources

        unique: List[Dict[str, Any]] = []
        seen: set = set()
        for item in sources:
            key = _norm_url(str(item.get("url") or "")).split("#")[0]
            if not key:
                key = str(item.get("id") or item.get("title") or len(seen))
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)

        cited = [
            _norm_url(url).split("#")[0] for url in ANSWER_URL_RE.findall(answer or "")
        ]
        by_url = {
            _norm_url(str(item.get("url") or "")).split("#")[0]: item for item in unique
        }

        ordered: List[Dict[str, Any]] = []
        used: set = set()
        for url in cited:
            if len(ordered) >= 4:
                break
            if url in used:
                continue
            item = by_url.get(url)
            if item is not None:
                used.add(url)
                ordered.append(item)

        for item in unique:
            if len(ordered) >= 4:
                break
            if item not in ordered:
                ordered.append(item)

        # Приоритет: страница и цитируется в ответе, и совпадает с темой вопроса.
        cited_only = [
            item
            for item in ordered
            if _norm_url(str(item.get("url") or "")).split("#")[0] in used
        ]

        question = getattr(self, "_current_question", "") or ""
        tokens = {
            word.lower() for word in re.findall(r"[\w-]{5,}", question)
        } - {
            "какие", "какой", "какая", "каких", "сколько", "входит", "нужно",
            "можно", "расскажи", "подробнее", "поддерживаются", "отличается",
        }

        def relevant(item: Dict[str, Any]) -> bool:
            if not tokens:
                return True
            words = {
                word.lower()
                for word in re.findall(
                    r"[\w-]{5,}",
                    f"{item.get('title') or ''} {item.get('url') or ''}",
                )
            }
            return bool(tokens & words)

        by_topic = [item for item in ordered if relevant(item)]
        pool = (
            [item for item in by_topic if item in cited_only]
            or by_topic
            or cited_only
            or ordered
        )
        with_url = [
            item for item in pool if str(item.get("url") or "").startswith("http")
        ]
        return (with_url or pool)[:3]

    def _link_bare_hosts(
        self, answer: str, sources: Optional[Sequence[Dict[str, Any]]]
    ) -> str:
        """Делает кликабельными голые домены, если знаем адрес источника.

        Тестировщик справедливо заметил: «(static.usergate.com, стр. 14)» и
        «(docs.usergate.com)» в тексте не нажимаются. Если для этого хоста есть
        адрес в найденных источниках — превращаем упоминание в ссылку.
        """
        if not answer or not sources:
            return answer
        by_host: Dict[str, str] = {}
        for item in sources:
            url = str(item.get("url") or "")
            host = _url_host(url)
            if host and url.startswith("http"):
                by_host.setdefault(host.removeprefix("www."), url)
        if not by_host:
            return answer

        def repl(match: re.Match) -> str:
            host = match.group(1)
            url = by_host.get(host.removeprefix("www."))
            if not url:
                return match.group(0)
            return f"[{host}]({url})"

        pattern = re.compile(
            r"(?<![\w/.@-])((?:[a-z0-9-]+\.)+(?:com|ru|org|net|io))", re.I
        )
        return pattern.sub(repl, answer)

    def _attach_doc_links(
        self, answer: str, sources: Optional[Sequence[Dict[str, Any]]]
    ) -> str:
        """Если текст отсылает к документации, рядом должна стоять ссылка.

        Модель любит писать «порядок описан в документации:» и обрывать фразу.
        Тогда подставляем адрес подходящего источника из выдачи, а висящее
        двоеточие убираем.
        """
        if not answer:
            return answer
        links: List[str] = []
        for item in sources or []:
            url = str(item.get("url") or "")
            if not url.startswith("http"):
                continue
            kind = str(item.get("kind") or "")
            if kind in ("doc", "web", "product", "glossary", "about", "company") and url not in links:
                links.append(url)
        if not links:
            return answer

        # Разбиваем по предложениям, сохраняя разделители.
        parts = re.split(r"(?<=[.!?])\s+", answer)
        result: List[str] = []
        for part in parts:
            refers = _DOC_REF_RE.search(part)
            has_link = "http" in part or "](/" in part
            if refers and not has_link:
                if part.rstrip().endswith(":"):
                    part = part.rstrip()[:-1].rstrip() + f" — {links[0]}."
                else:
                    part = part.rstrip().rstrip(".") + f" ({links[0]})."
            result.append(part)
        text = " ".join(result)
        # Висящее двоеточие в конце ответа: либо ссылка, либо убираем.
        stripped = text.rstrip()
        if stripped.endswith(":"):
            text = stripped[:-1].rstrip() + f" — {links[0]}."
        return text

    # --- полнота перечислений -------------------------------------------
    def _complete_enumeration(
        self,
        question: str,
        answer: str,
        sources: Optional[Sequence[Dict[str, Any]]],
    ) -> str:
        """Дописывает элементы, которые есть в материале, но не попали в ответ.

        Только для вопросов-перечислений и только то, что буквально есть в
        найденных фрагментах: это цитата из источника, а не догадка.
        """
        if not answer or not sources or not _is_enumeration(question):
            return answer
        body = " ".join(str(item.get("excerpt") or "") for item in sources).lower()
        if not body:
            return answer
        lowered = answer.lower()
        missing: List[str] = []
        for item in _enumeration_items(body):
            if item in lowered:
                continue
            if any(item in seen or seen in item for seen in missing):
                continue
            missing.append(item)
        if not missing:
            return answer
        write_log(f"  · дополняю перечисление: {len(missing)} элемент(ов)")
        return answer.rstrip() + (
            "\n\nВ материалах также упомянуты: " + ", ".join(missing[:3]) + "."
        )

    # --- ссылки на источники -------------------------------------------
    def _load_source_links(self) -> Dict[str, str]:
        path = Path(self.settings.data_dir) / "company" / "source-links.json"
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        if not isinstance(payload, dict):
            return {}
        return {str(key): str(value) for key, value in payload.items() if value}

    def _link_for(self, source: str) -> str:
        """Публичная ссылка для материала: URL, если он есть, иначе карта файлов."""
        text = str(source or "").strip()
        if text.startswith(("http://", "https://")):
            return text
        link = self._source_links.get(text)
        if link:
            return link
        # Пути из индекса приходят с префиксом «company/», а карта собрана без него.
        marker = "company/"
        if marker in text:
            return self._source_links.get(text.split(marker, 1)[-1], "")
        return ""

    def _view_exclude(self, mode: str) -> List[str]:
        """Типы фрагментов, которые не ищем в этом режиме.

        Настройка в agent.json → retrieval.views (имя → исключённые kind) и
        retrieval.view_by_mode (режим → имя). Пусто — ищем по всей базе.
        """
        retrieval = self.profile.retrieval
        if not retrieval.views:
            return []
        name = retrieval.view_by_mode.get(mode) or retrieval.view
        return list(retrieval.views.get(name, []))

    def _wants_news(self, question: str) -> bool:
        text = (question or "").lower()
        return any(marker in text for marker in _NEWS_MARKERS)

    def _exclusions(self, mode: str, question: str) -> List[str]:
        """Типы фрагментов, которые не ищем. Новости — только по прямому запросу."""
        exclude = list(self._view_exclude(mode))
        if not self._wants_news(question) and "news" not in exclude:
            exclude.append("news")
        self._news_excluded = "news" in exclude
        return exclude

    def _resolve_mode(
        self,
        question: str,
        lang: str,
        usage_out: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str, str]:
        """Режим по сложности вопроса: (fast|thinking, объяснение, кто решил)."""
        fallback, reason = heuristic_mode(question)
        # Очевидные случаи решаем без отдельного запроса к модели — это быстрее.
        if reason in ("короткое приветствие", "пустой вопрос"):
            return fallback, reason, "эвристика"
        if not self.client or self.settings.is_local:
            return fallback, reason, "эвристика"
        # Совет/подбор без параметров — повод для опроса, даже если назван
        # продукт или слово «курс». Фактовые вопросы решает эвристика.
        advice = bool(
            re.search(
                r"посовет|подбер|подобр|подбор|подскаж|помог|определ|не могу|не знаю|что выбрать|выбрать|нужен совет|хочу|с чего начать",
                question,
                re.I,
            )
        ) and len(question.split()) <= 18
        factual = bool(
            re.search(r"^(?:что такое|сколько стоит|какие версии|кто такой|где находится|какой сертификат)", question, re.I)
        )
        if advice and not factual:
            cache_key = f"{lang}|{question.strip().lower()}"
            cached = self._mode_cache.get(cache_key)
            if cached is not None:
                return cached
            try:
                quick_prompt = (
                    "Ты решаешь, нужен ли уточняющий опрос. Ответь одним словом:\n"
                    "CLARIFY — клиент просит помочь выбрать/подобрать/посоветовать продукт или обучение,\n"
                    "но не назвал параметры (что защищать, уровень, формат, бюджет, сроки);\n"
                    "FAST — вопрос про конкретный названный продукт, версию, цену или факт, ответ можно дать сразу.\n"
                    "Без пояснений."
                )
                parts: List[str] = []
                usage: Dict[str, Any] = {}
                for event in self.client.stream_chat(
                    [
                        {"role": "system", "content": quick_prompt},
                        {"role": "user", "content": question},
                    ],
                    None,
                    allow_thinking=False,
                    max_tokens=64,
                ):
                    if getattr(event, "type", "") == "delta":
                        parts.append(getattr(event, "text", "") or "")
                    elif getattr(event, "type", "") == "done" and getattr(event, "usage", None):
                        usage = event.usage
                parsed = parse_mode("".join(parts))
                if parsed:
                    if usage_out is not None:
                        usage_out.update(usage)
                    result = (parsed, "модель уточнила формат запроса", "модель")
                    if len(self._mode_cache) > 256:
                        self._mode_cache.clear()
                    self._mode_cache[cache_key] = result
                    return result
            except Exception:  # noqa: BLE001
                pass
            return "clarify", "запрос на подбор без параметров", "эвристика"
        return fallback, reason, "эвристика"

    # --- ответ ----------------------------------------------------------
    def run(
        self,
        question: str,
        history: Optional[Sequence[Dict[str, Any]]] = None,
        show_notes: bool = True,
        use_cache: bool = True,
        mode: str = "thinking",
    ) -> Iterator[Dict[str, Any]]:
        question = (question or "").strip()
        if not question:
            yield {"type": "error", "message": "Пустой запрос"}
            return

        requested = str(mode).lower()
        if requested not in ("auto", "fast", "thinking", "direct"):
            requested = "auto"
        lang = detect_lang(question)
        # Клиент русскоязычный: по умолчанию отвечаем по-русски, даже если
        # вопрос задан по-английски. Исключение — явная просьба о другом языке.
        if not _wants_other_language(question):
            lang = "ru"
        auto = requested == "auto"
        direct = requested == "direct"
        mode_usage: Dict[str, Any] = {}
        if auto:
            mode, decision, decided_by = self._resolve_mode(
                question, lang, usage_out=mode_usage
            )
        elif direct:
            mode, decision, decided_by = "thinking", "ответ после уточнения", "система"
        else:
            mode = "fast" if requested == "fast" else "thinking"
            decision = "режим выбран вручную"
            decided_by = "пользователь"
        # Режим просмотра базы: «кратко» не ищет по тяжёлой документации.
        # Там же включаем чистку выдачи от повторов: одна и та же статья лежит
        # в деревьях разных продуктов и иначе занимает весь контекст.
        self.retriever.set_view(self._exclusions(mode, question))
        retrieval = self.profile.retrieval
        self.retriever.set_dedupe(
            max_per_doc=retrieval.max_per_doc,
            threshold=retrieval.dedupe_threshold,
            enabled=retrieval.dedupe,
        )
        self.retriever.set_kind_weights(retrieval.kind_weights)
        self.retriever.set_channel_weights(retrieval.channel_weights)
        # Документация идёт во вторую очередь: карточки отвечают точнее.
        self.retriever.set_secondary_kinds(retrieval.secondary_kinds)
        yield {
            "type": "start",
            "mode": "api" if self.client else "demo",
            "answer_mode": mode,
            "requested_mode": requested,
            "auto": auto,
            "complexity": decision,
            "decided_by": decided_by,
            "lang": lang,
            "model": self.settings.effective_model if self.client else "retrieval-only",
            "thinking": bool(self.client and self.client.thinking_supported and mode == "thinking"),
            "notes": bool(show_notes),
            "company": self.company,
        }

        context_key = self._context_key(history)
        if self.cache is not None and use_cache and self.settings.answer_cache:
            try:
                hit = self.cache.lookup(
                    question,
                    show_notes=show_notes,
                    mode=mode,
                    lang=lang,
                    context_key=context_key,
                )
            except Exception:  # noqa: BLE001
                hit = None
            if hit:
                yield from self._rechecked_answer(
                    hit,
                    question,
                    history,
                    show_notes=show_notes,
                    mode=mode,
                    lang=lang,
                )
                return

        if not self.client:
            yield from self._run_offline(question, lang)
            return

        self._apply_audience_weights(show_notes)

        if mode == "clarify":
            yield from self._run_clarification(
                question, lang, history, show_notes, base_usage=mode_usage
            )
            return

        if direct:
            yield from self._run_single(
                question, lang, history, show_notes, mode, direct=True,
                context_key=context_key, base_usage=mode_usage,
            )
            return

        single_call = mode in {"fast", "auto"} or self.settings.is_local
        if single_call:
            yield from self._run_single(
                question, lang, history, show_notes, mode, direct=direct,
                context_key=context_key, base_usage=mode_usage,
            )
            return

        yield from self._run_agent(
            question, lang, history, show_notes, mode, context_key=context_key,
            base_usage=mode_usage,
        )

    def _run_clarification(
        self,
        question: str,
        lang: str,
        history: Optional[Sequence[Dict[str, Any]]],
        show_notes: bool,
        base_usage: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Один короткий вызов: получить у клиента недостающий параметр."""
        self._current_question = question
        ask_tool = next(
            (
                tool
                for tool in (self.tools or [])
                if tool["function"]["name"] == "ask_clarification"
            ),
            None,
        )
        if ask_tool is None or self.client is None:
            yield from self._run_agent(
                question, lang, history, show_notes, "thinking",
                base_usage=base_usage,
            )
            return

        context, _ = self._auto_context(
            question, show_notes=False, catalog=True
        )
        context = _clip(context, 2400)
        system = (
            f"Ты — {self.profile.persona.role} компании «{self.company}». "
            "Представь, что ты сотрудник компании, который консультирует клиента. "
            "Клиент задал вопрос или попросил действие, но для точной рекомендации "
            "не хватает информации. Задай столько вопросов, сколько реально нужно для "
            "рекомендации: минимум 1, желательно 3, максимум 10. Если достаточно одного "
            "вопроса — задай один, не добирай количество ради формы. "

            "Не спрашивай то, что уже известно. "
            "Вызови ask_clarification; у каждого вопроса 2–3 конкретных варианта, свой вариант клиент введёт сам. "
            "Опирайся на материалы компании: не добавляй направления, услуги и технологии, "
            "которых нет в справке. Не отвечай на исходный вопрос сейчас."
        )
        if context:
            system += "\n\n" + context
        messages: List[Dict[str, Any]] = [{"role": "system", "content": system}]
        messages.extend(self._prepare_history(history))
        messages.append({"role": "user", "content": question})

        yield {"type": "step", "n": 1, "max": 1, "title": "Уточняю пару деталей…"}
        calls: List[ToolCall] = []
        usage: Dict[str, Any] = {}
        for event in self.client.stream_chat(
            messages, [ask_tool], allow_thinking=False, max_tokens=1400
        ):
            if event.type == "tool_calls":
                calls = event.tool_calls
            elif event.type == "done":
                usage = event.usage or usage

        for call in calls:
            if call.name != "ask_clarification":
                continue
            try:
                args = json.loads(call.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            if not isinstance(args, dict):
                args = {}
            clarification = _clean_clarification(args)
            if not clarification:
                continue
            tool_entry = {
                "name": call.name,
                "arguments": args,
                "reason": str(args.get("reason") or ""),
                "summary": "уточняющий вопрос клиенту",
            }
            total_usage = _empty_usage()
            _merge_usage(total_usage, base_usage)
            _merge_usage(total_usage, usage)
            yield {"type": "clarification", **clarification}
            yield {
                "type": "done",
                "text": clarification.get("summary") or clarification["question"],
                "reasoning": "",
                "plan": None,
                "steps": 1,
                "usage": usage,
                "usage_total": total_usage,
                "sources": [],
                "attachments": [],
                "tool_calls": [tool_entry],
                "followups": [],
                "clarification": clarification,
                "cached": False,
                "mode": "clarify",
            }
            return

        # Модель не вернула уточнение — отвечаем обычным путём.
        yield from self._run_agent(
            question, lang, history, show_notes, "thinking",
            base_usage=base_usage,
        )


    def _apply_audience_weights(self, staff: bool) -> None:
        """Сотрудникам — упор на BM25, клиентам — на векторный поиск."""
        try:
            self.retriever.set_channel_weights(
                {"bm25": 1.9, "dense": 1.0} if staff else {"bm25": 1.0, "dense": 1.7}
            )
        except Exception:  # noqa: BLE001
            pass

    def _run_single(
        self,
        question: str,
        lang: str,
        history: Optional[Sequence[Dict[str, Any]]],
        show_notes: bool,
        mode: str,
        direct: bool = False,
        context_key: str = "",
        base_usage: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        query = question
        if direct and history:
            previous = next(
                (
                    str(item.get("content") or "").strip()
                    for item in reversed(history)
                    if item.get("role") == "user" and item.get("content")
                ),
                "",
            )
            if previous and previous not in query:
                query = f"{previous}\n{question}"
        context, context_sources = self._auto_context(
            query, show_notes, hits=5 if direct else None, catalog=direct
        )
        if direct:
            prompt = build_system_prompt(
                self.stats, self.profile, lang=lang, include_tools=False
            )
            prompt += (
                "\n\nКлиент уже ответил на уточняющие вопросы. Не задавай новых вопросов. "
                "Дай полноценную рекомендацию связным текстом, как консультант: короткий заголовок `##`, "
                "2–3 коротких абзаца через пустую строку и **жирные акценты** на ключевых фактах. "
                "Список или таблицу используй только при сравнении нескольких вариантов или для шагов. "
                "Называй конкретные факты из контекста и ссылайся на найденные источники: "
                "если подходящие данные там есть, используй их и не утверждай, что сведений нет. "
                "Не добавляй то, чего нет в контексте. "
                "Не сокращай ответ ради экономии."
            )
        else:
            prompt = build_fast_prompt(
                context, self.profile, lang=lang, show_notes=show_notes
            )
        messages: List[Dict[str, Any]] = [{"role": "system", "content": prompt}]
        messages.extend(self._prepare_history(history))
        messages.append(
            {
                "role": "user",
                "content": f"{question}\n{context}" if context else question,
            }
        )

        max_tokens = (
            1200
            if direct
            else self.profile.limits.local_max_tokens
            if self.settings.is_local
            else self.profile.limits.fast_max_tokens
        )
        yield {"type": "step", "n": 1, "max": 1}

        answer_parts: List[str] = []
        usage: Dict[str, Any] = {}
        for event in self.client.stream_chat(  # type: ignore[union-attr]
            messages, None, allow_thinking=direct, max_tokens=max_tokens
        ):
            if event.type == "delta":
                chunk = sanitize_text(event.text, lang)
                answer_parts.append(chunk)
                yield {"type": "delta", "text": chunk}
            elif event.type == "done":
                usage = event.usage or usage

        answer = sanitize_text("".join(answer_parts).strip(), lang)
        if not answer:
            answer = self._retry_answer(question, context, lang)
        if not answer:
            # Модель промолчала: отдаём честный ответ по найденным источникам,
            # а не «уточните вопрос».
            answer = self._no_data_answer(question, context_sources, lang)
        answer = answer or fallback_text(lang)
        answer = self._verified_answer(answer, context_sources)
        answer = self._attach_doc_links(answer, context_sources)
        answer = self._link_bare_hosts(answer, context_sources)
        answer = _footnote_links(answer)
        if not show_notes:
            answer = _client_text(answer)
        # Финальная нормализация — после всех правок текста: любая из них могла
        # склеить строки таблицы, а рендерер разбирает её построчно.
        answer = _structure_answer(answer)
        answer = _normalize_tables(answer)
        followups = (
            self._suggest_followups(
                question, answer, context_sources, staff=show_notes, lang=lang
            )
            if self._should_offer_followups(question, answer)
            else []
        )
        usage_total = _empty_usage()
        _merge_usage(usage_total, base_usage)
        _merge_usage(usage_total, usage)
        # Источники отдаём всегда: по условиям кейса ссылки на материалы обязательны.
        # Клиентский режим убирает размышления и шаги, но не происхождение фактов.
        if context_sources:
            yield {"type": "sources", "items": _official_sources(self._sources_without_cited(list(context_sources), answer))}

        # В кеш попадают только дорогие ответы: экономия должна быть заметной.
        if (
            self.cache is not None
            and self.settings.answer_cache
            and int(usage_total.get("total_tokens") or 0)
            >= self.settings.answer_cache_min_tokens
        ):
            try:
                self.cache.store(
                    question,
                    answer,
                    sources=context_sources,
                    show_notes=show_notes,
                    model=self.settings.effective_model,
                    tokens=int(usage_total.get("total_tokens") or 0),
                    mode=mode,
                    lang=lang,
                    context_key=context_key,
                )
            except Exception:  # noqa: BLE001
                pass

        yield {
            "type": "done",
            "text": _finalize(answer, context_sources, show_notes),
            "reasoning": "",
            "plan": None,
            "steps": 1,
            "usage": usage,
            "usage_total": usage_total,
            "sources": _official_sources(self._sources_without_cited(list(context_sources), answer)),
            "attachments": [],
            "tool_calls": [],
            "followups": _with_suggestions(self.client, question, answer, _filter_followups(followups, question, answer) or _fallback_followups(answer)),
            "cached": False,
            "mode": mode,
        }

    def _run_agent(
        self,
        question: str,
        lang: str,
        history: Optional[Sequence[Dict[str, Any]]],
        show_notes: bool,
        mode: str,
        context_key: str = "",
        base_usage: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        context, context_sources = self._auto_context(question, show_notes)
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": build_system_prompt(self.stats, self.profile, lang=lang),
            }
        ]
        messages.extend(self._prepare_history(history))
        messages.append(
            {"role": "user", "content": f"{question}\n{context}" if context else question}
        )

        answer_parts: List[str] = []
        early_parts: List[str] = []
        reasoning_parts: List[str] = []
        sources: Dict[str, Dict[str, Any]] = {
            item["id"]: item for item in context_sources if item.get("id")
        }
        tool_log: List[Dict[str, Any]] = []
        plan: Optional[Dict[str, Any]] = None
        followups: List[str] = []
        clarification: Optional[Dict[str, Any]] = None
        usage_total = _empty_usage()
        _merge_usage(usage_total, base_usage)
        usage: Dict[str, Any] = {}
        step = 0

        try:
            max_steps = self.profile.limits.max_steps
            for step in range(1, max_steps + 1):
                yield {"type": "step", "n": step, "max": max_steps}
                text_parts: List[str] = []
                calls: List[ToolCall] = []
                step_usage: Dict[str, Any] = {}
                finish_reason = ""

                for event in self.client.stream_chat(messages, self.tools or None):  # type: ignore[union-attr]
                    if event.type == "delta":
                        chunk = sanitize_text(event.text, lang)
                        text_parts.append(chunk)
                        yield {"type": "delta", "text": chunk}
                    elif event.type == "reasoning":
                        reasoning_parts.append(event.text)
                        if show_notes:
                            yield {"type": "reasoning_delta", "text": event.text}
                    elif event.type == "tool_calls":
                        calls = event.tool_calls
                    elif event.type == "done":
                        step_usage = event.usage or step_usage
                        usage = step_usage or usage
                        finish_reason = event.finish_reason or finish_reason

                _merge_usage(usage_total, step_usage)

                step_text = "".join(text_parts).strip()
                if not calls:
                    answer_parts.append(step_text)
                    break
                if step_text:
                    early_parts.append(step_text)

                messages.append(
                    {
                        "role": "assistant",
                        "content": "".join(text_parts),
                        "tool_calls": [
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {"name": call.name, "arguments": call.arguments},
                            }
                            for call in calls
                        ],
                    }
                )

                for call in calls:
                    args = {}
                    try:
                        args = json.loads(call.arguments or "{}")
                    except json.JSONDecodeError:
                        pass
                    reason = str((args or {}).get("reason") or "") if isinstance(args, dict) else ""
                    if call.name == "ask_clarification":
                        outcome = self._execute(call, question)
                        clar = outcome.get("clarification")
                        if clar:
                            clarification = clar
                            tool_log.append(
                                {
                                    "name": call.name,
                                    "arguments": args if isinstance(args, dict) else {},
                                    "reason": reason,
                                    "summary": outcome.get("summary", ""),
                                }
                            )
                            break
                    if show_notes:
                        yield {
                            "type": "tool_call",
                            "id": call.id,
                            "name": call.name,
                            "arguments": args if isinstance(args, dict) else {},
                            "reason": reason,
                        }
                    outcome = self._execute(call, question)
                    if call.name == "offer_followups":
                        followups = _clean_followups(
                            (outcome.get("result") or {}).get("items")
                        )
                    summary = outcome.get("summary", "")
                    for source in outcome.get("sources", []):
                        key = source.get("id") or source.get("source") or summary
                        sources[str(key)] = source
                    tool_log.append(
                        {
                            "name": call.name,
                            "arguments": args if isinstance(args, dict) else {},
                            "reason": reason,
                            "summary": summary,
                        }
                    )
                    if call.name == "plan" and outcome.get("plan"):
                        plan = outcome["plan"]
                        if show_notes:
                            yield {"type": "plan", **plan}
                    if show_notes:
                        yield {
                            "type": "tool_result",
                            "id": call.id,
                            "name": call.name,
                            "summary": summary,
                            "sources": outcome.get("sources", [])[:6],
                            "attachments": [],
                        }
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(
                                _strip_source_keys(outcome.get("result", {}))
                                if not show_notes
                                else outcome.get("result", {}),
                                ensure_ascii=False,
                            )[:6000],
                        }
                    )
                if clarification:
                    break
                if sources:
                    # Источники нужны в любом режиме: по условиям кейса ссылки обязательны.
                    yield {"type": "sources", "items": _official_sources(self._sources_without_cited(list(sources.values()), locals().get("text") or locals().get("answer") or ""))}
            else:
                yield {"type": "step", "n": max_steps, "max": max_steps}
                messages.append(
                    {
                        "role": "user",
                        "content": "Ответь по уже собранным данным, без новых инструментов.",
                    }
                )
                final_usage: Dict[str, Any] = {}
                for event in self.client.stream_chat(messages, None):
                    if event.type == "delta":
                        chunk = sanitize_text(event.text, lang)
                        answer_parts.append(chunk)
                        yield {"type": "delta", "text": chunk}
                    elif event.type == "done":
                        final_usage = event.usage or final_usage
                _merge_usage(usage_total, final_usage)

            final_answer = "".join(answer_parts).strip()
            early_answer = "\n\n".join(early_parts).strip()
            if early_answer and (not final_answer or len(final_answer) < 220):
                answer = early_answer
                if final_answer and final_answer not in early_answer:
                    answer = f"{early_answer}\n\n{final_answer}"
            else:
                answer = final_answer or early_answer
            answer = sanitize_text(answer.strip(), lang) or fallback_text(lang)
            answer = self._verified_answer(answer, list(sources.values()))
            answer = ensure_official_url(answer, question, self._source_texts)
            answer = self._attach_doc_links(answer, list(sources.values()))
            if not show_notes:
                answer = _client_text(answer)
            followups = self._review_followups(
                followups, question, answer, list(sources.values()),
                staff=show_notes, lang=lang,
            )
            # Модель иногда даёт одну удачную кнопку из четырёх: добираем план
            # из базы, не повторяя уже одобренное.
            if len(followups) < 2 and self._should_offer_followups(question, answer):
                followups = self._suggest_followups(
                    question, answer, list(sources.values()),
                    staff=show_notes, lang=lang, keep=followups,
                )
            reasoning = "".join(reasoning_parts).strip()
            if plan:
                plan_text = "\n".join(
                    f"{index}. {item}" for index, item in enumerate(plan.get("steps", []), start=1)
                )
                reasoning = (f"План:\n{plan_text}" + (f"\n\n{reasoning}" if reasoning else "")).strip()

            if clarification:
                yield {"type": "clarification", **clarification}
                yield {
                    "type": "done",
                    "text": clarification.get("summary") or clarification["question"],
                    "reasoning": reasoning,
                    "plan": plan,
                    "steps": step,
                    "usage": usage,
                    "usage_total": usage_total,
                    "sources": _official_sources(self._sources_without_cited(list(sources.values()), answer)),
                    "attachments": [],
                    "tool_calls": tool_log,
                    "followups": [],
                    "clarification": clarification,
                    "cached": False,
                    "mode": mode,
                }
                return

            # В кеш попадают только дорогие ответы: экономия должна быть заметной.
            if (
                self.cache is not None
                and self.settings.answer_cache
                and answer
                and int(usage_total.get("total_tokens") or 0)
                >= self.settings.answer_cache_min_tokens
            ):
                try:
                    self.cache.store(
                        question,
                        answer,
                        reasoning=reasoning,
                        sources=list(sources.values()),
                        tool_calls=tool_log,
                        show_notes=show_notes,
                        model=self.settings.effective_model,
                        tokens=int(usage_total.get("total_tokens") or 0),
                        mode=mode,
                        lang=lang,
                        context_key=context_key,
                    )
                except Exception:  # noqa: BLE001
                    pass

            yield {
                "type": "done",
                "text": _finalize(answer, context_sources, show_notes),
                "reasoning": reasoning,
                "plan": plan,
                "steps": step,
                "usage": usage,
                "usage_total": usage_total,
                "sources": _official_sources(self._sources_without_cited(list(sources.values()), answer)),
                "attachments": [],
                "tool_calls": tool_log,
                "followups": _with_suggestions(self.client, question, answer, _filter_followups(followups, question, answer) or _fallback_followups(answer)),
                "cached": False,
                "mode": mode,
            }
        except LLMError as exc:
            yield {"type": "error", "message": str(exc), "status": exc.status}
        except Exception as exc:  # noqa: BLE001
            yield {"type": "error", "message": f"{type(exc).__name__}: {exc}"}

    def _cached_answer(
        self, hit: Dict[str, Any], show_notes: bool = True
    ) -> Iterator[Dict[str, Any]]:
        answer = sanitize_text(
            hit.get("answer") or "", str(hit.get("lang") or "")
        )
        answer = _normalize_tables(answer)
        if not show_notes:
            answer = _client_text(answer)
        answer = _normalize_tables(answer)
        cached_sources = list(hit.get("sources") or [])
        cached_question = str(hit.get("question") or "")
        cached_lang = str(hit.get("lang") or "ru")
        followups = self._review_followups(
            _followups_from_calls(hit.get("tool_calls")),
            cached_question, answer, cached_sources,
            staff=show_notes, lang=cached_lang,
        )
        if len(followups) < 2 and self._should_offer_followups(cached_question, answer):
            followups = self._suggest_followups(
                cached_question, answer, cached_sources,
                staff=show_notes, lang=cached_lang, keep=followups,
            )
        sources = cached_sources
        yield {
            "type": "cache",
            "hit": True,
            "question": hit.get("question"),
            "similarity": hit.get("similarity"),
            "exact": bool(hit.get("exact")),
        }
        if sources:
            yield {"type": "sources", "items": _official_sources(self._sources_without_cited(list(sources), locals().get("text") or locals().get("answer") or ""))}
        for start in range(0, len(answer), max(1, len(answer) // 20)):
            yield {
                "type": "delta",
                "text": sanitize_text(
                    answer[start:start + max(1, len(answer) // 20)],
                    str(hit.get("lang") or ""),
                ),
            }
        yield {
            "type": "done",
            "text": _finalize(answer, sources, show_notes),
            "reasoning": hit.get("reasoning") or "",
            "plan": None,
            "steps": 0,
            "usage": {},
            "usage_total": {},
            "sources": _official_sources(self._sources_without_cited(list(sources), locals().get("text") or locals().get("answer") or "")),
            "attachments": [],
            "tool_calls": hit.get("tool_calls") or [],
            "followups": _with_suggestions(self.client, cached_question, answer, _filter_followups(followups, cached_question, answer) or _fallback_followups(answer)),
            "cached": True,
            "mode": hit.get("kb_stamp", "").split("|")[-1] or "thinking",
        }

    def _retry_answer(self, question: str, context: str, lang: str) -> str:
        """Один короткий повтор, если модель вернула пустой ответ.

        Тестировщик получил «Не удалось сформулировать ответ» на сложный вопрос
        про обход DPI. Вместо отказа пробуем ещё раз с простой инструкцией.
        """
        if not self.client:
            return ""
        prompt = build_system_prompt(
            self.stats, self.profile, lang=lang, include_tools=False
        )
        prompt += (
            "\n\nОтветь коротко и по делу: 2–4 абзаца, только факты из контекста. "
            "Если фактов нет — скажи, что в материалах этого нет, и предложи канал связи."
        )
        messages: List[Dict[str, Any]] = [{"role": "system", "content": prompt}]
        messages.append(
            {"role": "user", "content": f"{question}\n{context}" if context else question}
        )
        parts: List[str] = []
        try:
            for event in self.client.stream_chat(
                messages, None, allow_thinking=False, max_tokens=900
            ):
                if event.type == "delta":
                    parts.append(event.text)
        except Exception:  # noqa: BLE001
            return ""
        return sanitize_text("".join(parts).strip(), lang)

    def _no_data_answer(
        self, question: str, sources: Sequence[Dict[str, Any]], lang: str = "ru"
    ) -> str:
        """Честный ответ, когда модель не смогла сформулировать текст.

        Уточнять вопрос бессмысленно, если данных нет: говорим прямо и даём канал.
        """
        if lang == "en":
            return (
                "There are no details on this in UserGate's public materials. "
                "The exact answer is confirmed by the company: sales@usergate.com."
            )
        return (
            "В открытых материалах UserGate этого нет: описание по такому сценарию "
            "не публикуется, поэтому обещать конкретные механизмы нельзя.\n\n"
            "Точный ответ по вашей задаче подтверждает компания — sales@usergate.com."
        )

    def _rechecked_answer(
        self,
        hit: Dict[str, Any],
        question: str,
        history: List[Dict[str, Any]],
        *,
        show_notes: bool,
        mode: str,
        lang: str,
    ) -> Iterator[Dict[str, Any]]:
        """Кеш отдаём через модель: сохранённый ответ адаптируется к диалогу."""
        cached = sanitize_text(hit.get("answer") or "", str(hit.get("lang") or lang))
        sources = list(hit.get("sources") or [])
        if not cached or not self.settings.answer_cache_recheck or not self.client:
            yield from self._cached_answer(hit, show_notes=show_notes)
            return

        prompt = build_system_prompt(
            self.stats, self.profile, lang=lang, include_tools=False
        )
        prompt += (
            "\n\nНиже — ответ, ранее сохранённый в кеше для похожего вопроса. "
            "Перепиши его для текущего диалога: сохрани все факты, цифры и ссылки, "
            "убери то, что не относится к уточнениям пользователя, и не добавляй новых фактов. "
            "Если вопрос изменился по смыслу — ответь по существу, опираясь только на этот ответ."
        )
        messages: List[Dict[str, Any]] = [{"role": "system", "content": prompt}]
        messages.extend(self._prepare_history(history))
        messages.append(
            {
                "role": "user",
                "content": f"Вопрос: {question}\n\nСохранённый ответ:\n{cached}",
            }
        )

        yield {
            "type": "cache",
            "hit": True,
            "question": hit.get("question"),
            "similarity": hit.get("similarity"),
            "exact": bool(hit.get("exact")),
            "rechecked": True,
        }
        if sources:
            yield {"type": "sources", "items": _official_sources(self._sources_without_cited(list(sources), locals().get("text") or locals().get("answer") or ""))}

        parts: List[str] = []
        usage: Dict[str, Any] = {}
        try:
            for event in self.client.stream_chat(  # type: ignore[union-attr]
                messages, None, allow_thinking=False, max_tokens=self.settings.max_tokens
            ):
                if event.type == "delta":
                    chunk = sanitize_text(event.text, lang)
                    parts.append(chunk)
                    yield {"type": "delta", "text": chunk}
                elif event.type == "done":
                    usage = event.usage or usage
        except Exception:  # noqa: BLE001
            if not parts:
                yield from self._cached_answer(hit, show_notes=show_notes)
                return

        text = sanitize_text("".join(parts).strip(), lang)
        if not text:
            yield from self._cached_answer(hit, show_notes=show_notes)
            return
        text = self._verified_answer(text, sources)
        text = _footnote_links(text)
        text = _structure_answer(text)
        if not show_notes:
            text = _client_text(text)
        followups = self._review_followups(
            _followups_from_calls(hit.get("tool_calls")),
            question,
            text,
            sources,
            staff=show_notes,
            lang=lang,
        )
        yield {
            "type": "done",
            "text": _finalize(text, sources, show_notes),
            "reasoning": "",
            "plan": None,
            "steps": 0,
            "usage": usage,
            "usage_total": usage,
            "sources": _official_sources(self._sources_without_cited(list(sources), locals().get("text") or locals().get("answer") or "")),
            "attachments": [],
            "tool_calls": hit.get("tool_calls") or [],
            "followups": _with_suggestions(self.client, question, text, _filter_followups(followups, question, text) or _fallback_followups(text)),
            "cached": True,
            "rechecked": True,
            "mode": mode,
        }

    def _run_offline(self, question: str, lang: str) -> Iterator[Dict[str, Any]]:
        hits = self.retriever.search(question, k=3)
        sources = [hit.to_source() for hit in hits]
        if sources:
            lines = [
                f"**{item['title']}** ({item['source']})\n{item['excerpt']}" for item in sources
            ]
            text = "Нашёл в базе знаний:\n\n" + "\n\n".join(lines)
        else:
            text = fallback_text(lang)
        yield {"type": "tool_call", "id": "offline-search", "name": "search_knowledge", "arguments": {"query": question}, "reason": ""}
        yield {"type": "tool_result", "id": "offline-search", "name": "search_knowledge", "summary": f"фрагментов: {len(hits)}", "sources": _official_sources(self._sources_without_cited(list(sources), locals().get("text") or locals().get("answer") or "")), "attachments": []}
        if sources:
            yield {"type": "sources", "items": _official_sources(self._sources_without_cited(list(sources), locals().get("text") or locals().get("answer") or ""))}
        yield {"type": "delta", "text": text}
        yield {
            "type": "done",
            "text": _finalize(text, sources, False),
            "reasoning": "",
            "plan": None,
            "steps": 1,
            "usage": {},
            "usage_total": _empty_usage(),
            "sources": _official_sources(self._sources_without_cited(list(sources), locals().get("text") or locals().get("answer") or "")),
            "attachments": [],
            "tool_calls": [{"name": "search_knowledge", "arguments": {"query": question}, "summary": f"фрагментов: {len(hits)}"}],
            "followups": [],
            "cached": False,
            "mode": "demo",
        }

    @staticmethod
    def _prepare_history(history: Optional[Sequence[Dict[str, Any]]]) -> List[Dict[str, str]]:
        if not history:
            return []
        cleaned: List[Dict[str, str]] = []
        for item in history[-MAX_HISTORY_MESSAGES:]:
            role = item.get("role")
            content = str(item.get("content") or "").strip()
            if role not in ("user", "assistant") or not content:
                continue
            cleaned.append({"role": role, "content": _clip(content, 2000)})
        return cleaned

_PUBLIC_BY_PATH = {
    "faq/education.md": "https://usergate.com/academy",
    "faq/pricing.md": "https://usergate.com/purchase",
    "faq/products.md": "https://usergate.com/products",
    "faq/company.md": "https://usergate.com/about",
    "faq/contacts.md": "https://usergate.com/contacts",
    "about/academy.md": "https://usergate.com/academy",
}


def _public_url_for(source: str) -> str:
    value = str(source or "").replace("\\", "/").strip()
    for key, url in _PUBLIC_BY_PATH.items():
        if value.endswith(key):
            return url
    if value.startswith("faq/"):
        return "https://usergate.com/academy"
    if value.startswith(("about/", "docs/")):
        return "https://usergate.com/"
    return ""


def _official_facts_text() -> str:
    """Текст курированных официальных фрагментов (delta)."""
    path = Path(__file__).resolve().parents[1] / "storage/index/delta/chunks.jsonl"
    if not path.exists():
        return ""
    parts = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = str(item.get("text") or "")
        if "ОФИЦИАЛЬНЫЕ ДАННЫЕ" in text:
            parts.append(text)
    return " ".join(parts)


def ensure_official_url(answer: str, question: str, source_texts: dict) -> str:
    """Если спрашивали адрес, добавляем проверенный URL и код из фактов."""
    low = (question or "").lower()
    if not any(word in low for word in ("адрес", "ссылк", "url")):
        return answer
    facts = " ".join(str(value) for value in (source_texts or {}).values())
    facts = (facts + " " + _official_facts_text()).strip()
    found = ANSWER_URL_RE.findall(facts)
    if not found:
        return answer
    preferred = [
        url for url in found
        if "sertificirovannyj-professional-ngfw" in url or "11973" in url
    ]
    if preferred and preferred[0].split("//")[-1].rstrip("/") in answer:
        return answer
    url = preferred[0] if preferred else found[0]
    lines = []
    if "UG.SUMMA7.EC.1" in facts and "UG.SUMMA7.EC.1" not in answer:
        lines.append("Экзамен UG.SUMMA7.EC.1 «Сертифицированный специалист SUMMA».")
    lines.append(f"Адрес страницы: {url}")
    return answer.rstrip() + "\n\n" + "\n".join(lines)


def _official_sources(items) -> list:
    """Официальные домены, без дублей по URL, каждому — публичный адрес."""
    seen = set()
    unique = []
    for item in items or []:
        url = str(item.get("url") or "")
        key = url.split("#")[0].rstrip("/")
        if key and key in seen:
            continue
        seen.add(key)
        if not url.startswith("http"):
            fallback = _public_url_for(str(item.get("source") or ""))
            if not fallback:
                kind = str(item.get("kind") or "")
                fallback = (
                    "https://usergate.com/academy"
                    if kind == "faq"
                    else "https://usergate.com/"
                )
            item["url"] = fallback
        unique.append(item)
    official = [i for i in unique if "usergate.com" in str(i.get("url") or "").lower()]
    pool = official or unique
    with_url = [i for i in pool if str(i.get("url") or "").startswith("http")]
    return (with_url or pool)[:3]


def _clean_dangling(text: str) -> str:
    """Убирает оборванные фразы, чинит адреса и незакрытые ** по строкам."""
    original = str(text or "")
    value = original
    value = re.sub(r"\b(на|в|по)\s*[—:-]\s*это\s+официальн\w+\s+путь[^.]*\.?", "", value, flags=re.I)
    value = re.sub(r"\b(каталог|ссылка|адрес)\s*[—-]\s*[.,;:]?\s*$", r"\1.", value, flags=re.I)
    value = re.sub(r"\s*,\s*,", ",", value)
    value = re.sub(r"\bс\s*,", "с", value)
    value = re.sub(r"\bи\s*,", "и", value)
    # Адрес: «д. 1. 32А» → «д. 1.32А».
    value = re.sub(r"\bд\.?\s*(\d+)\.\s*(\d+)", r"д. \1.\2", value)
    # Незакрытый жирный маркер внутри строки — снимаем его.
    fixed_lines = []
    for line in value.splitlines():
        if line.count("**") % 2:
            # Непарный маркер в строке: снимаем все «**» в этой строке, иначе
            # выделение «перетекает» на следующие абзацы и жирнит весь ответ.
            line = line.replace("**", "")
        fixed_lines.append(line)
    value = "\n".join(fixed_lines)
    value = re.sub(r"[\s,;—]+$", "", value)
    if len(value.strip()) < max(120, int(len(original.strip()) * 0.5)):
        return original
    return value


def _fallback_followups(answer: str) -> list:
    lines = str(answer or "").splitlines()
    title = lines[0].lstrip("# ").strip() if lines else ""
    return ["Подробнее: " + title[:60]] if title else []


def _filter_followups(items, question: str, answer: str) -> list:
    """Кнопки только по теме вопроса."""
    words = {
        word.lower() for word in re.findall(r"[\w-]{5,}", question or "")
    } - {"какие", "какой", "какая", "каких", "сколько", "почему", "зачем"}
    generic = ("куда написать", "куда писать", "есть ли у вас")
    ask_contact = any(w in (question or "").lower() for w in ("контакт", "написать", "связ"))
    kept = []
    for item in items or []:
        text = str(item or "").strip()
        if not text or text.lower() == (question or "").strip().lower():
            continue
        if any(text.lower().startswith(prefix) for prefix in generic) and not ask_contact:
            continue
        if words and not (words & {w.lower() for w in re.findall(r"[\w-]{5,}", text)}):
            continue
        if text not in kept:
            kept.append(text)
        if len(kept) >= 4:
            break
    return kept

def _strip_inline_sources(text: str) -> str:
    """Убирает блок «Источники» и отдельные строки-ссылки под ним."""
    value = str(text or "")
    value = re.sub(
        r"(?im)^\s*(#{0,4}\s*)?\**\s*Источники\s*\**\s*[-—:]?\s*.*$", "", value
    )
    value = re.sub(r"(?im)^\s*[-*•]\s*https?://\S+\s*$", "", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _link_footnotes(text: str, sources) -> str:
    """Делает маркеры [n] кликабельными: [n](URL источника)."""
    urls = [str(item.get("url") or "") for item in (sources or [])]
    urls = [url for url in urls if url.startswith("http")]

    def repl(match: re.Match) -> str:
        number = int(match.group(1))
        if 1 <= number <= len(urls):
            return f"[{number}]({urls[number - 1]})"
        return match.group(0)

    return re.sub(r"\[(\d{1,2})\]", repl, str(text or ""))

def _strip_orphan_brackets(text: str) -> str:
    """Ссылка осталась без адреса — оставляем текст, убираем скобки."""
    def repl(match: re.Match) -> str:
        label = match.group(1).strip()
        if not label or label.isdigit():
            return match.group(0)
        return label

    return re.sub(r"\[([^\]\n]{2,120})\](?!\()", repl, str(text or ""))

def _finalize(text: str, sources, keep_markers: bool) -> str:
    """Единая финальная отделка ответа."""
    value = _normalize_tables(_clean_dangling(text))
    value = _link_footnotes(value, sources)
    value = _footnote_links(value)
    value = _strip_inline_sources(value)
    value = _strip_orphan_brackets(value)
    # Повторы одной и той же сноски: «[1][1]» → «[1]» (и в виде ссылок).
    value = re.sub(r"(\[\d{1,2}\])(?:\s*\1)+", r"\1", value)
    value = re.sub(r"(\[\d{1,2}\]\([^)]*\))(?:\s*\1)+", r"\1", value)
    # «1[1]» — лишняя цифра перед сноской: остаётся только [1].
    value = re.sub(r"\b\d{1,2}\[(\d{1,2})\]\(", r"[\1](", value)
    value = re.sub(r"\b\d{1,2}\[(\d{1,2})\]", r"[\1]", value)
    if not keep_markers:
        # Клиенту показываем номера в квадратных скобках: [1], [2] …
        # Ссылка при этом остаётся в блоке «Источники».
        value = re.sub(r"\[(\d{1,2})\]\([^)]*\)", r"[\1]", value)
        value = re.sub(r"(\[\d{1,2}\])(?:\s*\1)+", r"\1", value)
    return re.sub(r"[ \t]{2,}", " ", value).strip()

_RARE_TOKEN = re.compile(
    r"\b(?:[A-Z]{2,}[A-Z0-9._-]*|UG\.[A-Z0-9._]+|[A-Za-z]+-?\d{2,}\w*|\d{3,})\b"
)
_DOMAIN_TERMS = re.compile(
    r"\b(?:кластер\w*|команд\w*|верси\w*|лицензи\w*|сертифика\w*|журнал\w*|"
    r"VRID|VRRP|LACP|IPMI|PKI|SNMP|DCFW|NGFW|WAF|SWG|SIEM|API|CLI)\b",
    re.I,
)
_CAMEL = re.compile(r"\b[A-Z][a-z]+[A-Z][A-Za-z]*\b")


_VAGUE_START = re.compile(
    r"^\s*(что такое|что делает|чем отличается|зачем|как работает|как настроить|"
    r"расскажи|опиши|какие|сколько|кто такая|почему)\b",
    re.I,
)


_PRODUCT_RE = re.compile(r"\b(NGFW|DCFW|SWG|WAF|SIEM|SUMMA|UGOS|Log Analyzer|Management Center|Client)\b")
_GREETING_RE = re.compile(
    r"^\s*(привет\w*|здравств\w*|добрый\s+(?:день|вечер)\w*|доброе\s+утро|хай|hello|hi)\b",
    re.I,
)


def _heading_item(answer: str) -> str:
    """Кнопка из заголовка ответа — без вызова модели."""
    for line in str(answer or "").splitlines():
        text = line.strip()
        if not text.startswith("#"):
            continue
        title = " ".join(text.lstrip("#").strip().split())
        if not title:
            continue
        # «Подробнее: Подробнее: …» и приветствия кнопкой не становятся.
        title = re.sub(r"^(?:подробнее\s*[:—-]\s*)+", "", title, flags=re.I).strip()
        if not title or _GREETING_RE.match(title):
            return ""
        short = re.split(r"[:—–]|\.\s", title, maxsplit=1)[0].strip()
        short = short or title
        if len(short) > 45:
            # Длинный заголовок — это уже абзац, кнопкой он не становится.
            return ""
        return "Подробнее: " + short
    return ""


def _with_suggestions(client, question: str, answer: str, existing) -> list:
    """2–3 кнопки: одна из контекста, остальные — быстрый вызов модели."""
    items = []
    for item in existing or []:
        value = str(item).strip()
        if not value:
            continue
        bare = re.sub(r"^(?:подробнее\s*[:—-]\s*)+", "", value, flags=re.I).strip()
        if _GREETING_RE.match(bare):
            continue
        items.append(value)
    seen = {" ".join(item.lower().split()).rstrip("?.! ") for item in items}
    asked = " ".join(str(question or "").lower().split())

    def add(candidate: str, limit: int) -> None:
        candidate = " ".join(str(candidate or "").strip(" -•*0123456789.)").split())
        if not candidate or len(candidate) < 8 or len(candidate) > 90:
            return
        if not candidate.endswith("?"):
            candidate += "?"
        if _GREETING_RE.match(re.sub(r"^(?:подробнее\s*[:—-]\s*)+", "", candidate, flags=re.I)):
            return
        key = candidate.lower().rstrip("?.! ")
        if key in seen or key == asked or key[:-1] in asked:
            return
        seen.add(key)
        items.append(candidate)
        if len(items) >= limit:
            return

    # 1. Из контекста, без модели.
    greeting = bool(_GREETING_RE.match(str(question or "").strip()))
    if len(items) < 3 and not greeting:
        add(_heading_item(answer), 3)
    if greeting:
        items = [item for item in items if not item.lower().startswith("подробнее")]
    if greeting and len(items) < 3:
        add("Какие продукты есть у UserGate?", 3)
        add("С чего начать изучение UserGate?", 3)
        add("Как связаться с UserGate?", 3)
    if len(items) < 2:
        product = _PRODUCT_RE.search(f"{question} {answer}")
        if product:
            add(f"Какие версии UserGate {product.group(1)} существуют?", 3)
        else:
            add("Как связаться с UserGate?", 3)

    # 2. Остальное — один короткий вызов модели по вопросу.
    if len(items) < 3 and client is not None:
        try:
            data = client.complete(
                [
                    {
                        "role": "system",
                        "content": (
                            "Придумай 2 коротких вопроса клиента по теме вопроса. "
                            "Каждый с новой строки, без нумерации, до 70 символов."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"ВОПРОС: {question}\nОТВЕТ (начало): {str(answer or '')[:350]}",
                    },
                ],
                max_tokens=200,
                allow_thinking=False,
            )
            choices = data.get("choices") or []
            text = str((choices[0].get("message") or {}).get("content") or "") if choices else ""
        except Exception:  # noqa: BLE001 - кнопки не должны ронять ответ
            text = ""
        for line in re.split(r"[\n;]+", text):
            add(line, 3)
            if len(items) >= 3:
                break

    return items[:3]

def _table_cells(line: str) -> list:
    value = line.strip().strip("|")
    return [cell.strip() for cell in value.split("|")]


def _repair_table_headers(text: str) -> str:
    """Дополняет шапку таблицы, если первая колонка потерялась."""
    lines = str(text or "").splitlines()
    out = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip().startswith("|"):
            out.append(line)
            index += 1
            continue
        block = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            block.append(lines[index])
            index += 1
        separator = next(
            (pos for pos, row in enumerate(block) if set(row.strip()) <= set("|-: ")),
            None,
        )
        if separator is not None and separator > 0:
            header = _table_cells(block[separator - 1])
            data_rows = [_table_cells(row) for row in block[separator + 1:] if row.strip()]
            width = max((len(row) for row in data_rows), default=0)
            if width > len(header) and len(header) >= 1:
                header = ["Критерий"] + header
                block[separator - 1] = "| " + " | ".join(header) + " |"
                block[separator] = "|" + "|".join(["---"] * len(header)) + "|"
        out.extend(block)
    return "\n".join(out)

def _table_cells_row(line: str) -> list:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _normalize_table_shape(text: str) -> str:
    """Выравнивает таблицы: у всех строк столько же ячеек, сколько в шапке."""
    lines = str(text or "").splitlines()
    out = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip().startswith("|"):
            out.append(line)
            index += 1
            continue
        block = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            block.append(lines[index])
            index += 1
        separator = next(
            (pos for pos, row in enumerate(block) if set(row.strip()) <= set("|-: ")),
            None,
        )
        if separator is None or separator == 0:
            out.extend(block)
            continue
        header = _table_cells_row(block[separator - 1])
        # Повторяющиеся названия колонок: «Критерий | Критерий» → второй убираем.
        if len(header) > 1 and header[0] == header[1]:
            header = [header[0]] + header[2:]
        width = len(header)
        if width < 2:
            out.extend(block)
            continue
        fixed = []
        fixed.append("| " + " | ".join(header) + " |")
        fixed.append("|" + "|".join(["---"] * width) + "|")
        for row in block[separator + 1:]:
            cells = _table_cells_row(row)
            if len(cells) > width:
                cells = cells[: width - 1] + [" ".join(cells[width - 1:])]
            while len(cells) < width:
                cells.append("")
            fixed.append("| " + " | ".join(cells) + " |")
        out.extend(fixed)
    return "\n".join(out)

