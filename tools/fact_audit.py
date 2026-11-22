"""Проверка: есть ли факты эталона в базе знаний."""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "storage" / "index" / "chunks.json"
ANCHOR_RE = re.compile(r"\b\d[\d\s.,]{1,12}\d\b|\b[A-ZА-Я]{2,}[A-ZА-Я0-9._-]*\b|\b\w+\.[a-zа-я]{2,4}/[\w/.-]+\b")


def load_blob() -> str:
    data = json.loads(CHUNKS.read_text(encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("chunks") or []
    return " ".join(str(item.get("text") or "") for item in items).lower()


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    path = ROOT / "tools" / (argv[0] if argv else "benchmark-60-usergate-2026-11-21.json")
    ids = {x.strip().upper() for x in (argv[1].split(",") if len(argv) > 1 else [])}
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("questions") if isinstance(data, dict) else data
    blob = load_blob()
    print("база, символов:", len(blob))
    for row in rows:
        if ids and str(row.get("id", "")).upper() not in ids:
            continue
        reference = str(row.get("answer") or "")
        anchors = [a for a in ANCHOR_RE.findall(reference) if len(a) >= 2][:8]
        missing = [a for a in anchors if a.lower() not in blob]
        mark = "OK" if not missing else "НЕТ В БАЗЕ"
        print(f"{row.get('id')} {mark}: {', '.join(missing[:6]) if missing else '—'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
