"""Шаг 4: для перечислений передаём в контекст полный список элементов."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")

HELPER = '''def _list_items_from(text: str, limit: int = 12) -> List[str]:
    """Элементы списка из фрагмента: строки таблицы и хвосты после двоеточия.

    Нужно для перечислений: модели отдаём готовый перечень, а не «в материалах
    что-то перечислено», иначе она называет один-два пункта.
    """
    items: List[str] = []
    seen: set[str] = set()

    def add(value: str) -> None:
        clean = value.strip(" .;:—-«»\\"'|")
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


'''

OLD = '''        if _is_enumeration(question):
            # Элементы ищем во фрагментах до ответа: модель сама встроит их в текст,
            # а дописывание списка в конец ответа выглядело инородно.
            enum_source = " ".join(
                str(hit.chunk.get("text") or "") for hit in hits[:4]
            )
            enum_items = _enumeration_items(enum_source)[:6]
            hint = "ВОПРОС-ПЕРЕЧИСЛЕНИЕ: назови все элементы, не сокращая до одного примера."
            if enum_items:
                hint += " В материалах перечислено: " + ", ".join(enum_items) + "."
            lines.append(hint)'''

NEW = '''        if _is_enumeration(question):
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
            lines.append(hint)'''


def main() -> int:
    text = AGENT.read_text(encoding="utf-8")
    changed = []
    if "_list_items_from" not in text:
        anchor = "def _enumeration_items(text: str) -> List[str]:"
        text = text.replace(anchor, HELPER + anchor, 1)
        changed.append("извлечение списка")
    if "Полный перечень из материалов" not in text:
        if OLD in text:
            text = text.replace(OLD, NEW, 1)
            changed.append("контекст перечисления")
        else:
            print("не найден блок перечисления")
    AGENT.write_text(text, encoding="utf-8")
    print("агент:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
