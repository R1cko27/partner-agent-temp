"""Переносит подсказки-вопросы из-под чата внутрь сообщения ассистента."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

CHIPS_BLOCK = '''    <div class="ug-ask__chips" id="ugChips">
      <button class="ug-ask__chip" type="button">Чем NGFW отличается от WAF?</button>
      <button class="ug-ask__chip" type="button">Какие сертификаты ФСТЭК есть у продуктов?</button>
      <button class="ug-ask__chip" type="button">Какие аппаратные платформы поддерживаются?</button>
      <button class="ug-ask__chip" type="button">Что входит в каталог курсов и экзаменов Академии?</button>
    </div>
'''

LISTENERS = '''  Array.prototype.forEach.call(document.querySelectorAll('.ug-ask__chip'), function (chip) {
    chip.addEventListener('click', function () { ask(chip.textContent.trim()); });
  });
'''

FOLLOWUP_CSS = '''.ug-followups{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;animation:ugIn .3s ease both}
.ug-followups button{border:0;border-radius:999px;padding:8px 14px;font:500 13px "Granate","Inter",Arial,sans-serif;
color:#2050d0;background:#eef3ff;cursor:pointer;transition:background .18s ease}
.ug-followups button:hover{background:#dfe9ff}
'''

CALL_IN_ASK = '''      bot.innerHTML = renderMarkdown(text || 'Не удалось получить ответ.');'''

RENDER_FN = '''  function renderFollowups(node, items) {
    var questions = (items || []).map(function (item) {
      if (typeof item === 'string') return item;
      return (item && (item.question || item.text)) || '';
    }).filter(function (value) { return value; }).slice(0, 4);
    if (!questions.length) return;
    var row = document.createElement('div');
    row.className = 'ug-followups';
    questions.forEach(function (question) {
      var button = document.createElement('button');
      button.type = 'button';
      button.textContent = question;
      button.addEventListener('click', function () { ask(question); });
      row.appendChild(button);
    });
    node.appendChild(row);
  }

'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if CHIPS_BLOCK in text:
        text = text.replace(CHIPS_BLOCK, "", 1)
        changed.append("статические вопросы убраны")

    if LISTENERS in text:
        text = text.replace(LISTENERS, "", 1)
        changed.append("слушатели старых чипов убраны")

    if ".ug-followups" not in text:
        text = text.replace(
            ".ug-msg__sources{",
            FOLLOWUP_CSS + ".ug-msg__sources{",
            1,
        )
        changed.append("стили вопросов под сообщением")

    if "renderFollowups" not in text:
        text = text.replace("  async function ask(question) {", RENDER_FN + "  async function ask(question) {", 1)
        changed.append("функция рендера вопросов")

    # Собираем followups из события done и рисуем их под ответом.
    if "var chips = [];" not in text:
        text = text.replace("    var sources = [];", "    var sources = [];\n    var chips = [];", 1)
        text = text.replace(
            "              if (event.sources) sources = event.sources;",
            "              if (event.sources) sources = event.sources;\n"
            "              if (Array.isArray(event.followups)) chips = event.followups;",
            1,
        )
        text = text.replace(
            CALL_IN_ASK,
            CALL_IN_ASK + "\n      renderFollowups(bot, chips);",
            1,
        )
        changed.append("вопросы рисуются под ответом")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("сборщик:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
