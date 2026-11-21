"""Починка markdown-таблиц в ответах: пустые строки и число колонок."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")

HELPER = '''_TABLE_SEP_RE = re.compile(r"^\\|?[\\s:|-]+\\|?$")


def _normalize_tables(text: str) -> str:
    """Делает таблицы пригодными для markdown.

    Две типичные поломки от модели:
    1. таблица начинается сразу после абзаца без пустой строки — тогда markdown
       считает её продолжением абзаца и склеивает строки в сплошной текст;
    2. в разделителе другое число колонок, чем в заголовке — таблица не строится
       и показывается сырыми «|---|».
    """
    if "|" not in (text or ""):
        return text

    lines = [line.rstrip() for line in text.split("\\n")]
    spaced: list[str] = []
    for line in lines:
        is_row = line.lstrip().startswith("|")
        prev = spaced[-1].strip() if spaced else ""
        if is_row and prev and not prev.startswith("|"):
            spaced.append("")
        elif prev.startswith("|") and line.strip() and not is_row:
            spaced.append("")
        spaced.append(line)

    fixed: list[str] = []
    index = 0
    while index < len(spaced):
        line = spaced[index]
        is_row = line.lstrip().startswith("|")
        next_line = spaced[index + 1] if index + 1 < len(spaced) else ""
        is_sep = bool(_TABLE_SEP_RE.match(next_line.strip())) and "-" in next_line
        if is_row and is_sep:
            columns = max(1, len([cell for cell in line.strip().strip("|").split("|")]))
            fixed.append(line)
            fixed.append("|" + "|".join(["---"] * columns) + "|")
            index += 2
            continue
        if _TABLE_SEP_RE.match(line.strip()) and "-" in line and fixed:
            index += 1
            continue
        fixed.append(line)
        index += 1

    return "\\n".join(fixed)


'''

CALL_SITES = [
    (
        "        answer = self._attach_doc_links(answer, context_sources)",
        "        answer = self._attach_doc_links(answer, context_sources)\n"
        "        answer = _normalize_tables(answer)",
    ),
    (
        "        if not show_notes:\n"
        "            answer = _client_text(answer)\n"
        "        cached_sources = list(hit.get(\"sources\") or [])",
        "        answer = _normalize_tables(answer)\n"
        "        if not show_notes:\n"
        "            answer = _client_text(answer)\n"
        "        cached_sources = list(hit.get(\"sources\") or [])",
    ),
]


def main() -> int:
    text = AGENT.read_text(encoding="utf-8")
    changed = []

    if "_normalize_tables" not in text:
        anchor = "def _client_text(text: str) -> str:"
        text = text.replace(anchor, HELPER + anchor, 1)
        changed.append("функция нормализации")

    for old, new in CALL_SITES:
        if new.splitlines()[-1] in text and old in text and "_normalize_tables(answer)" not in text.split(old)[1][:80]:
            text = text.replace(old, new, 1)
            changed.append("вызов")

    AGENT.write_text(text, encoding="utf-8")
    print("агент:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
