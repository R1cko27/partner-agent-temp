"""Прогон набора вопросов с моделью-судьёй: ответ + качество контекста.

    python tools/judge_benchmark.py --file benchmark-60-v2.json --limit 12
    python tools/judge_benchmark.py --file benchmark-60-v2.json --no-context

Для каждого вопроса:
1. агент отвечает без кеша;
2. судья сравнивает ответ с эталоном (`judge_answer`);
3. отдельно судья оценивает контекст, который получила модель (`judge_context`).

Отчёт: `tools/_judge_report.json`.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from partner.agent import PartnerAgent
from partner.config import Settings
from partner.domain.agent_profile import build_profile
from partner.domain.retriever import Retriever
from partner.engine.embeddings import Embedder
from partner.engine.judge import Judge
from partner.engine.style_lint import style_lint
from partner.engine.llm import DeepSeekClient


def load_cases(path: Path) -> List[Dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload["questions"] if isinstance(payload, dict) else payload
    cases: List[Dict[str, Any]] = []
    for row in rows:
        behavior = str(row.get("expected_behavior") or "")
        if not behavior:
            behavior = {
                "rare_fact": "answer",
                "product_fact": "answer",
                "enumeration": "answer",
                "no_answer": "say_no_data",
                "no_data": "say_no_data",
                "injection": "refuse",
            }.get(str(row.get("category") or ""), "answer")
        cases.append(
            {
                "id": str(row.get("id") or f"#{len(cases)+1}"),
                "question": str(row.get("question") or ""),
                "reference": str(row.get("answer") or ""),
                "behavior": behavior,
                "category": str(row.get("category") or ""),
            }
        )
    return cases


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Прогон с моделью-судьёй")
    parser.add_argument("--file", default="benchmark-60-v2.json")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--no-context", action="store_true", help="не оценивать контекст")
    parser.add_argument("--ids", default="", help="ids через запятую")
    args = parser.parse_args(argv)

    settings = Settings.load()
    profile = build_profile(settings.data_dir)
    retrieval = profile.retrieval
    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    retriever = Retriever.load(settings.index_dir, embedder=embedder, chroma_dir=settings.chroma_dir)
    retriever.set_dedupe(retrieval.max_per_doc, retrieval.dedupe_threshold, retrieval.dedupe)
    retriever.set_kind_weights(retrieval.kind_weights)
    retriever.set_channel_weights(retrieval.channel_weights)
    retriever.set_secondary_kinds(retrieval.secondary_kinds)
    client = DeepSeekClient(settings)
    agent = PartnerAgent(retriever, settings, client=client, cache=None, profile=profile)
    judge = Judge(client, enabled=True)

    path = ROOT / "tools" / args.file
    cases = load_cases(path)
    wanted = {item.strip().upper() for item in args.ids.split(",") if item.strip()}
    if wanted:
        cases = [case for case in cases if case["id"].upper() in wanted]
    if args.limit:
        cases = cases[: args.limit]
    print(f"набор: {path.name} · вопросов: {len(cases)} · контекст оценивается: {not args.no_context}")

    report: List[Dict[str, Any]] = []
    for index, case in enumerate(cases, 1):
        started = time.perf_counter()
        candidates = agent.candidates(case["question"], limit=8)
        candidate_verdict = judge.judge_candidates(case["question"], candidates)
        done: Dict[str, Any] = {}
        for event in agent.run(
            case["question"], history=[], show_notes=True, use_cache=False, mode="auto"
        ):
            if event.get("type") == "done":
                done = event
        answer = str(done.get("text") or "")
        context = ""
        sources: List[Dict[str, Any]] = []
        context_verdict = None
        if not args.no_context:
            context, sources = agent._auto_context(case["question"], True)
            expect_absent = case["behavior"] in ("say_no_data", "refuse")
            context_verdict = judge.judge_context(
                case["question"], context, expect_absent=expect_absent
            )
        verdict = judge.judge_answer(case["question"], case["reference"], answer, context)
        style = style_lint(answer, case["question"], expects_absent=case["behavior"] != "answer")

        # Где потерялся факт: поиск → отбор в контекст → генерация.
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
            "stage": stage,
            "style": [issue.as_dict() for issue in style],
            "context_judge": context_verdict.as_dict() if context_verdict else None,
            "seconds": round(time.perf_counter() - started, 1),
        }
        report.append(row)

        flag = {"ok": "OK  ", "partial": "PART", "wrong": "WRNG", "invented": "INV "}.get(
            verdict.verdict, "?   "
        )
        extra = ""
        if context_verdict is not None:
            extra = (
                f" · контекст: {'достаточно' if context_verdict.enough else 'мало'}"
                f"{'/шум' if not context_verdict.relevant else ''}"
            )
        style_note = f" · стиль: {len(style)} наруш." if style else " · стиль: ok"
        stage_note = "" if stage == "ok" else f" · этап: {stage}"
        print(f"  {index:2}. {case['id']:5} {flag} {verdict.score:4.2f} {verdict.comment[:44]}{extra}{style_note}{stage_note}")

    out = ROOT / "tools" / "_judge_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    # Копия по имени набора: иначе следующий запуск затирает предыдущий отчёт.
    extra = ROOT / "tools" / f"_judge_{path.stem}.json"
    extra.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    total = len(report)
    ok = sum(1 for row in report if row["judge"]["verdict"] == "ok")
    partial = sum(1 for row in report if row["judge"]["verdict"] == "partial")
    wrong = sum(1 for row in report if row["judge"]["verdict"] == "wrong")
    invented = sum(1 for row in report if row["judge"]["verdict"] == "invented")
    print(f"\nОтветы: ok {ok} · частично {partial} · неверно {wrong} · выдумки {invented} · всего {total}")
    style_total = sum(len(row.get("style") or []) for row in report)
    clean_style = sum(1 for row in report if not row.get("style"))
    print(f"Стиль: без нарушений {clean_style}/{total} · всего замечаний {style_total}")
    stages: Dict[str, int] = {}
    for row in report:
        stages[row.get("stage", "ok")] = stages.get(row.get("stage", "ok"), 0) + 1
    if any(key != "ok" for key in stages):
        print("Этап провала:", ", ".join(f"{key} — {value}" for key, value in sorted(stages.items())))
    contexts = [row["context_judge"] for row in report if row["context_judge"]]
    if contexts:
        enough = sum(1 for item in contexts if item["enough"])
        relevant = sum(1 for item in contexts if item["relevant"])
        print(f"Контекст: достаточно {enough}/{len(contexts)} · по теме {relevant}/{len(contexts)}")
        noisy = [row["id"] for row in report if row["context_judge"] and not row["context_judge"]["relevant"]]
        if noisy:
            print("Шумный контекст:", ", ".join(noisy[:8]))
    print("отчёт:", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
