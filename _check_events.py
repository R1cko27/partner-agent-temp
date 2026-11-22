"""Проверка events.csv: колонки и отсутствие повторов по url/названию."""
from __future__ import annotations

import csv
import sys
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PATH = r"D:\hacaton\partner-agent-temp\data-temp\06-events\events.csv"
rows = list(csv.reader(open(PATH, encoding="utf-8-sig"), delimiter=";"))
print("строк:", len(rows))
print("колонок:", dict(Counter(len(r) for r in rows)))
print("битые:", [(i + 1, len(r)) for i, r in enumerate(rows) if len(r) != 11])
print("дубли url:", [u for u, c in Counter(r[7] for r in rows[1:]).items() if c > 1] or "нет")
print("дубли названий:", [n for n, c in Counter(r[3] for r in rows[1:]).items() if c > 1] or "нет")
print("статусы:", dict(Counter(r[10] for r in rows[1:])))
print("типы:", dict(Counter(r[4] for r in rows[1:])))
print()
for r in rows[1:]:
    print(f"  {r[0]:14} {r[1]:12} {r[4]:10} {r[3][:58]}")
