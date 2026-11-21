"""Предметные карточки: компания, продукты, люди, FAQ, новости.

Партнёр присылает материалы в свободной форме, поэтому карточки строятся из
структуры, которая обычно есть в документах: заголовок файла, папка, пары
«вопрос/ответ», дата в новости, роль в описании сотрудника.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from ..engine.types import Document
from .sources import RawSource

_DATE_RE = re.compile(r"\b(20\d{2})[-./](\d{1,2})[-./](\d{1,2})\b")
_ROLE_RE = re.compile(
    r"(?:должность|роль|position|role|title)\s*[:\-—]\s*(.+)", re.I
)
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_RE = re.compile(r"\+?\d[\d\s()\-]{8,}\d")
_FAQ_RE = re.compile(
    r"(?:^|\n)\s*(?:Q|Вопрос|В)\s*[:\-—]\s*(.+?)\n+\s*(?:A|Ответ|О)\s*[:\-—]\s*(.+?)(?=\n\s*(?:Q|Вопрос|В)\s*[:\-—]|\Z)",
    re.S,
)


@dataclass
class Entities:
    company: Dict[str, Any] = field(default_factory=dict)
    products: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    people: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    faq: List[Dict[str, Any]] = field(default_factory=list)
    glossary: List[Dict[str, Any]] = field(default_factory=list)
    news: List[Dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "company": self.company,
            "products": self.products,
            "people": self.people,
            "faq": self.faq,
            "glossary": self.glossary,
            "news": self.news,
        }


def _slug(text: str) -> str:
    slug = re.sub(r"[^\w]+", "-", (text or "").lower(), flags=re.U).strip("-")
    return slug or "entity"


def _first_paragraph(text: str, limit: int = 600) -> str:
    body = re.sub(r"^#+\s*.*$", "", text, flags=re.M).strip() or text
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
    summary = " ".join(paragraphs[:2]) if paragraphs else body
    return summary[:limit].strip()


def _date_of(text: str) -> str:
    match = _DATE_RE.search(text or "")
    if not match:
        return ""
    year, month, day = match.groups()
    return f"{year}-{int(month):02d}-{int(day):02d}"


def company_document(profile: Dict[str, Any], sources: List[RawSource]) -> Optional[Document]:
    """Карточка компании из profile.json (если представители его дали)."""
    if not profile:
        about = [source for source in sources if source.kind == "about"]
        if not about:
            return None
        profile = {"name": about[0].title}

    name = str(profile.get("name") or profile.get("company") or "Компания")
    lines = [f"Компания {name}"]
    for key, label in (
        ("legal_name", "Юридическое название"),
        ("industry", "Отрасль"),
        ("founded", "Год основания"),
        ("hq", "Штаб-квартира"),
        ("site", "Сайт"),
        ("employees", "Сотрудников"),
        ("mission", "Миссия"),
        ("description", "Описание"),
    ):
        value = profile.get(key)
        if value:
            lines.append(f"{label}: {value}")

    for key, label in (("products", "Продукты"), ("services", "Услуги")):
        values = profile.get(key) or []
        if values:
            lines.append(f"{label}: " + ", ".join(str(item) for item in values))

    contacts = profile.get("contacts") or {}
    if isinstance(contacts, dict) and contacts:
        lines.append(
            "Контакты: " + ", ".join(f"{key} — {value}" for key, value in contacts.items())
        )

    facts = profile.get("facts") or []
    if facts:
        lines.append("Факты: " + "; ".join(str(item) for item in facts))

    return Document(
        doc_id=f"company-{_slug(name)}",
        text="\n".join(lines),
        kind="company",
        title=f"Компания {name}",
        source="data/company/profile.json",
        entities={"company": name},
        metadata={"industry": profile.get("industry", "")},
        no_split=True,
    )


def _product_document(source: RawSource) -> Document:
    name = source.title
    # Карточка идёт в индекс целиком: версии, кластеры и параметры живут
    # в нижних разделах, а не в первом абзаце.
    return Document(
        doc_id=f"product-{_slug(name)}",
        text=f"Продукт {name}\n{source.text.strip()}\nИсточник: {source.origin}",
        kind="product",
        title=f"Продукт {name}",
        source=source.origin,
        entities={"product": name},
        metadata={"url": str(source.metadata.get("url") or "")},
    )


def _person_document(source: RawSource) -> Document:
    name = source.title
    role = ""
    match = _ROLE_RE.search(source.text[:600])
    if match:
        role = match.group(1).strip()[:120]
    lines = [f"Сотрудник {name}"]
    if role:
        lines.append(f"Роль: {role}")
    lines.append(_first_paragraph(source.text, 900))

    # Контакты часто лежат в конце файла — вытаскиваем их отдельно, иначе
    # карточка обрывается на биографии и ассистент говорит «контактов нет».
    emails = list(dict.fromkeys(_EMAIL_RE.findall(source.text)))
    phones = list(dict.fromkeys(_PHONE_RE.findall(source.text)))
    contacts = emails[:2] + [phone.strip() for phone in phones[:2]]
    if contacts:
        lines.append("Контакты: " + ", ".join(contacts))

    return Document(
        doc_id=f"person-{_slug(name)}",
        text="\n".join(lines),
        kind="person",
        title=f"Сотрудник {name}",
        source=source.origin,
        entities={"person": name},
        metadata={"role": role, "contacts": ", ".join(contacts)},
    )


def _faq_documents(source: RawSource) -> List[Document]:
    pairs = _FAQ_RE.findall(source.text)
    documents: List[Document] = []
    for index, (question, answer) in enumerate(pairs[:40], start=1):
        question = " ".join(question.split())[:200]
        answer = " ".join(answer.split())[:900]
        if len(question) < 8 or len(answer) < 10:
            continue
        documents.append(
            Document(
                doc_id=f"faq-{_slug(question)}-{index}",
                text=f"Вопрос: {question}\nОтвет: {answer}",
                kind="faq",
                title=question,
                source=source.origin,
                entities={"faq": question},
            )
        )
    return documents


def _news_document(source: RawSource) -> Document:
    date = _date_of(source.text) or _date_of(source.origin)
    link = str(source.metadata.get("url") or "")
    return Document(
        doc_id=f"news-{_slug(source.title)}",
        text=(
            f"Новость: {source.title}\n"
            + (f"Дата: {date}\n" if date else "")
            # Ссылка идёт до текста: она обрезается при сжатии карточки, а из неё
            # выводится и адрес страницы, и канал (t.me/канал/123 → канал).
            + (f"Ссылка: {link}\n" if link else "")
            + _first_paragraph(source.text, 900)
            + f"\nИсточник: {source.origin}"
        ),
        kind="news",
        title=source.title,
        source=source.origin,
        entities={"news": source.title},
        metadata={"date": date, "url": link},
    )


def _plain_document(source: RawSource) -> Document:
    return Document(
        doc_id=f"doc-{_slug(source.title)}",
        text=f"{source.title}\n{source.text}",
        kind=source.kind or "doc",
        title=source.title,
        source=source.origin,
        entities={},
    )


def _is_glossary(source: RawSource) -> bool:
    marker = f"{source.title} {source.origin}".lower()
    # glossar покрывает и «glossary», и транслит «glossarij» из краулера
    return "глоссар" in marker or "glossar" in marker


def _glossary_entries(text: str) -> List[Dict[str, str]]:
    """Разбирает страницу глоссария на пары «термин — определение».

    Формат страницы: строка термина без точки, затем одна или несколько строк
    определения. Навигацию по алфавиту и одиночные буквы отбрасываем.
    """
    body = text
    if body.startswith("---"):
        parts = body.split("---", 2)
        if len(parts) >= 3:
            body = parts[2]

    entries: List[Dict[str, str]] = []
    term = ""
    buffer: List[str] = []

    def flush() -> None:
        nonlocal term, buffer
        definition = " ".join(part.strip() for part in buffer).strip()
        if term and len(definition) > 20 and len(term) > 1:
            entries.append({"term": term, "definition": definition[:600]})
        buffer = []

    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        looks_like_term = (
            len(line) <= 70
            and not line.endswith((".", "!", "?", ":", ";"))
            and line[:1].isupper()
            and not line.lower().startswith(("все", "главная", "документация"))
        )
        if looks_like_term:
            flush()
            term = line
        elif term:
            buffer.append(line)
    flush()
    return entries


def build_documents(
    profile: Dict[str, Any], sources: List[RawSource]
) -> Tuple[List[Document], Entities]:
    """Собирает карточки и реестр сущностей из всех источников."""
    documents: List[Document] = []
    entities = Entities(company=dict(profile or {}))

    company = company_document(profile, sources)
    if company is not None:
        documents.append(company)
        entities.company = {
            "name": str(profile.get("name") or profile.get("company") or company.title),
            "site": profile.get("site", ""),
            "industry": profile.get("industry", ""),
            "description": profile.get("description", ""),
            "products": profile.get("products") or [],
            "contacts": profile.get("contacts") or {},
            "source": company.source,
        }

    for source in sources:
        if source.kind == "product":
            document = _product_document(source)
            entities.products[_slug(document.title)] = {
                "name": document.title.replace("Продукт ", ""),
                "description": _first_paragraph(source.text, 400),
                "source": source.origin,
            }
            documents.append(document)
        elif source.kind == "person":
            document = _person_document(source)
            entities.people[_slug(document.title)] = {
                "name": document.title.replace("Сотрудник ", ""),
                "role": document.metadata.get("role", ""),
                "contacts": document.metadata.get("contacts", ""),
                "source": source.origin,
            }
            documents.append(document)
        elif source.kind == "faq":
            faq_docs = _faq_documents(source)
            if faq_docs:
                documents.extend(faq_docs)
                entities.faq.extend(
                    {
                        "question": doc.title,
                        "answer": doc.text.split("Ответ:", 1)[-1].strip()[:400],
                        "source": source.origin,
                    }
                    for doc in faq_docs
                )
            else:
                documents.append(_plain_document(source))
        elif _is_glossary(source):
            # Глоссарий разбираем на термины: в общем поиске определение тонет
            # среди 35 тысяч фрагментов, а вопрос «что такое X» ждёт его сразу.
            entries = _glossary_entries(source.text)
            for entry in entries:
                entry["source"] = source.origin
            entities.glossary.extend(entries)
            documents.append(_plain_document(source))
        elif source.kind == "news":
            document = _news_document(source)
            entities.news.append(
                {
                    "title": document.title,
                    "date": document.metadata.get("date", ""),
                    "source": source.origin,
                }
            )
            documents.append(document)
        else:
            documents.append(_plain_document(source))

    return documents, entities
