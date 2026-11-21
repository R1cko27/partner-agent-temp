"""Реестр фактов из базы знаний для судьи.

Судья видит только эталон и контекст, поэтому честно взятый из базы факт может
попасть в «выдумки», если не дошёл до контекста. Реестр снимает эту проблему:
собираем числа, номера, версии, домены и названия событий из всех материалов.

    python tools/build_facts.py

Пишет `storage/index/facts.json`:
{"numbers": {"3905": ["сертификат ФСТЭК России … № 3905 …"]},
 "urls": {"docs.usergate.com/glossary": "…"},
 "versions": {"7.7.0": "…"}, "events": {"server_added": "…"}}
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from partner.config import Settings

NUMBER_RE = re.compile(r"\b\d[\d\s\u00a0]{1,}\b")
VERSION_RE = re.compile(r"\b\d+\.\d+(?:\.\d+)?(?:[xX])?\b")
URL_RE = re.compile(r"https?://[^\s)\]>»«\"']+")
DOMAIN_PATH_RE = re.compile(r"\b((?:docs|www|my|static)\.usergate\.com/[^\s)\]>»«\"'.,;]+|[a-z0-9-]+\.usergate\.com)")
EVENT_RE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+){1,3}\b")

MAX_CONTEXTS = 3
WINDOW = 70


def context(text: str, start: int, end: int) -> str:
    left = max(0, start - WINDOW)
    right = min(len(text), end + WINDOW)
    return " ".join(text[left:right].split())


def add(store: Dict[str, List[str]], key: str, snippet: str) -> None:
    clean = key.strip()
    if not clean:
        return
    items = store.setdefault(clean, [])
    if snippet and len(items) < MAX_CONTEXTS and snippet not in items:
        items.append(snippet[:200])


def main() -> int:
    settings = Settings.load()
    data_dir = settings.data_dir
    facts = {"numbers": {}, "versions": {}, "urls": {}, "events": {}}
    files = 0

    for path in data_dir.rglob("*.md"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        files += 1
        for match in NUMBER_RE.finditer(text):
            number = re.sub(r"\s+", "", match.group(0))
            if len(number) >= 3:
                add(facts["numbers"], number, context(text, match.start(), match.end()))
        for match in VERSION_RE.finditer(text):
            add(facts["versions"], match.group(0), context(text, match.start(), match.end()))
        for match in URL_RE.finditer(text):
            add(facts["urls"], match.group(0).rstrip(".,;"), context(text, match.start(), match.end()))
        for match in DOMAIN_PATH_RE.finditer(text):
            add(facts["urls"], match.group(0).rstrip(".,;"), context(text, match.start(), match.end()))
        for match in EVENT_RE.finditer(text):
            add(facts["events"], match.group(0), context(text, match.start(), match.end()))

    target = settings.index_dir / "facts.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(facts, ensure_ascii=False), encoding="utf-8")
    print(f"файлов: {files}")
    print(f"чисел: {len(facts['numbers'])} · версий: {len(facts['versions'])}"
          f" · адресов: {len(facts['urls'])} · событий: {len(facts['events'])}")
    print("записано:", target)
    for key in ("3905", "1194", "7.7.0", "server_added"):
        store = "numbers" if key in ("3905", "1194") else ("versions" if "." in key else "events")
        sample = facts[store].get(key)
        if sample:
            print(f"  {key}: {sample[0][:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
