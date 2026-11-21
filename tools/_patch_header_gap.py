"""Пункт меню — в конец списка, полоса чата прижимается к шапке."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

OLD_INSERT = """    if "data-ug-chat" not in html:
        marker = '<ul class="header-menu__menu">'
        if marker in html:
            html = html.replace(marker, marker + MENU_ITEM, 1)"""

NEW_INSERT = """    if ">Чат с ИИ<" not in html:
        marker = '<ul class="header-menu__menu">'
        start = html.find(marker)
        if start >= 0:
            end = html.find("</ul>", start)
            if end > start:
                html = html[:end] + MENU_ITEM + html[end:]"""

PULL_JS = """  var header = document.querySelector('header');
  function pullUp() {
    if (!header || !band) return;
    var gap = band.getBoundingClientRect().top - header.getBoundingClientRect().bottom;
    if (gap > 0.5) band.style.marginTop = (-gap) + 'px';
  }
  window.addEventListener('load', pullUp);
  window.addEventListener('resize', pullUp);

"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if OLD_INSERT in text:
        text = text.replace(OLD_INSERT, NEW_INSERT, 1)
        changed.append("пункт меню в конец списка")

    if "function pullUp()" not in text:
        text = text.replace("  typeRunning = true;", PULL_JS + "  typeRunning = true;", 1)
        changed.append("прижатие полосы к шапке")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("правки:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
