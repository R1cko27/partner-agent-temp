"""Обновляет глоссарий в готовом индексе без полной пересборки.

Полная сборка (`py ingest.py`) делает то же самое, но идёт несколько минут.
Этот скрипт перечитывает только страницы глоссария и переписывает
`storage/index/entities.json`, добавляя поле `glossary`.

    python tools/refresh_glossary.py
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from partner.config import Settings
from partner.domain.entities import _glossary_entries, _is_glossary
from partner.domain.sources import read_file


def main() -> int:
    settings = Settings.load()
    data_dir = settings.data_dir
    entities_path = settings.index_dir / "entities.json"
    if not entities_path.is_file():
        print(f"нет файла {entities_path} — сначала соберите индекс: py ingest.py")
        return 1

    payload = json.loads(entities_path.read_text(encoding="utf-8"))
    entries = []
    found = 0
    for path in sorted(data_dir.rglob("*.md")):
        try:
            source = read_file(path, data_dir)
        except Exception:  # noqa: BLE001 — битый файл не должен ломать обновление
            continue
        if not _is_glossary(source):
            continue
        found += 1
        for entry in _glossary_entries(source.text):
            entry["source"] = source.origin
            entries.append(entry)

    if not entries:
        print("страницы глоссария не найдены — проверьте, что docs/crawl содержит глоссарий")
        return 1

    payload["glossary"] = entries
    entities_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"страниц глоссария: {found} · терминов: {len(entries)}")
    print(f"обновлён {entities_path}")
    for entry in entries[:5]:
        print(f"  {entry['term'][:34]:36} {entry['definition'][:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
