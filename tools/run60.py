"""Прогон полного файла вопросов с судьёй по всем критериям.

    python tools/run60.py benchmark-60-usergate-2026-11-21.json
"""

from __future__ import annotations

import io
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from partner.agent import PartnerAgent  # noqa: E402
from partner.config import Settings  # noqa: E402
from partner.domain.agent_profile import build_profile  # noqa: E402
from partner.domain.retriever import Retriever  # noqa: E402
from partner.engine.embeddings import Embedder  # noqa: E402
from partner.engine.judge import Judge  # noqa: E402
from partner.engine.llm import DeepSeekClient  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CRITERIA = ("completeness", "sources", "format", "followups", "context")


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    name = argv[0] if argv else "benchmark-60-usergate-2026-11-21.json"
    candidate = ROOT / "tools" / name
    if not candidate.exists():
        candidate = ROOT / name
    data = json.loads(candidate.read_text(encoding="utf-8"))
    rows = data.get("questions") if isinstance(data, dict) else data
    limit = 0
    for arg in argv[1:]:
        if arg.startswith("--limit=") or (limit == 0 and arg.isdigit()):
            value = arg.split("=", 1)[-1]
            if value.isdigit():
                limit = int(value)
    if limit and limit < len(rows):
        import random
        random.seed(2026)
        rows = random.sample(rows, limit)

    settings = Settings.load()
    profile = build_profile(settings.data_dir)
    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    retriever = Retriever.load(
        settings.index_dir, embedder=embedder, chroma_dir=settings.chroma_dir
    )
    client = DeepSeekClient(settings)
    agent = PartnerAgent(retriever, settings, client=client, cache=None, profile=profile)
    judge = Judge(client, enabled=True)

    groups: dict[str, list[float]] = defaultdict(list)
    criteria_sum = {key: 0.0 for key in CRITERIA}
    scores: list[float] = []
    durations: list[float] = []
    passed = 0
    report = []

    for index, row in enumerate(rows, 1):
        question = str(row.get("question") or "")
        reference = str(row.get("answer") or "")
        done = None
        started = time.perf_counter()
        for event in agent.run(question, show_notes=False, mode="auto", use_cache=False):
            if event.get("type") == "done":
                done = event
        duration = time.perf_counter() - started
        answer = str((done or {}).get("text") or "")
        sources = (done or {}).get("sources") or []
        followups = (done or {}).get("followups") or []
        context, _ = agent._auto_context(question, show_notes=False)
        verdict = (
            judge.judge_full(question, reference, answer, sources, followups, context)
            if reference
            else {}
        )
        score = float((verdict or {}).get("overall") or 0)
        problems = [str(item) for item in (verdict or {}).get("problems") or []]
        scores.append(score)
        durations.append(duration)
        group = str(row.get("category") or row.get("topic") or "без группы")
        groups[group].append(score)
        for key in CRITERIA:
            try:
                criteria_sum[key] += float((verdict or {}).get(key) or 0)
            except (TypeError, ValueError):
                pass
        ok = score >= 0.8 and not problems and bool(answer.strip())
        if ok:
            passed += 1
        report.append(
            {
                "id": row.get("id"),
                "group": group,
                "question": question,
                "score": round(score, 2),
                "problems": problems[:3],
                "seconds": round(duration, 1),
                "followups": len(followups),
                "context_chars": len(context),
            }
        )
        print(f"{index:2}/{len(rows)} {row.get('id')} {score:.2f} {duration:4.1f} c {group[:24]}", flush=True)

    total = len(rows)
    average = sum(scores) / total if total else 0.0
    ordered = sorted(durations)
    print("\n===== СВОДКА =====")
    print(f"вопросов: {total} · средняя оценка: {average:.2f} · прошло (>=0.8 без замечаний): {passed}")
    print("по критериям:", {k: round(v / total, 2) for k, v in criteria_sum.items()})
    print(f"время: среднее {average and sum(durations)/total:.1f} c · медиана {ordered[len(ordered)//2]:.1f} c · максимум {max(durations):.1f} c")
    print("\nпо группам:")
    for group, values in sorted(groups.items(), key=lambda x: -len(x[1])):
        print(f"  {group[:32]:32} n={len(values):2} средняя={sum(values)/len(values):.2f} прошло={sum(1 for v in values if v >= 0.8)}")
    (ROOT / "tools" / "_run60_report.json").write_text(
        json.dumps(
            {"average": round(average, 3), "passed": passed, "total": total, "items": report},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
