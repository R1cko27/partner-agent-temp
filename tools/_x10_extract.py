"""Извлекает ключевые разделы datasheet X10 для карточки продукта."""

from __future__ import annotations

import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TEXT = pathlib.Path(
    "data-temp/09-company/products/usergate-x10/parsed/01-datasheet-usergate-x10.md"
).read_text(encoding="utf-8")


def section(title: str, limit: int = 1200) -> str:
    pattern = re.compile(r"^## " + re.escape(title) + r"\s*$(.*?)(?=^## |\Z)", re.M | re.S)
    match = pattern.search(TEXT)
    return match.group(1).strip()[:limit] if match else "(нет раздела)"


for name in (
    "Производительность",
    "Спецификация оборудования",
    "Соответствие требованиям законодательства Российской Федерации",
    "Дополнительные подписки",
):
    print("###", name)
    print(section(name))
    print()
