"""Цикл контроля качества: берём только нерешённые вопросы, ведём реестр.

    python tools/qa_cycle.py            # следующие 15 нерешённых
    python tools/qa_cycle.py --reset    # сбросить реестр
"""

from __future__ import annotations

import argparse
import time
import io
import json
import random
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.quality_gate import (  # noqa: E402
    check_context,
    check_followups,
    check_format,
    check_sources,
)

from partner.agent import PartnerAgent  # noqa: E402
from partner.config import Settings  # noqa: E402
from partner.domain.agent_profile import build_profile  # noqa: E402
from partner.domain.retriever import Retriever  # noqa: E402
from partner.engine.embeddings import Embedder  # noqa: E402
from partner.engine.judge import Judge  # noqa: E402
from partner.engine.llm import DeepSeekClient  # noqa: E402

STATE = ROOT / "tools" / "_qa_state.json"
HISTORY = ROOT / "tools" / "_qa_history.json"
THRESHOLD = 0.9
BENCH = [
    "benchmark-60-usergate-2026-11-21.json",
    "benchmark-60.json",
    "benchmark-60_2.json",
    "benchmark-60-v2.json",
    "benchmark-testers-7.json",
]


def sources_relevant(judge, question: str, answer: str, sources: list) -> bool:
    """Судья: подтверждают ли перечисленные страницы содержание ответа."""
    titles = "; ".join(
        f"{item.get('title') or ''} {item.get('url') or ''}"[:120] for item in sources
    )
    if not titles:
        return False
    raw = judge._ask(
        "Ты проверяешь источники ответа. Ответь JSON: {\"relevant\": true|false}.",
        f"ВОПРОС:\n{question}\n\nОТВЕТ:\n{answer[:1200]}\n\nСТРАНИЦЫ:\n{titles}",
    )
    return bool(raw.get("relevant"))


def load_questions() -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for name in BENCH:
        path = ROOT / "tools" / name
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data.get("questions") if isinstance(data, dict) else data
        for row in rows:
            qid = str(row.get("id") or "").strip()
            if not qid:
                continue
            key = f"{name.split('-')[-1].replace('.json','')}:{qid}"
            result[key] = {
                "id": qid,
                "file": name,
                "question": str(row.get("question") or "").strip(),
                "answer": str(row.get("answer") or ""),
                "topic": str(row.get("category") or row.get("topic") or ""),
            }
    return result


def load_state() -> Dict[str, Dict[str, Any]]:
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {}


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args(argv)

    if args.reset and STATE.exists():
        STATE.unlink()

    questions = load_questions()
    state = load_state()
    pending = [
        key
        for key, meta in questions.items()
        if "академ" not in meta["question"].lower() or True
    ]
    resolved = {key for key, meta in state.items() if meta.get("status") == "pass"}
    candidates = [key for key in pending if key not in resolved]
    random.seed(42)
    random.shuffle(candidates)
    selected = candidates[: args.limit]

    settings = Settings.load()
    profile = build_profile(settings.data_dir)
    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    retriever = Retriever.load(
        settings.index_dir, embedder=embedder, chroma_dir=settings.chroma_dir
    )
    client = DeepSeekClient(settings)
    agent = PartnerAgent(retriever, settings, client=client, cache=None, profile=profile)
    judge = Judge(client, enabled=True)

    scores: List[float] = []
    durations: List[float] = []
    passed = 0
    for key in selected:
        meta = questions[key]
        question = meta["question"]
        started = time.perf_counter()
        done = None
        for event in agent.run(question, show_notes=False, mode="auto", use_cache=False):
            if event.get("type") == "done":
                done = event
        durations.append(time.perf_counter() - started)
        answer = str((done or {}).get("text") or "")
        context_text, _ = agent._auto_context(question, show_notes=False)
        sources = (done or {}).get("sources") or []
        followups = (done or {}).get("followups") or []

        problems = {
            "format": check_format(answer),
            "sources": check_sources(sources, question, answer),
            "followups": check_followups(followups, question),
            "context": check_context(context_text, question),
        }
        if problems["sources"] and sources and all(
            "не по теме" in item for item in problems["sources"]
        ):
            if sources_relevant(judge, question, answer, sources):
                problems["sources"] = []
        verdict = (
            judge.judge_full(
                question, meta["answer"], answer, sources, followups, context_text
            )
            if meta["answer"]
            else {}
        )
        score = float((verdict or {}).get("overall") or 0)
        judge_problems = [str(item) for item in (verdict or {}).get("problems") or []]
        scores.append(score)
        hard_format = any(
            marker in item
            for item in problems["format"]
            for marker in ("пустой ответ", "нет заголовка")
        )
        clean = (
            score >= 0.8
            and bool(answer.strip())
            and not hard_format
            and not judge_problems
        )
        if clean:
            passed += 1
        state[key] = {
            "status": "pass" if clean else "fail",
            "score": score,
            "problems": {k: v for k, v in problems.items() if v},
        }
        flags = "; ".join(
            list(problems["format"]) + judge_problems + sum(
                [v for k, v in problems.items() if k != "format"], []
            )
        )[:120]
        print(f"{key} {'OK' if clean else 'FAIL'} судья={score:.2f} | {question[:60]} | {flags}", flush=True)

    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    average = sum(scores) / len(scores) if scores else 0.0
    history = []
    if HISTORY.exists():
        history = json.loads(HISTORY.read_text(encoding="utf-8"))
    history.append({"average": round(average, 3), "passed": passed, "total": len(selected)})
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    ready = average > THRESHOLD
    print(f"\nПРОЙДЕНО: {passed}/{len(selected)} · средняя оценка судьи: {average:.2f}")
    if durations:
        ordered = sorted(durations)
        print(f"ВРЕМЯ: среднее {sum(durations)/len(durations):.1f} c · медиана {ordered[len(ordered)//2]:.1f} c · максимум {max(durations):.1f} c")
    print(f"ПОРОГ ДЛЯ ФИНАЛЬНЫХ 60: {THRESHOLD} · пока {'ДОСТИГНУТ' if ready else 'НЕ достигнут'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
