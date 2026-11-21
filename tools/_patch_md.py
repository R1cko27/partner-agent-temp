"""Добавляет markdown-рендер в чат на странице site.html."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page3.py")

JS = '''  function renderMarkdown(text) {
    var lines = String(text || "").replace(/\\r\\n/g, "\\n").split("\\n");
    var out = [];
    var i = 0;

    function fmt(value) {
      var s = escapeHtml(value);
      s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
      s = s.replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>");
      s = s.replace(/(https?:\\/\\/[^\\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
      return s;
    }

    while (i < lines.length) {
      var line = lines[i];
      if (!line.trim()) { i += 1; continue; }

      var head = line.match(/^(#{1,4})\\s+(.*)$/);
      if (head) { out.push("<h3>" + fmt(head[2]) + "</h3>"); i += 1; continue; }

      var isRow = line.trim().charAt(0) === "|";
      var nextIsSep = i + 1 < lines.length && /^\\|?[\\s:|-]+\\|?$/.test(lines[i + 1].trim()) && lines[i + 1].indexOf("-") !== -1;
      if (isRow && nextIsSep) {
        var cells = function (value) {
          return value.trim().replace(/^\\|/, "").replace(/\\|$/, "").split("|").map(function (c) { return c.trim(); });
        };
        var head2 = cells(line);
        i += 2;
        var rows = [];
        while (i < lines.length && lines[i].trim().charAt(0) === "|") { rows.push(cells(lines[i])); i += 1; }
        var html = '<div class="ug-table"><table><thead><tr>' +
          head2.map(function (c) { return "<th>" + fmt(c) + "</th>"; }).join("") +
          "</tr></thead><tbody>";
        rows.forEach(function (row) {
          html += "<tr>" + row.map(function (c) { return "<td>" + fmt(c) + "</td>"; }).join("") + "</tr>";
        });
        out.push(html + "</tbody></table></div>");
        continue;
      }

      if (/^\\s*[-*]\\s+/.test(line)) {
        var items = [];
        while (i < lines.length && /^\\s*[-*]\\s+/.test(lines[i])) {
          items.push(lines[i].replace(/^\\s*[-*]\\s+/, ""));
          i += 1;
        }
        out.push("<ul>" + items.map(function (it) { return "<li>" + fmt(it) + "</li>"; }).join("") + "</ul>");
        continue;
      }

      var buf = [];
      while (
        i < lines.length && lines[i].trim() &&
        !/^(#{1,4})\\s+/.test(lines[i]) &&
        lines[i].trim().charAt(0) !== "|" &&
        !/^\\s*[-*]\\s+/.test(lines[i])
      ) {
        buf.push(fmt(lines[i]));
        i += 1;
      }
      out.push("<p>" + buf.join("<br>") + "</p>");
    }
    return out.join("");
  }
'''

CSS = """
.ug-msg--bot h3{margin:2px 0 8px;font:700 17px/1.3 "Granate","Inter",Arial,sans-serif;color:#1d2b3a}
.ug-msg--bot p{margin:0 0 10px}
.ug-msg--bot p:last-child{margin-bottom:0}
.ug-msg--bot ul{margin:6px 0 10px;padding-left:20px}
.ug-msg--bot li{margin:2px 0}
.ug-msg--bot code{background:#eef2f7;border-radius:5px;padding:1px 5px;font-size:13px}
.ug-table{overflow-x:auto;margin:10px 0}
.ug-table table{border-collapse:collapse;width:100%;font-size:14px}
.ug-table th,.ug-table td{border:1px solid #dfe6ee;padding:8px 10px;text-align:left;vertical-align:top}
.ug-table th{background:#f4f7fb;font-weight:700}
"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if "renderMarkdown" not in text:
        start = text.index("  function inline(text) {")
        end = text.index("\n  }\n", start) + len("\n  }\n")
        text = text[:start] + JS + text[end:]
        text = text.replace("inline(text)", "renderMarkdown(text)")
        text = text.replace("inline(text || ", "renderMarkdown(text || ")
        changed.append("рендер markdown")

    if ".ug-table table" not in text:
        text = text.replace(
            "img[src*=\"_files/\"]{display:none!important}",
            CSS + 'img[src*="_files/"]{display:none!important}',
            1,
        )
        changed.append("стили таблиц и списков")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("сборщик:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
