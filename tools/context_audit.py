"""Фаза 1: аудит контекста — точность, полнота, дубли, покрытие сущностей.

    python tools/context_audit.py --tops 20
"""

from __future__ import annotations

import argparse
import io
import json
import re
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

URL_RE = re.compile(r"https?://[^\s\])]+")
HEAD_RE = re.compile(r"(?m)^(?:\[([^\]]+)\]|Факт \(([^)]+)\):)")
ANCHOR_RE = re.compile(r"https?://[^\s\])]+|\b[A-Z]{2,}[A-Z0-9._-]{2,}\b|\b\d{3,}\b")
HEADER_WORD = re.compile(r"[\w-]{4,}")


def tokens(text: str) -> set:
    return {w.lower() for w in HEADER_WORD.findall(text or "")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="benchmark-60-usergate-2026-11-21.json")
    parser.add_argument("--tops", type=int, default=20)
    parser.add_argument("--out", default="tools/_context_audit.json")
    args = parser.parse_args(argv)

    data = json.loads((ROOT / "tools" / args.file).read_text(encoding="utf-8"))
    rows = data.get("questions") if isinstance(data, dict) else data
    scored = {str(item["id"]): item for item in json.loads(
        (ROOT / "tools" / "_run60_report.json").read_text(encoding="utf-8")
    )["items"]}
    rows = sorted(rows, key=lambda r: scored.get(str(r.get("id")), {}).get("score", 1.0))
    rows = rows[: args.tops]

    settings = Settings.load()
    profile = build_profile(settings.data_dir)
    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    retriever = Retriever.load(
        settings.index_dir, embedder=embedder, chroma_dir=settings.chroma_dir
    )
    client = DeepSeekClient(settings)
    agent = PartnerAgent(retriever, settings, client=client, cache=None, profile=profile)
    judge = Judge(client, enabled=True)

    report = []
    for row in rows:
        question = str(row.get("question") or "")
        reference = str(row.get("answer") or "")
        done = None
        started = time.perf_counter()
        for event in agent.run(question, show_notes=False, mode="auto", use_cache=False):
            if event.get("type") == "done":
                done = event
        seconds = time.perf_counter() - started
        answer = str((done or {}).get("text") or "")
        sources = (done or {}).get("sources") or []
        context, _ = agent._auto_context(question, show_notes=False)

        headers = [a or b for a, b in HEAD_RE.findall(context)]
        answer_urls = set(URL_RE.findall(answer))
        source_urls = {str(item.get("url") or "") for item in sources}
        cited = [url for url in source_urls if url and url in answer]
        precision = len(cited) / len(sources) if sources else 0.0
        anchors = set(ANCHOR_RE.findall(reference))
        found = [a for a in anchors if a.lower() in context.lower()]
        recall = len(found) / len(anchors) if anchors else 1.0
        duplicates = len(headers) - len(set(headers))
        verdict = judge.judge_context(question, context)
        enough = bool(getattr(verdict, "enough", False))
        relevant = bool(getattr(verdict, "relevant", False))
        noise = list(getattr(verdict, "noise", []) or [])
        context_score = (0.5 if enough else 0.0) + (0.5 if relevant else 0.0)
        context_score = max(0.0, context_score - min(0.3, 0.1 * len(noise)))

        used = (
            precision >= 0.8 and recall >= 0.7 and duplicates == 0 and context_score >= 0.7
        )
        report.append(
            {
                "id": row.get("id"),
                "question": question,
                "fragments": len(headers),
                "chars": len(context),
                "sources": len(sources),
                "cited": len(cited),
                "precision": round(precision, 2),
                "recall": round(recall, 2),
                "duplicates": duplicates,
                "context_score": round(context_score, 2),
                "seconds": round(seconds, 1),
                "ok": used,
            }
        )
        print(
            f"{row.get('id')} фр={len(headers)} prec={precision:.2f} rec={recall:.2f} "
            f"дуб={duplicates} судья={context_score:.2f} {'OK' if used else '-'}",
            flush=True,
        )

    total = len(report)
    average_precision = sum(r["precision"] for r in report) / total if total else 0
    average_recall = sum(r["recall"] for r in report) / total if total else 0
    average_score = sum(r["context_score"] for r in report) / total if total else 0
    duplicates_total = sum(r["duplicates"] for r in report)
    ok_count = sum(1 for r in report if r["ok"])
    print("\n===== ИТОГ КОНТЕКСТА =====")
    print(f"вопросов: {total} · точность {average_precision:.2f} · полнота {average_recall:.2f}")
    print(f"оценка судьи по контексту: {average_score:.2f} · дублей всего: {duplicates_total}")
    print(f"полностью годный контекст: {ok_count}/{total}")
    print(
        "фрагментов в среднем: "
        f"{sum(r['fragments'] for r in report) / total:.1f} · "
        f"символов: {sum(r['chars'] for r in report) / total:.0f}"
    )
    (ROOT / args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
