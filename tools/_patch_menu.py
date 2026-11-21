"""Пункт «Чат с ИИ» — в основное меню (menubar), а не в верхнюю строку."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

OLD_MENU_ITEM = """MENU_ITEM = (
    '<li class="header-menu__menu-item">'
    '<a class="header-menu__menu-item-link" href="#ugAsk">Чат с ИИ</a>'
    "</li>"
)"""

NEW_MENU_ITEM = """MENU_ITEM = (
    '<li class="header-menu__item" role="presentation">'
    '<a class="header-menu__item-link" href="#ugAsk"><span>Чат с ИИ</span></a>'
    "</li>"
)"""

OLD_INSERT = """    if ">Чат с ИИ<" not in html:
        marker = '<ul class="header-menu__menu">'
        start = html.find(marker)
        if start >= 0:
            end = html.find("</ul>", start)
            if end > start:
                html = html[:end] + MENU_ITEM + html[end:]"""

NEW_INSERT = """    if ">Чат с ИИ<" not in html:
        menubar = '<ul class="" role="menubar">'
        start = html.find(menubar)
        if start >= 0:
            html = html[: start + len(menubar)] + MENU_ITEM + html[start + len(menubar):]"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if OLD_MENU_ITEM in text:
        text = text.replace(OLD_MENU_ITEM, NEW_MENU_ITEM, 1)
        changed.append("разметка пункта меню")

    if OLD_INSERT in text:
        text = text.replace(OLD_INSERT, NEW_INSERT, 1)
        changed.append("вставка в menubar")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("правки:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
