"""Проверка модели на редких фактах: эталон против ответа.

Для каждого вопроса известно:
- что должно быть в ответе (ключевые термины эталона);
- есть ли факт в базе вообще.

Отдельно смотрим, попал ли нужный материал в выдачу поиска: если нет,
ошибка не модели, а поиска.
"""

from __future__ import annotations

import io
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from partner.agent import PartnerAgent
from partner.config import Settings
from partner.domain.agent_profile import build_profile
from partner.domain.retriever import Retriever
from partner.engine.embeddings import Embedder
from partner.engine.llm import DeepSeekClient

# эталон: ключевые слова, которые должны появиться
CASES: List[Dict[str, Any]] = [
    {
        "id": "BATV",
        "question": "Что такое BATV в UserGate?",
        "expect": ["bounce address tag validation", "возврат"],
        "in_base": True,
        "source_hint": "glossary",
    },
    {
        "id": "BFD",
        "question": "Что такое BFD?",
        "expect": ["bidirectional forwarding detection", "обнаружен"],
        "in_base": True,
        "source_hint": "glossary",
    },
    {
        "id": "Hairpin",
        "question": "Что такое Hairpin NAT?",
        "expect": ["hairpin nat", "преобразован", "ip-адрес"],
        "in_base": True,
        "source_hint": "glossary",
    },
    {
        "id": "Кластеры DCFW",
        "question": "Какие типы кластеров поддерживает UserGate DCFW?",
        "expect": ["кластер конфигурации", "кластер отказоустойчивости"],
        "in_base": True,
        "source_hint": "funkcional6nye",
    },
    {
        "id": "SNMP DCFW",
        "question": "Какие версии SNMP поддерживает DCFW?",
        "expect": ["v2c", "v3"],
        "in_base": True,
        "source_hint": "funkcional6nye",
    },
    {
        "id": "UserID",
        "question": "Что такое функциональность UserID в UserGate?",
        "expect": ["прозрачн", "аутентификац"],
        "in_base": True,
        "source_hint": "funkcional6nye",
    },
    {
        "id": "F8010 (нет в базе)",
        "question": "Сколько портов 10G и какая пропускная способность у UserGate NGFW F8010?",
        "expect": [],
        "in_base": False,
        "source_hint": "",
    },
    {
        "id": "Сертификат WAF (нет в базе)",
        "question": "Какой номер сертификата ФСТЭК у UserGate WAF?",
        "expect": [],
        "in_base": False,
        "source_hint": "",
    },
    # --- вторая волна: термины, перечисления, недостающие факты -------------
    {
        "id": "DMZ",
        "question": "Что такое DMZ в терминах UserGate?",
        "expect": ["демилитаризованная", "сегмент"],
        "in_base": True,
        "source_hint": "glossar",
    },
    {
        "id": "DDoS",
        "question": "Что такое DDoS-атака?",
        "expect": ["отказ в обслуживании", "ботнет"],
        "in_base": True,
        "source_hint": "glossar",
    },
    {
        "id": "DHCP",
        "question": "Что такое DHCP?",
        "expect": ["dynamic host configuration protocol", "автоматическ"],
        "in_base": True,
        "source_hint": "glossar",
    },
    {
        "id": "UserGate Client",
        "question": "Что такое UserGate Client?",
        "expect": ["рабоч", "нулев"],
        "in_base": True,
        "source_hint": "products/client",
    },
    {
        "id": "Продукты SUMMA (перечисление)",
        "question": "Какие продукты входят в экосистему SUMMA?",
        "expect": ["ngfw", "siem"],
        "in_base": True,
        "source_hint": "ecosystem",
    },
    {
        "id": "Офисы (перечисление)",
        "question": "Какие офисы есть у UserGate?",
        "expect": ["москв", "петербург"],
        "in_base": True,
        "source_hint": "contacts",
    },
    {
        "id": "Сотрудники",
        "question": "Сколько сотрудников работает в UserGate?",
        "expect": ["600"],
        "in_base": True,
        "source_hint": "company",
    },
    {
        "id": "Подписка (нет в базе)",
        "question": "Сколько стоит годовая подписка на обновления UserGate NGFW?",
        "expect": [],
        "in_base": False,
        "source_hint": "",
    },
]

