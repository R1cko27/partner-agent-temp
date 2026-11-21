"""Судья третьего уровня: кандидаты поиска + определение этапа провала."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")
TOOL = pathlib.Path("tools/judge_benchmark.py")

CANDIDATES_METHOD = '''    def candidates(self, question: str, limit: int = 8) -> List[Dict[str, Any]]:
        """Кандидаты поиска до сборки контекста — для контроля судьёй.

        Позволяет отличить провал поиска (факта нет в кандидатах) от провала
        отбора (факт есть, но не попал в контекст) и от провала генерации.
        """
        if _looks_like_injection(question):
            return []
        result: List[Dict[str, Any]] = []
        for hit in self._search_hits(question, max(limit, 6))[:limit]:
            text = str(hit.chunk.get("text") or "")
            result.append(
                {
                    "id": hit.chunk.get("id"),
                    "kind": hit.chunk.get("kind"),
                    "title": hit.chunk.get("title"),
                    "source": hit.chunk.get("source"),
                    "score": round(float(hit.score), 4),
                    "excerpt": _clip(text, 300),
                }
            )
        return result

'''


def patch_agent() -> None:
    text = AGENT.read_text(encoding="utf-8")
    if "def candidates(" in text:
        print("агент: метод candidates уже есть")
        return
    anchor = "    def _search_hits(self, question: str, k: int) -> List[SearchHit]:"
    text = text.replace(anchor, CANDIDATES_METHOD + anchor, 1)
    AGENT.write_text(text, encoding="utf-8")
    print("агент: добавлен метод candidates")


def patch_tool() -> None:
    text = TOOL.read_text(encoding="utf-8")
    if "judge_candidates" in text:
        print("прогон: уже использует судью кандидатов")
        return

    text = text.replace(
        "from partner.engine.judge import Judge",
        "from partner.engine.judge import Judge",
    )

    # 1. кандидаты до ответа
    old_start = '''        started = time.perf_counter()
        done: Dict[str, Any] = {}'''
    new_start = '''        started = time.perf_counter()
        candidates = agent.candidates(case["question"], limit=8)
        candidate_verdict = judge.judge_candidates(case["question"], candidates)
        done: Dict[str, Any] = {}'''
    if old_start in text:
        text = text.replace(old_start, new_start, 1)

    # 2. этап провала и поля отчёта
    old_row = '''        row = {
            **case,
            "answer_text": answer,
            "judge": verdict.as_dict(),'''
    new_row = '''        # Где потерялся факт: поиск → отбор в контекст → генерация.
        stage = "ok"
        if verdict.verdict != "ok":
            if not candidate_verdict.answer_in_candidates:
                stage = "поиск"
            else:
                best = candidate_verdict.best_index
                best_id = candidates[best - 1].get("id") if 0 < best <= len(candidates) else None
                context_ids = {item.get("id") for item in (sources or [])}
                stage = "отбор" if best_id and best_id not in context_ids else "генерация"

        row = {
            **case,
            "answer_text": answer,
            "judge": verdict.as_dict(),
            "candidate_judge": candidate_verdict.as_dict(),
            "candidates": candidates,
            "stage": stage,'''
    if old_row in text:
        text = text.replace(old_row, new_row, 1)

    # 3. контекст нужен и для этапа, и для отчёта
    old_ctx = '''        context = ""
        context_verdict = None
        if not args.no_context:'''
    new_ctx = '''        context = ""
        sources: List[Dict[str, Any]] = []
        context_verdict = None
        if not args.no_context:'''
    if old_ctx in text:
        text = text.replace(old_ctx, new_ctx, 1)

    # 4. печать колонки «этап»
    old_print = '''        style_note = f" · стиль: {len(style)} наруш." if style else " · стиль: ok"'''
    new_print = '''        style_note = f" · стиль: {len(style)} наруш." if style else " · стиль: ok"
        stage_note = "" if stage == "ok" else f" · этап: {stage}"'''
    if old_print in text:
        text = text.replace(old_print, new_print, 1)
    text = text.replace(
        "{extra}{style_note}\")",
        "{extra}{style_note}{stage_note}\")",
    )

    # 5. сводка по этапам
    old_sum = '''    contexts = [row["context_judge"] for row in report if row["context_judge"]]'''
    new_sum = '''    stages: Dict[str, int] = {}
    for row in report:
        stages[row.get("stage", "ok")] = stages.get(row.get("stage", "ok"), 0) + 1
    if any(key != "ok" for key in stages):
        print("Этап провала:", ", ".join(f"{key} — {value}" for key, value in sorted(stages.items())))
    contexts = [row["context_judge"] for row in report if row["context_judge"]]'''
    if old_sum in text:
        text = text.replace(old_sum, new_sum, 1)

    TOOL.write_text(text, encoding="utf-8")
    print("прогон: добавлены кандидаты, этап провала и сводка")


def main() -> int:
    patch_agent()
    patch_tool()
    return 0


if __name__ == "__main__":
    sys.exit(main())
