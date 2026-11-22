"""Проверка третьего набора: структура и отсутствие повторов с двумя предыдущими."""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"D:\hacaton\partner-agent-temp\tests")
NEW = BASE / "benchmark-60-usergate-2026-11-21-v2.json"
OLD = [
    BASE / "golden-questions-usergate-2026-11-20.json",
    BASE / "benchmark-60-usergate-2026-11-21.json",
]

new = json.loads(NEW.read_text(encoding="utf-8"))
items = new["questions"]
print("вопросов:", len(items))
print("категории:", dict(Counter(i["category"] for i in items)))
print("in_base:", dict(Counter(i["in_base"] for i in items)))
print("дубли id:", [k for k, v in Counter(i["id"] for i in items).items() if v > 1] or "нет")

problems = []
for item in items:
    for field in ("id", "category", "product", "in_base", "question", "answer", "source"):
        if field not in item or item[field] in ("", None):
            problems.append(f"{item.get('id')}: поле {field}")
    if len(item["question"]) < 30:
        problems.append(f"{item['id']}: короткий вопрос")
    if len(item["answer"]) < 50:
        problems.append(f"{item['id']}: короткий ответ")
print("проблемы структуры:", problems or "нет")


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"\w{4,}", text.lower())}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


print("\nпересечения с предыдущими наборами:")
total_overlaps = 0
for path in OLD:
    previous = json.loads(path.read_text(encoding="utf-8"))["questions"]
    hits = []
    for item in items:
        for old_item in previous:
            score = jaccard(tokens(item["question"]), tokens(old_item["question"]))
            if score > 0.45:
                hits.append((round(score, 2), item["id"], old_item["id"], item["question"][:55]))
    total_overlaps += len(hits)
    print(f"  {path.name}: {len(hits)}")
    for row in hits:
        print("    ", row)
print("всего пересечений:", total_overlaps)
