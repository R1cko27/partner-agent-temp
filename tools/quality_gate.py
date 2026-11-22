"""Контроль качества ответов: полнота, источники, формат, кнопки, контекст.

    python tools/quality_gate.py --file benchmark-testers-7.json
    python tools/quality_gate.py --file benchmark-60-usergate-2026-11-21.json --ids R11,R16,R29
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from partner.agent import PartnerAgent  # noqa: E402
from partner.config import Settings  # noqa: E402
from partner.domain.agent_profile import build_profile  # noqa: E402
from partner.domain.retriever import Retriever  # noqa: E402
from partner.engine.embeddings import Embedder  # noqa: E402
from partner.engine.judge import Judge  # noqa: E402
from partner.engine.llm import DeepSeekClient  # noqa: E402

WORD_RE = re.compile(r"[А-Яа-яA-Za-z0-9-]{4,}")
STOP = {
    "какие", "какой", "какая", "каких", "сколько", "входит", "нужно", "можно",
    "расскажи", "подробнее", "почему", "зачем", "этого", "этот", "есть",
    "какая", "какие",
}
OFFICIAL_HOSTS = {
    "usergate.com", "www.usergate.com", "docs.usergate.com",
    "academy.usergate.com", "static.usergate.com",
}


def keywords(text: str) -> set:
    return {w.lower() for w in WORD_RE.findall(text or "")} - STOP


def check_format(answer: str) -> List[str]:
    problems: List[str] = []
    text = answer or ""
    if not text.strip():
        return ["пустой ответ"]
    if not re.search(r"(?m)^##\s+\S", text):
        problems.append("нет заголовка ##")
    if len(re.findall(r"\*\*", text)) % 2:
        problems.append("непарные **")
    for line in text.splitlines():
        stripped = line.strip()
        if "|" in stripped and not stripped.startswith("|"):
            problems.append("таблица склеена с текстом")
            break
    if re.search(r"(?m)^\s*Источники\s*:?\s*$", text):
        problems.append("лишний блок «Источники»")
    if len(text) < 200:
        problems.append("ответ слишком короткий")
    if len(text) > 4200:
        problems.append("ответ слишком длинный")
    return problems


def check_sources(sources: List[Dict[str, Any]], question: str, answer: str = "") -> List[str]:
    problems: List[str] = []
    items = sources or []
    if not items:
        problems.append("нет источников")
        return problems
    if len(items) > 4:
        problems.append(f"источников больше 4 ({len(items)})")
    seen = set()
    qwords = keywords(f"{question} {answer}")
    for item in items:
        url = str(item.get("url") or "")
        if not url.startswith("http"):
            problems.append("источник без ссылки")
            continue
        host = re.sub(r"^https?://", "", url).split("/")[0].lower()
        if host not in OFFICIAL_HOSTS and not host.endswith(".usergate.com"):
            problems.append(f"неофициальный домен: {host}")
        if url in seen:
            problems.append("дубль источника")
        seen.add(url)
        title_words = keywords(f"{item.get('title') or ''} {url}")
        mentioned = any(word in (answer or "").lower() for word in title_words)
        if qwords and not (qwords & title_words) and not mentioned:
            problems.append(f"источник не по теме: {(item.get('title') or url)[:40]}")
    return problems


def check_followups(followups: List[Any], question: str) -> List[str]:
    problems: List[str] = []
    items = [str(x.get("question") if isinstance(x, dict) else x) for x in (followups or [])]
    items = [x.strip() for x in items if x and x.strip()]
    if not items:
        problems.append("нет кнопок-продолжений")
        return problems
    if len(items) > 4:
        problems.append("слишком много кнопок")
    qlow = (question or "").strip().lower()
    if any(i.lower() == qlow for i in items):
        problems.append("кнопка повторяет вопрос")
    qwords = keywords(question)
    for item in items:
        if item.startswith('Подробнее:'):
            continue
        if qwords and not (qwords & keywords(item)):
            problems.append(f"кнопка не по теме: {item[:40]}")
    return problems


def check_context(context: str, question: str, limit_chars: int = 8500) -> List[str]:
    problems: List[str] = []
    text = context or ""
    if not text.strip():
        problems.append("контекст пуст")
        return problems
    if len(text) > limit_chars:
        problems.append(f"контекст длинный: {len(text)} символов")
    blocks = re.findall(r"(?m)^\[([^\]]+)\]", text)
    hosts_only = False
    if not blocks:
        blocks = re.findall(r"(?m)^Факт \(([^)]+)\):", text)
        hosts_only = True
    if len(blocks) > 8:
        problems.append(f"фрагментов больше 6 ({len(blocks)})")
    headers = re.findall(r"(?m)^\[([^\]]+)\]", text)
    if headers and len(headers) != len(set(headers)):
        problems.append("дубли фрагментов в контексте")
    qwords = keywords(question)
    titles = [b for b in blocks]
    relevant = [t for t in titles if qwords & keywords(t)]
    if titles and relevant is not None and not relevant and not hosts_only:
        problems.append("ни один фрагмент не совпал с темой")
    return problems


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="benchmark-testers-7.json")
    parser.add_argument("--ids", default="")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--out", default="tools/_quality_report.json")
    args = parser.parse_args(argv)

    settings = Settings.load()
    profile = build_profile(settings.data_dir)
    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    retriever = Retriever.load(
        settings.index_dir, embedder=embedder, chroma_dir=settings.chroma_dir
    )
    client = DeepSeekClient(settings)
    agent = PartnerAgent(retriever, settings, client=client, cache=None, profile=profile)
    judge = Judge(client, enabled=True)

    data = json.loads((ROOT / "tools" / args.file).read_text(encoding="utf-8"))
    rows = data.get("questions") if isinstance(data, dict) else data
    if args.ids:
        wanted = {x.strip().upper() for x in args.ids.split(",") if x.strip()}
        rows = [r for r in rows if str(r.get("id", "")).upper() in wanted]
    if args.limit:
        rows = rows[: args.limit]

    report = []
    for row in rows:
        question = str(row.get("question") or row.get("q") or "").strip()
        expected = str(row.get("answer") or row.get("reference") or "")
        done = None
        context_text, _ = agent._auto_context(question, show_notes=False)
        for event in agent.run(question, show_notes=False, mode="auto", use_cache=False):
            if event.get("type") == "done":
                done = event
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
        verdict = judge.judge_answer(question, answer, expected) if expected else None
        judge_score = float(getattr(verdict, "score", 0) or 0)
        clean = all(not v for v in problems.values())
        entry = {
            "id": row.get("id"),
            "question": question,
            "judge_score": judge_score,
            "judge_reason": getattr(verdict, "reason", "") if verdict else "",
            "problems": problems,
            "answer_chars": len(answer),
            "sources": [s.get("url") for s in sources],
            "followups": followups,
        }
        report.append(entry)
        flags = sum(1 for v in problems.values() if v)
        mark = "OK" if clean and judge_score >= 0.7 else "FAIL"
        print(f"{row.get('id')} {mark} судья={judge_score:.2f} проблем={flags} "
              f"{'; '.join(sum(problems.values(), []))[:110]}", flush=True)

    total = len(report)
    passed = sum(
        1
        for e in report
        if not any(e["problems"].values()) and e["judge_score"] >= 0.7
    )
    print(f"\nИТОГО: {passed}/{total} полностью качественных")
    (ROOT / args.out).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
