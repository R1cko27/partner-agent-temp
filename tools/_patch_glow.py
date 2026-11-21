"""Радужная анимированная рамка по краю экрана (как у Gemini) при загрузке."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

CSS = """.ug-glow{position:fixed;inset:0;z-index:9997;pointer-events:none;padding:3px;opacity:0;
transition:opacity .55s ease;
-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
-webkit-mask-composite:xor;mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
mask-composite:exclude}
.ug-glow.on{opacity:1}
.ug-glow i{position:absolute;inset:-45%;display:block;
background:conic-gradient(from 0deg,#ff2d55,#ff9500,#ffe600,#34c759,#32ade6,#5856d6,#ff2d55);
animation:ugSpin 5.5s linear infinite}
@keyframes ugSpin{to{transform:rotate(360deg)}}
"""

JS = """  var glow = document.createElement('div');
  glow.className = 'ug-glow';
  glow.appendChild(document.createElement('i'));
  document.body.appendChild(glow);
  window.setTimeout(function () { glow.classList.add('on'); }, 60);
  window.setTimeout(function () { glow.classList.remove('on'); }, 1700);

"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if ".ug-glow{" not in text:
        text = text.replace(".ug-ask{margin:0;padding:0;", CSS + ".ug-ask{margin:0;padding:0;", 1)
        changed.append("стили рамки")

    if "ug-glow" not in text.split("var glow")[0]:
        text = text.replace("  var header = document.querySelector('header');", JS + "  var header = document.querySelector('header');", 1)
        changed.append("создание рамки")

    # Показываем рамку, пока модель готовит ответ.
    if "glow.classList.add('on')" in text and "state.text.length === 0" not in text:
        text = text.replace(
            "              state.text += event.text;",
            "              if (glow) glow.classList.remove('on');\n              state.text += event.text;",
            1,
        )
        text = text.replace(
            "    var bot = addMessage('bot', '<span class=\"ug-msg__typing\">Думаю</span>');",
            "    var bot = addMessage('bot', '<span class=\"ug-msg__typing\">Думаю</span>');\n    if (glow) glow.classList.add('on');",
            1,
        )
        changed.append("рамка при ожидании")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("правки:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
