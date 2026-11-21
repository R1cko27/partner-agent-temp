"""Контроль источников в базе знаний.

Проверяет, что у каждого файла материалов есть ссылка на источник,
и собирает сводку ссылок по разделам. Ничего не меняет — только читает.

    python tools/check_sources.py            # отчёт в stdout
    python tools/check_sources.py --write    # плюс сводка в storage/source-links.md
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
COMPANY = ROOT / "data" / "company"
URL_RE = re.compile(r"https?://[^\s\)\]\>\"'«»]+")
# Разделы, где ссылка на источник обязательна: материал должен быть проверяемым.
REQUIRED = ("about", "products", "faq", "docs")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Контроль источников в базе знаний")
    parser.add_argument("--write", action="store_true", help="записать сводку в storage/source-links.md")
    args = parser.parse_args(argv)

    files = sorted(COMPANY.rglob("*.md"))
    files = [path for path in files if path.name != "README.md"]

    without_url: list[str] = []
    per_folder: Counter[str] = Counter()
    total_urls = 0

    for path in files:
        relative = path.relative_to(COMPANY)
        folder = relative.parts[0] if len(relative.parts) > 1 else "корень"
        text = path.read_text(encoding="utf-8", errors="replace")
        urls = URL_RE.findall(text)
        total_urls += len(urls)
        per_folder[folder] += 1
        if not urls and folder in REQUIRED:
            without_url.append(relative.as_posix())

    print(f"файлов материалов: {len(files)}")
    print("по разделам:", dict(sorted(per_folder.items())))
    print(f"ссылок всего: {total_urls}")
    print(f"без ссылок в разделах {REQUIRED}: {len(without_url)}")
    for item in without_url:
        print("  !", item)

    if args.write:
        out = ROOT / "storage" / "source-links.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ["# Сводка источников по файлам базы", ""]
        for path in files:
            relative = path.relative_to(COMPANY).as_posix()
            urls = URL_RE.findall(path.read_text(encoding="utf-8", errors="replace"))
            if urls:
                lines.append(f"- `{relative}` — {len(urls)} ссылк.")
            else:
                lines.append(f"- `{relative}` — **без ссылок**")
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("сводка:", out.relative_to(ROOT).as_posix())

    return 1 if without_url else 0


if __name__ == "__main__":
    sys.exit(main())
