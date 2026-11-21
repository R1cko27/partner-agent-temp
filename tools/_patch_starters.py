"""Стартовые вопросы видны до первого запроса, потом исчезают."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

MARKUP_OLD = """    </form>
  </div>
</section>"""

MARKUP_NEW = """    </form>
    <div class="ug-ask__starters" id="ugStarters">
      <button type="button">Чем NGFW отличается от WAF?</button>
      <button type="button">Какие сертификаты ФСТЭК есть у продуктов?</button>
      <button type="button">Какие аппаратные платформы поддерживаются?</button>
      <button type="button">Что входит в каталог курсов и экзаменов Академии?</button>
    </div>
  </div>
</section>"""

CSS = """.ug-ask__starters{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.ug-ask__starters button{border:0;border-radius:999px;padding:8px 15px;font:500 14px "Granate","Inter",Arial,sans-serif;
color:#fff;background:rgba(255,255,255,.16);cursor:pointer;transition:background .18s ease,transform .18s ease}
.ug-ask__starters button:hover{background:rgba(255,255,255,.3);transform:translateY(-1px)}
.ug-ask__starters.is-hidden{display:none}
"""

JS = """  var starters = document.getElementById('ugStarters');
  if (starters) {
    Array.prototype.forEach.call(starters.querySelectorAll('button'), function (button) {
      button.addEventListener('click', function () { ask(button.textContent.trim()); });
    });
  }
"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if "ugStarters" not in text:
        text = text.replace(MARKUP_OLD, MARKUP_NEW, 1)
        changed.append("кнопки стартовых вопросов")

    if ".ug-ask__starters{" not in text:
        text = text.replace(".ug-msg{border-radius:14px;", CSS + ".ug-msg{border-radius:14px;", 1)
        changed.append("стили стартовых кнопок")

    if "var starters = document.getElementById" not in text:
        text = text.replace("  form.addEventListener('submit'", JS + "\n  form.addEventListener('submit'", 1)
        changed.append("обработчики")

    if "starters.classList.add('is-hidden')" not in text:
        text = text.replace(
            "    band.classList.add('is-chat');",
            "    band.classList.add('is-chat');\n    if (starters) starters.classList.add('is-hidden');",
            1,
        )
        changed.append("скрытие после первого вопроса")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("сборщик:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
