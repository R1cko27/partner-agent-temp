"""Анимация печати примерных вопросов в поле ввода, как в основном интерфейсе."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

JS = r"""  var EXAMPLES = [
    'Чем NGFW отличается от WAF?',
    'Какие сертификаты ФСТЭК есть у продуктов?',
    'Какие аппаратные платформы поддерживаются?',
    'Что входит в каталог курсов и экзаменов Академии?'
  ];
  var typeIndex = 0;
  var typePos = 0;
  var typeDeleting = false;
  var typeTimer = null;
  var typeRunning = false;

  function stopTyping() {
    typeRunning = false;
    if (typeTimer) { clearTimeout(typeTimer); typeTimer = null; }
    input.placeholder = 'Введите запрос…';
  }

  function typeLoop() {
    if (!typeRunning) return;
    var text = EXAMPLES[typeIndex % EXAMPLES.length];
    if (!typeDeleting) {
      typePos += 1;
      if (typePos >= text.length) {
        input.placeholder = text;
        typeDeleting = true;
        typeTimer = setTimeout(typeLoop, 1700);
        return;
      }
    } else {
      typePos -= 1;
      if (typePos <= 0) {
        typeDeleting = false;
        typeIndex += 1;
        typePos = 0;
      }
    }
    input.placeholder = typePos > 0 ? text.slice(0, typePos) : 'Введите запрос…';
    typeTimer = setTimeout(typeLoop, typeDeleting ? 24 : 58);
  }

  input.addEventListener('focus', stopTyping);
  input.addEventListener('input', function () { if (input.value) stopTyping(); });

"""

ANCHOR = "  form.addEventListener('submit'"


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    if "function typeLoop()" in text:
        print("анимация уже есть")
        return 0
    text = text.replace(ANCHOR, JS + ANCHOR, 1)
    text = text.replace(
        "    if (starters) starters.classList.add('is-hidden');",
        "    if (starters) starters.classList.add('is-hidden');\n    stopTyping();",
        1,
    )
    text = text.replace(
        "  input.addEventListener('focus', stopTyping);",
        "  typeRunning = true;\n  typeLoop();\n\n  input.addEventListener('focus', stopTyping);",
        1,
    )
    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("добавлена анимация печати примеров в поле ввода")
    return 0


if __name__ == "__main__":
    sys.exit(main())
