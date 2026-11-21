"""Клиент: домены без схемы становятся кликабельными."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

APP = pathlib.Path("partner/web/app.js")

HELPER = r"""const BARE_DOMAIN = /(^|[\s(«])((?:[a-z0-9-]+\.)+(?:ru|com|org|net|io|su|by|kz)(?:\/[\w\-./?=&%#+]*)?)/gi;

function linkifyDomains(html) {
  // Домены без схемы («dreamjob.ru/employers/125535») тоже делаем ссылками.
  // Готовые <a> не трогаем, иначе получится вложенная ссылка.
  const parts = html.split(/(<a\b[^>]*>[\s\S]*?<\/a>)/);
  return parts
    .map((part, index) => {
      if (index % 2 === 1) return part;
      return part.replace(BARE_DOMAIN, (match, prefix, domain) =>
        `${prefix}<a href="https://${domain}" target="_blank" rel="noopener noreferrer">${domain}</a>`);
    })
    .join('');
}

"""


def main() -> int:
    text = APP.read_text(encoding="utf-8")
    changed = []

    if "linkifyDomains" not in text:
        anchor = "function inlineMarkup(text) {"
        text = text.replace(anchor, HELPER + anchor, 1)
        changed.append("функция")

    old_call = "  out = linkifyOrMarkdown(out);"
    new_call = "  out = linkifyDomains(linkifyOrMarkdown(out));"
    if new_call not in text and old_call in text:
        text = text.replace(old_call, new_call, 1)
        changed.append("вызов")

    APP.write_text(text, encoding="utf-8", newline="\n")
    print("app.js:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
