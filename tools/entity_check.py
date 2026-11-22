"""Покрытие ключевых сущностей эталона в ответе агента.

    python tools/entity_check.py benchmark-60.json N05
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from partner.agent import PartnerAgent  # noqa: E402
from partner.config import Settings  # noqa: E402
from partner.domain.agent_profile import build_profile  # noqa: E402
from partner.domain.retriever import Retriever  # noqa: E402
from partner.engine.embeddings import Embedder  # noqa: E402
from partner.engine.llm import DeepSeekClient  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

URL_RE = re.compile(r"https?://[^\s\])]+")
CODE_RE = re.compile(r"\b[A-Z]{2,}[A-Z0-9._-]{2,}\b")
NUM_RE = re.compile(r"\b\d{3,}\b")


def anchors(reference: str) -> set:
    return set(URL_RE.findall(reference) + CODE_RE.findall(reference) + NUM_RE.findall(reference))


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if not argv:
        print("укажите файл набора")
        return 1
    path = ROOT / "tools" / argv[0]
    ids = {x.strip().upper() for x in (argv[1].split(",") if len(argv) > 1 else [])}
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("questions") if isinstance(data, dict) else data

    settings = Settings.load()
    profile = build_profile(settings.data_dir)
    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    retriever = Retriever.load(
        settings.index_dir, embedder=embedder, chroma_dir=settings.chroma_dir
    )
    agent = PartnerAgent(
        retriever, settings, client=DeepSeekClient(settings), cache=None, profile=profile
    )

    for row in rows:
        if ids and str(row.get("id", "")).upper() not in ids:
            continue
        question = str(row.get("question") or "")
        reference = str(row.get("answer") or "")
        done = None
        for event in agent.run(question, show_notes=False, mode="auto", use_cache=False):
            if event.get("type") == "done":
                done = event
        answer = str((done or {}).get("text") or "")
        expected = anchors(reference)
        found = [a for a in expected if a.lower() in answer.lower()]
        missing = sorted(expected - set(found))
        coverage = len(found) / len(expected) if expected else 1.0
        print(f"{row.get('id')} покрытие={coverage:.0%} найдено={len(found)}/{len(expected)}")
        if missing:
            print("  нет в ответе:", ", ".join(missing[:6]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
