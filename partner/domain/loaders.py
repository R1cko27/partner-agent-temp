"""Сборка базы знаний Partner-Agent из источников компании."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..engine.types import Document
from .entities import Entities, build_documents
from .sources import collect_sources, load_profile


@dataclass
class Knowledge:
    documents: List[Document]
    entities: Entities
    report: Dict[str, Any] = field(default_factory=dict)


def _overview(company: Dict[str, Any], entities: Entities, documents: List[Document]) -> Document:
    name = company.get("name") or "Компания-партнёр"
    lines = [f"Обзор базы знаний о компании {name}."]
    if company.get("site"):
        lines.append(f"Сайт: {company['site']}")
    if company.get("industry"):
        lines.append(f"Отрасль: {company['industry']}")
    if company.get("description"):
        lines.append(str(company["description"])[:600])

    lines.append(
        f"В базе: документов {len(documents)}, продуктов {len(entities.products)}, "
        f"сотрудников {len(entities.people)}, вопросов FAQ {len(entities.faq)}, "
        f"новостей {len(entities.news)}."
    )
    if entities.products:
        lines.append(
            "Продукты: " + ", ".join(
                item["name"] for item in list(entities.products.values())[:12]
            )
        )
    if entities.people:
        lines.append(
            "Команда: " + ", ".join(
                f"{item['name']} ({item['role']})" if item.get("role") else item["name"]
                for item in list(entities.people.values())[:12]
            )
        )
    if entities.news:
        lines.append(
            "Свежие новости: " + "; ".join(
                f"{item['title']} ({item['date']})" if item.get("date") else item["title"]
                for item in entities.news[:6]
            )
        )
    lines.append(
        "Агент отвечает только по этим источникам; если ответа нет — говорит об этом "
        "и предлагает уточнить вопрос или запросить материалы у представителя компании."
    )
    return Document(
        doc_id="overview",
        text="\n".join(lines),
        kind="overview",
        title=f"Обзор знаний о {name}",
        source="data/company/",
        entities={"company": name},
        no_split=True,
    )


def _dedupe_documents(documents: List[Document]) -> List[Document]:
    seen: set[str] = set()
    unique: List[Document] = []
    for document in documents:
        doc_id = document.doc_id
        if doc_id in seen:
            base = re.sub(r"-\d+$", "", doc_id)
            suffix = 2
            while f"{base}-{suffix}" in seen:
                suffix += 1
            doc_id = f"{base}-{suffix}"
            document.doc_id = doc_id
        seen.add(doc_id)
        unique.append(document)
    return unique


def build_knowledge(
    data_dir: Path,
    fetch_web: bool = True,
    progress: Optional[Callable[[str], None]] = None,
) -> Knowledge:
    """Читает материалы компании и строит документы + реестр сущностей."""
    data_dir = Path(data_dir)
    if not data_dir.is_dir():
        raise FileNotFoundError(f"Каталог данных не найден: {data_dir}")

    profile = load_profile(data_dir)
    sources, report = collect_sources(data_dir, fetch_web=fetch_web, progress=progress)
    documents, entities = build_documents(profile, sources)

    if progress:
        progress(
            f"  источников: {report['total']} "
            f"(файлов {report['files']}, URL {report['urls']}, пропущено {report['skipped']})"
        )

    documents = _dedupe_documents(documents)
    documents.insert(0, _overview(entities.company, entities, documents))

    report["documents"] = len(documents)
    report["company"] = entities.company.get("name", "")
    return Knowledge(documents=documents, entities=entities, report=report)
