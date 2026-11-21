"""Сводка по прогону нового набора: вердикты, время, полнота по якорям."""

from __future__ import annotations

import io
import json
import pathlib
import re
import statistics
import sys
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPORT = pathlib.Path("tools/_judge_report.json")
CASE_NAMES = {"rare_fact": "редкий факт", "enumeration": "перечисление",
              "no_answer": "нет данных", "injection": "инъекция"}

ANCHOR_RE = re.compile(r"\b\d+[.,]?\d*\b|\b[A-ZА-Я]{2,}\b|\b[A-Za-z]+[0-9][A-Za-z0-9.]*\b")


def anchors(text: str) -> list[str]:
    """Значимые опоры эталона: числа, аббревиатуры, коды версий."""
    found = [item.strip(".,;:()") for item in ANCHOR_RE.findall(text or "")]
    return [item for item in dict.fromkeys(found) if len(item) >= 2][:12]


def percentile(values: list[float], share: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(share * (len(ordered) - 1))))]


def main() -> int:
    if not REPORT.is_file():
        print("нет отчёта:", REPORT)
        return 1
    rows = json.loads(REPORT.read_text(encoding="utf-8-sig"))

    verdicts = Counter(row["judge"]["verdict"] for row in rows)
    stages = Counter(row["stage"] for row in rows)
    by_cat: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        by_cat[CASE_NAMES.get(row.get("category"), row.get("category"))][row["judge"]["verdict"]] += 1

    totals = [row["timing"]["answer_s"] for row in rows if row.get("timing")]
    searches = [row["timing"]["retrieval_s"] for row in rows if row.get("timing")]

    # Полнота: доля опор эталона, найденных в ответе (когда must_contain нет).
    shares = []
    for row in rows:
        base = anchors(row.get("reference") or "")
        if not base:
            continue
        answer = (row.get("answer_text") or "").lower()
        shares.append(sum(1 for item in base if item.lower() in answer) / len(base))

    print("Вердикты:", dict(verdicts), "· всего", len(rows))
    print("Этапы:", dict(stages))
    print(f"Время ответа: p50 {percentile(totals, 0.5):.1f} с · p95 {percentile(totals, 0.95):.1f} с"
          f" · среднее {statistics.mean(totals):.1f} с")
    print(f"Поиск: p50 {percentile(searches, 0.5):.2f} с")
    if shares:
        good = sum(1 for value in shares if value >= 0.8)
        print(f"Полнота по опорам: средняя {statistics.mean(shares):.0%} · ≥80% у {good}/{len(shares)}")

    context = Counter(("достаточно" if (row.get("context_judge") or {}).get("enough") else "мало") for row in rows if row.get("context_judge"))
    print("Контекст:", dict(context))
    style_total = sum(len(row.get("style") or []) for row in rows)
    print(f"Стиль: замечаний {style_total} · без нарушений {sum(1 for r in rows if not r.get('style'))}/{len(rows)}")

    print("\nПо категориям:")
    for name, counter in by_cat.items():
        print(f"  {name:14} {dict(counter)}")

    print("\nПровалы:")
    for row in rows:
        verdict = row["judge"]["verdict"]
        if verdict == "ok":
            continue
        missing = "; ".join((row["judge"].get("missing") or [])[:2])[:70]
        print(f"  {row['id']:4} {verdict:8} {row['stage']:10} {row['timing']['answer_s']:5.1f} с  {missing}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
