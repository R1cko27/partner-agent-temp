"""Правка сборки карточек: продукты и справочные страницы — целиком, а не первым абзацем.

Раньше `_product_document` брал `_first_paragraph(text, 1200)`, и всё, что ниже
первого абзаца (версии, кластеры, VRRP, события), в индекс не попадало.
"""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("partner/domain/entities.py")

OLD = '''def _product_document(source: RawSource) -> Document:
    name = source.title
    return Document(
        doc_id=f"product-{_slug(name)}",
        text=f"Продукт {name}\\n{_first_paragraph(source.text, 1200)}\\nИсточник: {source.origin}",
        kind="product",
        title=f"Продукт {name}",
        source=source.origin,
        entities={"product": name},
    )'''

NEW = '''def _product_document(source: RawSource) -> Document:
    name = source.title
    # Карточка идёт в индекс целиком: версии, кластеры и параметры живут
    # в нижних разделах, а не в первом абзаце.
    return Document(
        doc_id=f"product-{_slug(name)}",
        text=f"Продукт {name}\\n{source.text.strip()}\\nИсточник: {source.origin}",
        kind="product",
        title=f"Продукт {name}",
        source=source.origin,
        entities={"product": name},
        metadata={"url": str(source.metadata.get("url") or "")},
    )'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    if "{source.text.strip()}" in text:
        print("карточки уже собираются целиком")
        return 0
    if OLD not in text:
        print("исходный фрагмент не найден — правка не применена")
        return 1
    PATH.write_text(text.replace(OLD, NEW), encoding="utf-8")
    print("карточки продуктов теперь индексируются целиком")
    return 0


if __name__ == "__main__":
    sys.exit(main())
