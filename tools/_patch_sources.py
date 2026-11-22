"""Источники — раскрывающийся блок под ответом, кнопки остаются над ним."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

OLD = """      if (sources && sources.length) {
        var block = document.createElement('div');
        block.className = 'ug-msg__sources';
        var seen = {};
        var unique = sources.filter(function (item) {
          var key = String(item.url || item.source || item.title || '');
          if (!key || seen[key]) return false;
          seen[key] = true;
          return true;
        });
        block.innerHTML = 'Источники:' + unique.slice(0, 4).map(function (item) {
          var url = item.url || item.source || '';
          var title = item.title || url;
          return url ? '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener">' + escapeHtml(title) + '</a>' : '';
        }).join('');
        bot.appendChild(block);
      }"""

NEW = """      if (sources && sources.length) {
        var seen = {};
        var unique = sources.filter(function (item) {
          var key = String(item.url || item.source || item.title || '');
          if (!key || seen[key]) return false;
          seen[key] = true;
          return true;
        });
        if (unique.length) {
          var details = document.createElement('details');
          details.className = 'ug-msg__sources';
          var summary = document.createElement('summary');
          summary.textContent = 'Источники (' + unique.length + ')';
          details.appendChild(summary);
          unique.slice(0, 6).forEach(function (item) {
            var url = item.url || item.source || '';
            if (!url) return;
            var link = document.createElement('a');
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener';
            link.textContent = item.title || url;
            details.appendChild(link);
          });
          bot.appendChild(details);
        }
      }"""

CSS_OLD = """.ug-msg__sources{margin-top:10px;font-size:13px;color:#5b6b7c}
.ug-msg__sources a{display:block;margin-top:4px;color:#0c89db;text-decoration:none}"""

CSS_NEW = """.ug-msg__sources{margin-top:10px;font-size:13px;color:#5b6b7c}
.ug-msg__sources summary{cursor:pointer;list-style:none;font-weight:600;color:#2f4bff;
display:flex;align-items:center;gap:6px;outline:none}
.ug-msg__sources summary::-webkit-details-marker{display:none}
.ug-msg__sources summary:before{content:"▸";font-size:12px;transition:transform .18s ease}
.ug-msg__sources[open] summary:before{content:"▾"}
.ug-msg__sources a{display:block;margin-top:6px;color:#0c89db;text-decoration:none;line-height:1.4}
.ug-msg__sources a:hover{text-decoration:underline}"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if OLD in text:
        text = text.replace(OLD, NEW, 1)
        changed.append("источники в details")

    if CSS_OLD in text:
        text = text.replace(CSS_OLD, CSS_NEW, 1)
        changed.append("стили раскрывающегося блока")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("сборщик:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
