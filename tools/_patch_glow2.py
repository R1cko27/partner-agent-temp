"""Вставляет создание радужной рамки в скрипт страницы."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

JS = """  var glow = document.createElement('div');
  glow.className = 'ug-glow';
  glow.appendChild(document.createElement('i'));
  document.body.appendChild(glow);
  window.setTimeout(function () { glow.classList.add('on'); }, 60);
  window.setTimeout(function () { glow.classList.remove('on'); }, 1700);

"""

ANCHOR = "  var header = document.querySelector('header');"


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if "var glow" not in text:
        text = text.replace(ANCHOR, JS + ANCHOR, 1)
        changed.append("создание рамки")

    if "glow.classList.add('on')" in text and "if (glow) glow.classList.add('on');" not in text:
        text = text.replace(
            "    var bot = addMessage('bot', '<span class=\"ug-msg__typing\">Думаю</span>');",
            "    var bot = addMessage('bot', '<span class=\"ug-msg__typing\">Думаю</span>');\n"
            "    if (glow) glow.classList.add('on');",
            1,
        )
        text = text.replace(
            "              state.text += event.text;",
            "              if (glow) glow.classList.remove('on');\n"
            "              state.text += event.text;",
            1,
        )
        changed.append("рамка при ожидании")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("правки:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
