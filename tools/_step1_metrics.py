"""Шаг 1: время по этапам и полнота ответа в прогоне судьи."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TOOL = pathlib.Path("tools/judge_benchmark.py")

# 1. тащим must_contain из набора
OLD_CASE = '''        cases.append(
            {
                "id": str(row.get("id") or f"#{len(cases)+1}"),
                "question": str(row.get("question") or ""),
                "reference": str(row.get("answer") or ""),
                "behavior": behavior,
                "category": str(row.get("category") or ""),
            }
        )'''
NEW_CASE = '''        must = [str(item) for item in (row.get("must_contain") or []) if str(item).strip()]
        cases.append(
            {
                "id": str(row.get("id") or f"#{len(cases)+1}"),
                "question": str(row.get("question") or ""),
                "reference": str(row.get("answer") or ""),
                "behavior": behavior,
                "category": str(row.get("category") or ""),
                "must": must,
            }
        )'''

# 2. замеры по этапам
OLD_START = '''        started = time.perf_counter()
        candidates = agent.candidates(case["question"], limit=8)'''
NEW_START = '''        started = time.perf_counter()
        t_retr = time.perf_counter()
        candidates = agent.candidates(case["question"], limit=8)
        t_retrieval = time.perf_counter() - t_retr'''

OLD_CTX = '''        if not args.no_context:
            context, sources = agent._auto_context(case["question"], True)'''
NEW_CTX = '''        t_ctx = time.perf_counter()
        if not args.no_context:
            context, sources = agent._auto_context(case["question"], True)
        t_context = time.perf_counter() - t_ctx'''

# 3. полнота и времена в строке отчёта
OLD_ROW = '''        row = {
            **case,
            "answer_text": answer,
            "judge": verdict.as_dict(),
            "candidate_judge": candidate_verdict.as_dict(),'''
NEW_ROW = '''        # Полнота: доля обязательных элементов эталона, попавших в ответ.
        must = case.get("must") or []
        covered = [item for item in must if item.lower() in answer.lower()]
        completeness = round(len(covered) / len(must), 2) if must else None
        t_total = time.perf_counter() - started

        row = {
            **case,
            "answer_text": answer,
            "judge": verdict.as_dict(),
            "completeness": completeness,
            "missing_must": [item for item in must if item not in covered],
            "timing": {
                "retrieval_s": round(t_retrieval, 2),
                "context_s": round(t_context, 2),
                "total_s": round(t_total, 2),
            },
            "candidate_judge": candidate_verdict.as_dict(),'''

# 4. компактная строка печати
OLD_PRINT = '''        style_note = f" · стиль: {len(style)} наруш." if style else " · стиль: ok"'''
NEW_PRINT = '''        style_note = (
            f" · полн. {completeness:.0%} · {t_total:.1f} с" if completeness is not None
            else f" · {t_total:.1f} с"
        )'''

# 5. сводка: p50/p95 и полнота
OLD_SUM = '''    style_total = sum(len(row.get("style") or []) for row in report)'''
NEW_SUM = '''    def percentile(values, share):
        if not values:
            return 0.0
        ordered = sorted(values)
        index = min(len(ordered) - 1, int(round(share * (len(ordered) - 1))))
        return ordered[index]

    totals = [row["timing"]["total_s"] for row in report if row.get("timing")]
    retrievals = [row["timing"]["retrieval_s"] for row in report if row.get("timing")]
    completes = [row["completeness"] for row in report if row.get("completeness") is not None]
    if totals:
        print(
            f"Время: p50 {percentile(totals, 0.5):.1f} с · p95 {percentile(totals, 0.95):.1f} с"
            f" · поиск p50 {percentile(retrievals, 0.5):.2f} с"
        )
    if completes:
        good = sum(1 for value in completes if value >= 0.9)
        print(
            f"Полнота: средняя {sum(completes)/len(completes):.0%}"
            f" · ≥90% у {good}/{len(completes)}"
        )
    style_total = sum(len(row.get("style") or []) for row in report)'''

EDITS = [
    (OLD_CASE, NEW_CASE, "must_contain в наборе"),
    (OLD_START, NEW_START, "замер поиска"),
    (OLD_CTX, NEW_CTX, "замер контекста"),
    (OLD_ROW, NEW_ROW, "полнота и времена"),
    (OLD_PRINT, NEW_PRINT, "печать"),
    (OLD_SUM, NEW_SUM, "сводка p50/p95"),
]


def main() -> int:
    text = TOOL.read_text(encoding="utf-8")
    if "percentile(" in text and "completeness" in text:
        print("шаг 1 уже применён")
        return 0
    applied = []
    for old, new, label in EDITS:
        if old in text:
            text = text.replace(old, new, 1)
            applied.append(label)
        else:
            print("не найден фрагмент:", label)
    TOOL.write_text(text, encoding="utf-8")
    print("применено:", ", ".join(applied))
    return 0


if __name__ == "__main__":
    sys.exit(main())
