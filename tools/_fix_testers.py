"""Правки по замечаниям тестировщиков (без запуска тестов и сервера)."""

from __future__ import annotations

import io
import json
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")
PROFILE = pathlib.Path("data/company/agent.json")
CONTACTS = pathlib.Path("data/company/about/contacts.md")

RULES = [
    "Отвечай по-русски. Другой язык — только если пользователь прямо попросил "
    "ответить на нём («по-английски», «in English»).",
    "Держи структуру: каждая мысль — отдельным абзацем через пустую строку. "
    "Не выдавай сплошное полотно текста.",
    "Не добавляй заголовок «Источники» в конце ответа: список источников "
    "интерфейс показывает отдельно.",
    "Если называешь сертификат, рядом с ним давай ссылку на реестр или страницу "
    "подтверждения, а не одну общую ссылку на весь ответ.",
    "На вопрос о телефоне называй только общий номер со страницы контактов. "
    "Номера Академии и из справки партнёра не выдавай за общий номер компании.",
]

HELPERS = '''_OTHER_LANG_RE = re.compile(
    r"in english|english please|answer in|по-английски|на английском|на китайском",
    re.I,
)
_SOURCES_HEAD_RE = re.compile(r"(?im)^\\s*(#{1,4}\\s*)?(источники|sources)\\s*:?\\s*$")


def _wants_other_language(question: str) -> bool:
    """Пользователь явно попросил ответить не по-русски."""
    return bool(_OTHER_LANG_RE.search(question or ""))


def _strip_sources_heading(text: str) -> str:
    """Убирает «### Источники»: список источников интерфейс показывает сам."""
    cleaned = _SOURCES_HEAD_RE.sub("", text or "")
    return re.sub(r"\\n{3,}", "\\n\\n", cleaned).strip()


'''

LANG_OLD = "        lang = detect_lang(question)"
LANG_NEW = """        lang = detect_lang(question)
        # Клиент русскоязычный: по умолчанию отвечаем по-русски, даже если
        # вопрос задан по-английски. Исключение — явная просьба о другом языке.
        if not _wants_other_language(question):
            lang = "ru\""""

PUNCT_OLD = '''    cleaned = re.sub(r"\\s+(?:и|или|а|но)\\s*([.,;:!?])", r"\\1", cleaned)'''
PUNCT_NEW = '''    cleaned = re.sub(r"\\s+(?:и|или|а|но)\\s*([.,;:!?])", r"\\1", cleaned)
    # После вырезанной ссылки остаётся «переменную:.» или «текст :.» — чистим.
    cleaned = re.sub(r":\\s*([.,;])", r"\\1", cleaned)
    cleaned = re.sub(r"\\s+:\\s*", ": ", cleaned)'''

CONTACTS_NOTE = """
## Какой номер считать общим

Общий номер компании — **8 495 150 97 48** (страница контактов). Его и называют
на вопрос «телефон для связи».

Другие номера в базе общим не являются и выдавать их за общий нельзя:

- **8 499 472 46 79** — номер из справки партнёра, не со страницы контактов;
- **8 499 450 22 48, доб. 9277** — линия Академии по вопросам обучения;
- **+7 958 540-62-92** — мобильная линия Академии.

Если спрашивают телефон Академии — называется номер Академии; если телефон
компании — только 8 495 150 97 48.
"""


def patch_agent() -> None:
    text = AGENT.read_text(encoding="utf-8")
    changed = []

    if "_wants_other_language" not in text:
        anchor = "def _client_text(text: str) -> str:"
        text = text.replace(anchor, HELPERS + anchor, 1)
        changed.append("хелперы языка и заголовка")

    if "_wants_other_language(question)" not in text:
        text = text.replace(LANG_OLD, LANG_NEW, 1)
        changed.append("русский по умолчанию")

    if "После вырезанной ссылки" not in text:
        text = text.replace(PUNCT_OLD, PUNCT_NEW, 1)
        changed.append("чистка пунктуации")

    if "_strip_sources_heading" in text and "return _strip_sources_heading" not in text:
        old = "        return _normalize_tables(text).strip()"
        new = "        return _strip_sources_heading(_normalize_tables(text)).strip()"
        if old in text:
            text = text.replace(old, new, 1)
            changed.append("снятие заголовка «Источники»")

    AGENT.write_text(text, encoding="utf-8")
    print("агент:", ", ".join(changed) or "без изменений")


def patch_profile() -> None:
    data = json.loads(PROFILE.read_text(encoding="utf-8-sig"))
    rules = data.get("rules") or []
    added = [rule for rule in RULES if rule not in rules]
    if not added:
        print("правила: уже есть")
        return
    rules.extend(added)
    data["rules"] = rules
    PROFILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("правила: добавлено", len(added))


def patch_contacts() -> None:
    text = CONTACTS.read_text(encoding="utf-8")
    if "Какой номер считать общим" in text:
        print("контакты: уточнение уже есть")
        return
    CONTACTS.write_text(text.rstrip() + "\n" + CONTACTS_NOTE, encoding="utf-8")
    print("контакты: добавлено правило общего номера")


def main() -> int:
    patch_agent()
    patch_profile()
    patch_contacts()
    return 0


if __name__ == "__main__":
    sys.exit(main())