NUMBER_RE = re.compile(r"\b\d[\d\s.,]{1,}\s?(?:гбит|гб/с|мбит|порто?в|порт\b)", re.I)
ADMIT = ("нет", "не указан", "не привед", "в материалах отсутств", "не раскрыва", "не публик", "registry-entry", "уточн")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Проверка фактов")
    parser.add_argument("--only", default="", help="ids через запятую")
    args = parser.parse_args()
    wanted = {item.strip().lower() for item in args.only.split(",") if item.strip()}
    if wanted:
        CASES[:] = [
            case for case in CASES
            if any(item in case["id"].lower() for item in wanted)
        ]

    settings = Settings.load()
    profile = build_profile(settings.data_dir)
    retrieval = profile.retrieval
    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    retriever = Retriever.load(settings.index_dir, embedder=embedder, chroma_dir=settings.chroma_dir)
    retriever.set_dedupe(retrieval.max_per_doc, retrieval.dedupe_threshold, retrieval.dedupe)
    retriever.set_kind_weights(retrieval.kind_weights)
    retriever.set_channel_weights(retrieval.channel_weights)
    retriever.set_secondary_kinds(retrieval.secondary_kinds)
    agent = PartnerAgent(
        retriever, settings, client=DeepSeekClient(settings), cache=None, profile=profile
    )

    report: List[Dict[str, Any]] = []
    for case in CASES:
        # попал ли нужный факт в текст выданных фрагментов
        hits = retriever.search(case["question"], k=8)
        context_text = " ".join(str(h.chunk.get("text") or "") for h in hits).lower()
        grounded_terms = [kw for kw in case["expect"] if kw in context_text]
        found_source = bool(case["expect"]) and len(grounded_terms) >= max(
            1, len(case["expect"]) - 1
        )

        started = time.perf_counter()
        done: Dict[str, Any] = {}
        for event in agent.run(
            case["question"], history=[], show_notes=True, use_cache=False, mode="auto"
        ):
            if event.get("type") == "done":
                done = event
        text = str(done.get("text") or "")
        low = text.lower()

        hit_expect = [kw for kw in case["expect"] if kw in low]
        if case["in_base"]:
            passed = len(hit_expect) >= max(1, len(case["expect"]) - 1)
            if not passed:
                verdict = "ошибка"
            elif found_source:
                verdict = "верно и подтверждено"
            else:
                # ответ совпал с эталоном, но нужного фрагмента не было в контексте
                verdict = "верно без источника"
        else:
            # Ответ честно говорит, что номера нет, а упомянутый номер относит
            # к другому продукту — это правильное поведение, а не выдумка.
            admitted = any(marker in low for marker in ADMIT)
            invented = (not admitted) and (
                bool(NUMBER_RE.search(text)) or bool(re.search(r"сертификат\s*№\s*\d", low))
            )
            passed = admitted and not invented
            verdict = "верно" if passed else ("выдумал" if invented else "уклонился")

        report.append(
            {
                "id": case["id"],
                "question": case["question"],
                "verdict": verdict,
                "found_source": found_source,
                "expect_hits": hit_expect,
                "seconds": round(time.perf_counter() - started, 1),
                "answer": text,
            }
        )
        print(f"\n{'='*84}\n[{case['id']}] {case['question']}")
        print(f"вердикт: {verdict} · эталонных терминов найдено: {len(hit_expect)}/{len(case['expect'])}"
              f" · материал в выдаче: {'да' if found_source else 'нет'}")
        print(text[:700])

    passed = sum(1 for item in report if item["verdict"].startswith("верно"))
    print(f"\n{'='*84}\nИТОГО: {passed} из {len(report)} верно")
    out = ROOT / "tools" / "_fact_probe.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print("полный отчёт:", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
