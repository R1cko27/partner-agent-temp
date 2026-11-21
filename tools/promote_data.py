"""Перенос собранных материалов из data-temp в data/company.

Источники (что переносим):
  data-temp/09-company/docs/**            — обход документации и основного сайта
  data-temp/02-media/telegram/*.md        — посты Telegram
  data-temp/02-media/vk/*.md              — посты VK
  data-temp/02-media/habr/*.md            — статьи Habr

Куда:
  data/company/docs/crawl/<продукт>/…     — тип «документ», полный текст
  data/company/docs/crawl/habr/…          — статьи, полный текст
  data/company/news/social/<сеть>-…md     — тип «новость», короткие посты с датой

Не переносим: CSV-каталоги, реестры обхода, шаблоны, файлы _пример.md и
site-map-*.md — они остаются рабочим инструментом в data-temp.
"""

from __future__ import annotations

import csv
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMP = ROOT / "data-temp"
DATA = ROOT / "data" / "company"

CRAWL_SRC = TEMP / "09-company" / "docs"
CRAWL_DST = DATA / "docs" / "crawl"
NEWS_DST = DATA / "news" / "social"

SKIP_NAMES = {"_пример.md"}


def is_skip(path: Path) -> bool:
    return path.name in SKIP_NAMES or path.name.startswith("site-map-")


def move_many(src: Path, dst: Path, prefix: str = "") -> int:
    """Переносит .md файлы, сохраняя вложенность; возвращает число перенесённых."""
    if not src.is_dir():
        print(f"  нет папки {src.relative_to(ROOT)}")
        return 0
    moved = 0
    for path in sorted(src.rglob("*.md")):
        if is_skip(path):
            continue
        relative = path.relative_to(src)
        target = dst / (prefix + relative.name if prefix else relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(target))
        moved += 1
    return moved


def main() -> int:
    if not DATA.is_dir():
        print("нет data/company")
        return 1

    print("=== перенос материалов ===")
    crawl = move_many(CRAWL_SRC, CRAWL_DST)
    print(f"  обход сайтов      → docs/crawl/            {crawl}")

    telegram = move_many(TEMP / "02-media" / "telegram", NEWS_DST, prefix="telegram-")
    print(f"  Telegram          → news/social/           {telegram}")

    vk = move_many(TEMP / "02-media" / "vk", NEWS_DST, prefix="vk-")
    print(f"  VK                → news/social/           {vk}")

    habr = move_many(TEMP / "02-media" / "habr", CRAWL_DST / "habr")
    print(f"  Habr              → docs/crawl/habr/       {habr}")

    # Реестры обхода должны указывать на новое место файлов.
    print("\n=== обновление путей в реестрах ===")
    replaced = 0
    for report in (TEMP / "00-meta").glob("crawl-report-*.csv"):
        rows = list(csv.DictReader(report.open(encoding="utf-8", newline=""), delimiter=";"))
        if not rows:
            continue
        columns = list(rows[0].keys())
        for row in rows:
            old = row.get("файл", "")
            if old.startswith("data-temp/09-company/docs/"):
                row["файл"] = old.replace("data-temp/09-company/docs/", "data/company/docs/crawl/", 1)
                replaced += 1
        with report.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
        print(f"  {report.name}")
    print(f"  обновлено путей: {replaced}")

    print("\n=== остаток в data-temp/09-company/docs ===")
    left = [p for p in CRAWL_SRC.rglob("*") if p.is_file()] if CRAWL_SRC.is_dir() else []
    for path in left:
        print(f"  {path.relative_to(ROOT)}")
    print(f"  файлов всего: {len(left)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
