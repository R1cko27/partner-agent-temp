"""Оценка контекста на фиксированном наборе вопросов.

    python tools/ctx_eval.py E02 R07 R16 R21 N06 R33
"""

from __future__ import annotations

import io
import json
import sys
import time
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

DEFAULT_IDS = ["E02", "R07", "R16", "R21", "N06", "R33"]


def main() -> int:
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or DEFAULT_IDS
    source = ROOT / "tools" / "benchmark-60-usergate-2026-11-21.json"
    for arg in sys.argv[1:]:
        if arg.startswith("--file="):
            source = ROOT / arg.split("=", 1)[1]
    rows = json.loads(source.read_text(encoding="utf-8"))["questions"]
    by_id = {str(row["id"]): row for row in rows}

    settings = Settings.load()
    profile = build_profile(settings.data_dir)
    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    retriever = Retriever.load(
        settings.index_dir, embedder=embedder, chroma_dir=settings.chroma_dir
    )
    client = DeepSeekClient(settings)
    agent = PartnerAgent(retriever, settings, client=client, cache=None, profile=profile)
    judge = Judge(client, enabled=True)

    context_scores, overall_scores, lengths = [], [], []
    for qid in ids:
        row = by_id[qid]
        started = time.perf_counter()
        done = None
        for event in agent.run(row["question"], show_notes=False, mode="auto", use_cache=False):
            if event.get("type") == "done":
                done = event
        seconds = time.perf_counter() - started
        answer = str((done or {}).get("text") or "")
        context, _ = agent._auto_context(row["question"], show_notes=False)
        verdict = judge.judge_full(
            row["question"],
            row.get("answer") or "",
            answer,
            (done or {}).get("sources") or [],
            (done or {}).get("followups") or [],
            context,
        )
        ctx = float(verdict.get("context") or 0)
        overall = float(verdict.get("overall") or 0)
        context_scores.append(ctx)
        overall_scores.append(overall)
        lengths.append(len(context))
        print(
            f"{qid:5} ctx={ctx:.2f} overall={overall:.2f} фрагм={len((done or {}).get('sources') or [])} "
            f"симв={len(context)} {seconds:.1f}c"
        )

    total = len(ids)
    print(
        f"\nИТОГО: context={sum(context_scores)/total:.2f} "
        f"overall={sum(overall_scores)/total:.2f} "
        f"средний контекст={sum(lengths)//total} символов"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
