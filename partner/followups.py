"""Кнопки-продолжения: привязаны к вопросу и проверены по базе знаний.

Почему не «по любому совпадению», как было раньше:

* продолжения собирались запросом «вопрос + первые 400 символов ответа» к BM25
  по вопросам FAQ. Любое общее слово (название продукта, «версия», «сборка»)
  давало совпадение, поэтому после вопроса про сборку 6.1.2 появлялись кнопки
  про цену NGFW и телефон компании — кнопки «на рандом»;
* модель в режиме с инструментами тоже могла предложить что угодно: в описании
  инструмента не было требования держаться предмета ответа.

Здесь у каждого кандидата есть привязка (anchor): сборка, версия, продукт,
термин или контакт, названный в вопросе или ответе. Кандидат без привязки не
показывается — лучше две точные кнопки, чем четыре случайные.

Продолжения зависят от того, кто спрашивает (признак — служебные примечания:
в клиентском режиме они выключены):

* сотруднику нужны рабочие вопросы — соседние сборки, изменения в линейке,
  актуальность, канал поддержки. Рекламные формулировки («возможности
  продукта», «сколько стоит», «скидки») отбрасываются;
* клиенту — «что нового», «какие версии», «что выбрать».

Всё считается локально: индекс карточек (заголовок, продукт, версия, раздел)
строится один раз из уже загруженных фрагментов. Дополнительных вызовов модели
нет, поэтому скорость ответа не меняется.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

from .engine.tokenize import STOPWORDS, clean_text, stem

# Сколько кнопок максимум: интерфейс показывает четыре без «Показать ещё».
MAX_ITEMS = 4

# Длиннее 90 символов кнопка превращается в текст — обрезаем такой кандидат.
MAX_ITEM_CHARS = 90

_BUILD_RE = re.compile(
    r"\b(\d{1,2})\.(\d{1,2})(?:\.(\d{1,4}))?(?:\.(\d{1,6}))?\s*([Rr][Cc]?)\b"
)
_VERSION_RE = re.compile(r"\b(\d{1,2})\.(\d{1,2})(?:\.(\d{1,3}))?\b")
_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
# Ссылка с путём: «usergate.com/registry-entry» — уже конкретный канал.
_URL_PAGE_RE = re.compile(
    r"https?://([^\s/)\]}>«»\"',;]+/[^\s)\]}>«»\"',;]*)", re.I
)

# Фронтматтер страницы документации: заголовок, продукт, версия, раздел, крошки.
_FRONT_MATTER_RE = re.compile(r"(?ms)^---\s*$\n(.*?)\n^---\s*$")
_FRONT_LINE_RE = re.compile(r"^([^\s:][^:\n]{0,40}):\s*(.+?)\s*$")
_HEADING_RE = re.compile(r"(?m)^#{1,3}\s+(.+?)\s*$")

# Признаки релизной страницы и страницы изменений.
_RELEASE_WORDS = ("сборк", "release", "build", "hotfix")
_WITHDRAWN_RE = re.compile(r"(?i)\bотозван")
_CHANGES_RE = re.compile(r"(?i)^\s*изменения\b")

# «Продающие» кнопки: сотруднику они не помогают, ему нужен функционал.
_SALES_RE = re.compile(
    r"(?i)(сколько\s+стоит|стоимост|цен[аыу]\b|ценник|скидк|бесплатн|пробн"
    r"|купить|покупк|аренд|подписк|доставк|тендер|закупк|прайс|акци[яи]\b)"
)
_PITCH_RE = re.compile(
    r"(?i)^(возможности|преимуществ|что\s+умеет|почему\s+стоит|зачем\s+покупать|чем\s+хорош)"
)

# Ответ честно признаёт нехватку данных — тогда уместен вопрос про канал.
_GAP_RE = re.compile(
    r"(?i)(в\s+материалах[^.]{0,60}\bнет\b|нет\s+данных|данных\s+(?:об?\s+\S+\s+)?нет"
    r"|не\s+указан|не\s+приводится|не\s+описан|не\s+сказано|не\s+назван"
    r"|не\s+подтвержд|нельзя\s+восстановить|уточня(?:йте|ет))"
)

# Разделы, которые ничего не добавляют к ответу: кнопка про них бесполезна.
_BLANK_SECTIONS = {
    "часто задаваемые вопросы",
    "документация",
    "документы",
    "главная",
    "статьи",
    "новости",
    "глоссарий",
    "glossary",
}

# Вопрос-определение: тогда соседний термин — естественное продолжение.
_DEFINITION_RE = re.compile(r"(?i)^\s*(что\s+такое|что\s+значит|what\s+is|what's)\b")
# Источник из карточек FAQ: «faq/education.md».
_FAQ_SOURCE_RE = re.compile(r"(?:^|/)faq/", re.I)
# Вопрос про канал: «куда написать», «где проверить». Только такие вопросы
# годятся в продолжение, когда ответ признал нехватку данных.
_CHANNEL_RE = re.compile(
    r"(?i)(куда|где|как)\s+(написать|писать|обратиться|обращаться|связаться|"
    r"смотреть|проверить|уточнить|запросить|получить)"
)

_PHRASES: Dict[str, Dict[str, str]] = {
    "ru": {
        "release_staff": "Что изменилось в сборке {build}?",
        "release_client": "Что нового в сборке {build}?",
        "latest_staff": "Какая последняя сборка {product}?",
        "latest_client": "Какая актуальная версия {product}?",
        "versions_staff": "Какие сборки {product} вышли?",
        "versions_client": "Какие версии {product} существуют?",
        "changes_staff": "Какие изменения были в {product} {major}?",
        "changes_client": "Что нового в {product} {major}?",
        "changes_plain_staff": "Какие изменения были в {product}?",
        "changes_plain_client": "Что нового в {product}?",
        "term_staff": "Что такое {term}?",
        "term_client": "Что такое {term}?",
        "section_staff": "Что ещё есть в разделе «{section}»?",
    },
    "latin": {
        "release_staff": "What changed in build {build}?",
        "release_client": "What is new in build {build}?",
        "latest_staff": "What is the latest {product} build?",
        "latest_client": "What is the current {product} version?",
        "versions_staff": "Which {product} builds were released?",
        "versions_client": "Which {product} versions exist?",
        "changes_staff": "What changes are in {product} {major}?",
        "changes_client": "What is new in {product} {major}?",
        "changes_plain_staff": "What changes are in {product}?",
        "changes_plain_client": "What is new in {product}?",
        "term_staff": "What is {term}?",
        "term_client": "What is {term}?",
        "section_staff": "",
    },
}

# Группы кнопок: четыре кнопки одного смысла подряд — это тоже шум.
_BUCKETS = {
    "release_next": "release",
    "release_prev": "release",
    "changes": "changes",
    "latest": "product",
    "versions": "product",
    "faq": "knowledge",
    "faq_page": "knowledge",
    "term": "knowledge",
    "channel": "knowledge",
    "section": "section",
}
_BUCKET_LIMITS = {
    "release": 2,
    "changes": 1,
    "product": 2,
    "knowledge": 2,
    "section": 1,
}


def supported_lang(lang: str) -> bool:
    """Язык, для которого есть формулировки кнопок.

    Материалы базы русскоязычные, формулировки — русские и английские. Для
    остальных языков кнопки лучше не показывать, чем показать чужие.
    """
    return (lang or "ru") in _PHRASES


def _phrase(lang: str, key: str, staff: bool, **values: str) -> str:
    table = _PHRASES.get(lang) or _PHRASES["ru"]
    suffix = "staff" if staff else "client"
    template = table.get(f"{key}_{suffix}") or table.get(f"{key}_staff") or ""
    if not template:
        return ""
    try:
        return template.format(**values)
    except (KeyError, IndexError):
        return ""


# --- нормализация -------------------------------------------------------
def _content_tokens(text: str) -> Set[str]:
    """Слова для сравнения смысла: без служебных и без односимвольных."""
    tokens: Set[str] = set()
    for word in clean_text(text).split():
        if len(word) < 3 or word in STOPWORDS:
            continue
        tokens.add(stem(word))
    return tokens


def _same_text(first: str, second: str, threshold: float = 0.7) -> bool:
    left = _content_tokens(first)
    right = _content_tokens(second)
    if not left or not right:
        return False
    return len(left & right) / len(left | right) >= threshold


def _same_root(first: str, second: str) -> bool:
    """Слова одного корня: «сертифицирован» и «сертификат» — про одно."""
    if first == second:
        return True
    limit = min(len(first), len(second))
    if limit < 6:
        return False
    prefix = 0
    for left, right in zip(first, second):
        if left != right:
            break
        prefix += 1
    return prefix >= 6


def _related_count(left: Set[str], right: Set[str]) -> int:
    """Сколько слов пересекается с учётом однокоренных форм."""
    if not left or not right:
        return 0
    matched = 0
    used: Set[str] = set()
    for first in left:
        for second in right:
            if second in used:
                continue
            if _same_root(first, second):
                used.add(second)
                matched += 1
                break
    return matched


def _ensure_question(text: str) -> str:
    """Аккуратная подпись кнопки: одна строка, в конце «?»."""
    value = " ".join(str(text or "").split()).strip(" -—•,;")
    if not value:
        return ""
    if value[-1] not in "?？":
        value += "?"
    return value


def _build_of(text: str) -> Tuple[str, Tuple[int, ...]]:
    """Сборка и её числовой ключ: «6.1.2.10523R» → (6, 1, 2, 10523)."""
    match = _BUILD_RE.search(text or "")
    if not match:
        return "", ()
    parts = [int(group) for group in match.groups()[:4] if group]
    if not parts:
        return "", ()
    build = ".".join(str(part) for part in parts) + match.group(5).upper()
    return build, tuple(parts)


def _version_of(key: Tuple[int, ...]) -> str:
    return ".".join(str(part) for part in key[:3]) if len(key) >= 3 else ""


def _trailing_major(text: str) -> str:
    """Версия линейки в конце заголовка: «Изменения в UserGate NGFW 6» → 6."""
    match = _MAJOR_RE.search(text or "")
    return match.group(1) if match else ""


_MAJOR_RE = re.compile(r"(\d{1,2})\s*[.)]?\s*$")


def _product_key(text: str) -> str:
    """Ключ продукта без вендорного префикса: «UserGate NGFW» → «ngfw»."""
    value = clean_text(text)
    return re.sub(r"^usergate\s+", "", value).strip()


_ALIAS_CACHE: Dict[str, "re.Pattern[str]"] = {}


def _alias_pattern(alias: str) -> "re.Pattern[str]":
    pattern = _ALIAS_CACHE.get(alias)
    if pattern is None:
        pattern = re.compile(rf"(?<!\w){re.escape(alias)}(?!\w)", re.I)
        _ALIAS_CACHE[alias] = pattern
    return pattern


def _contacts_in(text: str) -> List[str]:
    """Конкретные каналы из текста: адреса почты и ссылки с путём.

    Голый хост компании (`usergate.com`) каналом не считается: он встречается
    почти в каждом материале и ничего не привязывает.
    """
    found: List[str] = []
    for match in _EMAIL_RE.finditer(text or ""):
        value = match.group(0).lower().rstrip(".,;")
        if value not in found:
            found.append(value)
    for match in _URL_PAGE_RE.finditer(text or ""):
        value = match.group(1).lower().rstrip(".,;")
        if value not in found:
            found.append(value)
    return found[:6]


# --- карточка документа -------------------------------------------------
@dataclass(frozen=True)
class DocMeta:
    """Что известно о документе базы без чтения всего текста."""

    source: str
    slug: str
    heading: str
    product: str
    section: str
    crumbs: str
    build: str
    key: Tuple[int, ...]
    major: str
    release: bool
    changes: bool


def _front_matter(text: str) -> Dict[str, str]:
    """Поля шапки страницы документации (заголовок, продукт, версия, крошки)."""
    head = (text or "")[:1600]
    match = _FRONT_MATTER_RE.search(head)
    if not match:
        return {}
    data: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        item = _FRONT_LINE_RE.match(line.strip())
        if item:
            data[item.group(1).strip().lower()] = item.group(2).strip()[:250]
    return data


def _doc_meta(source: str, text: str, title: str = "") -> Optional[DocMeta]:
    data = _front_matter(text)
    heading = data.get("заголовок") or ""
    if not heading:
        match = _HEADING_RE.search((text or "")[:1200])
        if match:
            heading = match.group(1)
    if not heading:
        heading = title
    heading = " ".join(str(heading or "").split())[:180]
    if not heading:
        return None
    section = " ".join(str(data.get("раздел") or "").split())[:160]
    slug = " ".join(str(title or "").split())[:200]
    build, key = _build_of(f"{heading} {section}")
    low = heading.lower()
    return DocMeta(
        source=source,
        slug=slug,
        heading=heading,
        product=" ".join(str(data.get("продукт") or "").split()),
        section=section,
        crumbs=" ".join(str(data.get("крошки") or "").split())[:300],
        build=build,
        key=key,
        major=str(key[0]) if key else "",
        release=bool(build) and any(word in low for word in _RELEASE_WORDS),
        changes=bool(_CHANGES_RE.match(heading)),
    )


# --- предмет вопроса ----------------------------------------------------
@dataclass
class Subject:
    """О чём именно был вопрос: привязки для кнопок-продолжений."""

    question: str
    answer: str
    staff: bool
    lang: str
    builds: List[str] = field(default_factory=list)
    versions: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    terms: List[str] = field(default_factory=list)
    contacts: List[str] = field(default_factory=list)
    tokens: Set[str] = field(default_factory=set)
    answer_tokens: Set[str] = field(default_factory=set)
    product_tokens: Set[str] = field(default_factory=set)
    focus_tokens: Set[str] = field(default_factory=set)
    faq_docs: List[Tuple[str, str]] = field(default_factory=list)
    docs: List[DocMeta] = field(default_factory=list)
    primary: Optional[DocMeta] = None
    release: Optional[DocMeta] = None
    asked_product: Optional[str] = None
    gap: bool = False


@dataclass
class Candidate:
    text: str
    weight: float
    kind: str


class FollowupPlanner:
    """Собирает продолжения из того, что действительно есть в базе.

    Планировщик живёт вместе с агентом: индекс документов строится при первом
    обращении и переиспользуется, поэтому на каждый ответ тратятся только
    словарные проверки.
    """

    def __init__(self, retriever: Any) -> None:
        self._retriever = retriever
        self._docs: Optional[Dict[str, DocMeta]] = None
        self._by_slug: Dict[str, DocMeta] = {}
        self._series: Dict[str, List[DocMeta]] = {}
        self._catalog: Optional[List[Tuple[str, List["re.Pattern[str]"]]]] = None

    # --- публичный интерфейс ------------------------------------------
    def warm(self) -> None:
        """Готовит индекс карточек заранее, чтобы первый ответ не ждал его."""
        try:
            self._docs_index()
        except Exception:  # noqa: BLE001
            pass

    def plan(
        self,
        question: str,
        answer: str,
        sources: Sequence[Dict[str, Any]] = (),
        *,
        staff: bool = False,
        lang: str = "ru",
        keep: Sequence[str] = (),
    ) -> List[str]:
        """Кнопки-продолжения для готового ответа: 0–4 штуки.

        `keep` — уже одобренные кнопки (например, от модели): они идут первыми,
        а план из базы только добирает недостающее, не повторяя их.
        """
        question = (question or "").strip()
        if not question or not supported_lang(lang):
            return []
        subject = self._subject(question, answer or "", sources, staff, lang)
        candidates: List[Candidate] = []
        for builder in (
            self._release_candidates,
            self._changes_candidates,
            self._product_candidates,
            self._faq_candidates,
            self._faq_page_candidates,
            self._channel_candidates,
            self._term_candidates,
            self._section_candidates,
        ):
            try:
                candidates.extend(builder(subject))
            except Exception:  # noqa: BLE001 - одна ветка не должна ронять ответ
                continue
        return self._select(candidates, subject, keep=keep)

    def review(
        self,
        items: Sequence[str],
        question: str,
        answer: str,
        sources: Sequence[Dict[str, Any]] = (),
        *,
        staff: bool = False,
        lang: str = "ru",
    ) -> List[str]:
        """Проверяет кнопки, которые предложила модель.

        Оставляет только те, что цепляются за вопрос, и убирает продающие
        формулировки для сотрудника. Пустой список — сигнал перейти на план
        из самой базы.
        """
        question = (question or "").strip()
        if not question or not items:
            return []
        subject = self._subject(question, answer or "", sources, staff, lang)
        kept: List[str] = []
        for raw in items:
            text = _ensure_question(raw)
            if not text or len(text) > MAX_ITEM_CHARS:
                continue
            if _same_text(text, question):
                continue
            if staff and (_SALES_RE.search(text) or _PITCH_RE.search(text)):
                continue
            if not self._on_topic(text, subject):
                continue
            if any(_same_text(text, other) for other in kept):
                continue
            kept.append(text)
            if len(kept) >= MAX_ITEMS:
                break
        return kept

    # --- каталог продуктов и индекс документов -------------------------
    def _product_catalog(self) -> List[Tuple[str, List["re.Pattern[str]"]]]:
        if self._catalog is not None:
            return self._catalog
        catalog: List[Tuple[str, List["re.Pattern[str]"]]] = []
        try:
            records = self._retriever.products() or []
        except Exception:  # noqa: BLE001
            records = []
        for record in records:
            name = " ".join(str(record.get("name") or "").split())
            if not name:
                continue
            display = re.split(r"\s+—\s+", name)[0].strip() or name
            aliases = {name, display}
            short = re.sub(r"^usergate\s+", "", display, flags=re.I).strip()
            # Короткое имя берём только для аббревиатур и явных словосочетаний:
            # иначе «Client» совпадёт с английским словом в любом вопросе.
            if short and (re.fullmatch(r"[A-Z0-9]{3,}", short) or len(short) >= 8):
                aliases.add(short)
            patterns = [_alias_pattern(alias) for alias in aliases if len(alias) >= 3]
            catalog.append((display, patterns))
        self._catalog = catalog
        return catalog

    def _display_products(self, text: str) -> List[str]:
        found: List[str] = []
        for display, patterns in self._product_catalog():
            if any(pattern.search(text) for pattern in patterns):
                if display not in found:
                    found.append(display)
        return found

    def _display_for_key(self, key: str) -> str:
        name = key
        for display, _patterns in self._product_catalog():
            if _product_key(display) == key:
                name = display
                break
        return name

    def _mentions_product(self, text: str, display: str) -> bool:
        for name, patterns in self._product_catalog():
            if name != display:
                continue
            return any(pattern.search(text) for pattern in patterns)
        return False

    def _docs_index(self) -> Dict[str, DocMeta]:
        """Одна карточка на документ: строится из первых фрагментов базы."""
        if self._docs is not None:
            return self._docs
        docs: Dict[str, DocMeta] = {}
        for chunk in getattr(self._retriever, "chunks", None) or []:
            if chunk.get("index"):
                continue
            source = str(chunk.get("source") or "")
            if not source or source in docs:
                continue
            meta = _doc_meta(
                source,
                str(chunk.get("text") or ""),
                str(chunk.get("title") or ""),
            )
            if meta is not None:
                docs[source] = meta
                if meta.slug:
                    self._by_slug.setdefault(meta.slug, meta)
        self._docs = docs
        return docs

    def _doc_for(self, source: Dict[str, Any]) -> Optional[DocMeta]:
        """Документ источника: по пути, а в клиентском режиме — по заголовку.

        Клиентская выдача скрывает путь к файлу и оставляет только хост, поэтому
        единственная зацепка — служебный заголовок фрагмента.
        """
        path = str(source.get("source") or "")
        if path:
            meta = self._docs_index().get(path)
            if meta is not None:
                return meta
        title = " ".join(str(source.get("title") or "").split())
        if title:
            return self._by_slug.get(title)
        return None

    def _release_series(self, key: str) -> List[DocMeta]:
        """Релизы одного продукта в порядке версий, без повторов и отозванных."""
        if key in self._series:
            return self._series[key]
        items = [
            doc
            for doc in self._docs_index().values()
            if doc.release and _product_key(doc.product) == key
        ]
        items.sort(key=lambda doc: (doc.key, doc.source))
        series: List[DocMeta] = []
        seen: Set[str] = set()
        for doc in items:
            if not doc.build or doc.build in seen:
                continue
            if _WITHDRAWN_RE.search(doc.heading):
                continue
            seen.add(doc.build)
            series.append(doc)
        self._series[key] = series
        return series

    def _faq_items(self) -> List[Dict[str, Any]]:
        try:
            return list(self._retriever.faq_items() or [])
        except Exception:  # noqa: BLE001
            return []

    def _glossary_items(self) -> List[Dict[str, Any]]:
        try:
            return list(self._retriever.glossary_items() or [])
        except Exception:  # noqa: BLE001
            return []

    # --- предмет вопроса -----------------------------------------------
    def _subject(
        self,
        question: str,
        answer: str,
        sources: Sequence[Dict[str, Any]],
        staff: bool,
        lang: str,
    ) -> Subject:
        subject = Subject(question=question, answer=answer, staff=staff, lang=lang)
        text = f"{question}\n{answer}"
        for match in _BUILD_RE.finditer(text):
            build, key = _build_of(match.group(0))
            if build and build not in subject.builds:
                subject.builds.append(build)
            version = _version_of(key)
            if version and version not in subject.versions:
                subject.versions.append(version)
        if not subject.builds:
            for match in _VERSION_RE.finditer(question):
                version = ".".join(part for part in match.groups() if part)
                if version and version not in subject.versions:
                    subject.versions.append(version)
        subject.products = self._display_products(text)
        asked = self._display_products(question)
        subject.asked_product = asked[0] if asked else None
        try:
            for entry in self._retriever.find_term(question, limit=2) or []:
                term = str(entry.get("term") or "").strip()
                if term:
                    subject.terms.append(term)
        except Exception:  # noqa: BLE001
            pass
        subject.contacts = _contacts_in(f"{answer}\n{question}")
        subject.tokens = _content_tokens(question)
        subject.answer_tokens = _content_tokens(answer)
        product_tokens: Set[str] = set()
        for product in subject.products:
            product_tokens |= _content_tokens(product)
        # Вендорное слово — не тема: «UserGate» есть почти в любом вопросе.
        product_tokens.add("usergate")
        subject.product_tokens = product_tokens
        subject.focus_tokens = subject.tokens - product_tokens
        subject.gap = bool(_GAP_RE.search(answer or ""))

        docs: List[DocMeta] = []
        for source in sources or []:
            meta = self._doc_for(source)
            if meta is not None and meta not in docs:
                docs.append(meta)
        subject.docs = docs
        subject.faq_docs = [
            (str(source.get("source") or ""), str(source.get("title") or ""))
            for source in sources or []
            if _FAQ_SOURCE_RE.search(str(source.get("source") or ""))
        ]
        subject.primary = self._pick_primary(docs, question, answer)
        subject.release = self._release_for(subject)
        if subject.primary is None:
            subject.primary = subject.release
        return subject

    def _release_for(self, subject: Subject) -> Optional[DocMeta]:
        """Релизная страница, о которой идёт речь: по сборке, затем по версии."""
        doc: Optional[DocMeta] = None
        if subject.builds:
            doc = self._release_by_build(subject.builds)
        if doc is None and subject.versions:
            doc = self._release_by_version(subject.versions)
        if doc is None and subject.primary is not None and subject.primary.release:
            doc = subject.primary
        return doc

    def _pick_primary(
        self, docs: Sequence[DocMeta], question: str, answer: str
    ) -> Optional[DocMeta]:
        """Главный документ ответа: тот продукт, о котором речь шла раньше.

        Сборку 6.1.2 выпустили сразу три продукта, и в источниках лежат три
        релизные страницы. Продолжение по случайной из них выглядит невпопад,
        поэтому сначала учитываем продукт из вопроса, затем — «базовую» страницу
        (в заголовке которой нет названия отдельного продукта).
        """
        if not docs:
            return None
        releases = [doc for doc in docs if doc.release]
        if not releases:
            return docs[0]
        for product in self._display_products(question):
            key = _product_key(product)
            for doc in releases:
                if _product_key(doc.product) == key:
                    return doc

        def generic(doc: DocMeta) -> int:
            display = self._display_for_key(_product_key(doc.product))
            if display and display.lower() in doc.heading.lower():
                return 1
            return 0

        return min(
            releases, key=lambda doc: (generic(doc), releases.index(doc))
        )

    def _release_by_build(self, builds: Sequence[str]) -> Optional[DocMeta]:
        wanted = {build.lower() for build in builds}
        matches = [
            doc
            for doc in self._docs_index().values()
            if doc.release and doc.build.lower() in wanted
        ]
        return self._prefer_base(matches)

    def _release_by_version(self, versions: Sequence[str]) -> Optional[DocMeta]:
        """Релиз по номеру версии: «7.1.1» → сборка 7.1.1.12162R."""
        wanted = {version.lower() for version in versions}
        matches = [
            doc
            for doc in self._docs_index().values()
            if doc.release and _version_of(doc.key).lower() in wanted
        ]
        return self._prefer_base(matches)

    def _prefer_base(self, matches: Sequence[DocMeta]) -> Optional[DocMeta]:
        """Из нескольких продуктов с той же сборкой — «базовая» страница.

        Сборку выпускают сразу несколько продуктов. Если пользователь не назвал
        продукт, продолжение по случайной странице (например, SIEM) выглядит
        невпопад, а страница без названия продукта в заголовке — это и есть
        основная линейка UserGate.
        """
        if not matches:
            return None

        def generic(doc: DocMeta) -> int:
            display = self._display_for_key(_product_key(doc.product))
            if display and display.lower() in doc.heading.lower():
                return 1
            return 0

        base = [doc for doc in matches if generic(doc) == 0]
        pool = base or list(matches)
        pool.sort(key=lambda doc: (doc.key, doc.source))
        return pool[-1]

    # --- генераторы кандидатов -----------------------------------------
    def _release_candidates(self, subject: Subject) -> List[Candidate]:
        """Соседние сборки того же продукта — главный ответ на «про сборку»."""
        if not subject.builds and not subject.versions:
            return []
        doc = subject.release or subject.primary
        if doc is None or not doc.release:
            return []
        series = self._release_series(_product_key(doc.product))
        position = next(
            (index for index, item in enumerate(series) if item.build == doc.build),
            None,
        )
        if position is None:
            position = next(
                (index for index, item in enumerate(series) if item.source == doc.source),
                None,
            )
        if position is None:
            return []
        out: List[Candidate] = []
        if position + 1 < len(series):
            nxt = series[position + 1]
            text = _phrase(subject.lang, "release", subject.staff, build=nxt.build)
            if text:
                out.append(Candidate(text, 10.0, "release_next"))
        if position - 1 >= 0:
            prev = series[position - 1]
            text = _phrase(subject.lang, "release", subject.staff, build=prev.build)
            if text:
                out.append(Candidate(text, 8.0, "release_prev"))
        return out

    def _changes_candidates(self, subject: Subject) -> List[Candidate]:
        """Страница изменений линейки: «что менялось в NGFW 6»."""
        if not subject.builds and not subject.versions:
            return []
        doc = subject.release or subject.primary
        key = _product_key(doc.product) if doc is not None else ""
        if not key and subject.asked_product:
            key = _product_key(subject.asked_product)
        if not key:
            return []
        major = doc.major if doc is not None else ""
        if not major and subject.versions:
            major = subject.versions[0].split(".")[0]
        target: Optional[DocMeta] = None
        fallback: Optional[DocMeta] = None
        for candidate in self._docs_index().values():
            if not candidate.changes or _product_key(candidate.product) != key:
                continue
            if major and _trailing_major(candidate.heading) == major:
                target = candidate
                break
            if fallback is None:
                fallback = candidate
        target = target or fallback
        if target is None:
            return []
        if major and _trailing_major(target.heading) != major:
            # Не приписываем кнопке версию, которой нет на найденной странице.
            major = ""
        product = self._display_for_key(key)
        text = (
            _phrase(subject.lang, "changes", subject.staff, product=product, major=major)
            if major
            else _phrase(
                subject.lang, "changes_plain", subject.staff, product=product
            )
        )
        return [Candidate(text, 7.0, "changes")] if text else []

    def _product_candidates(self, subject: Subject) -> List[Candidate]:
        """Актуальная версия и список сборок — только когда спросили о версиях."""
        product = subject.asked_product
        if not product:
            return []
        if not subject.builds and not re.search(
            r"(?i)(верси|сборк|релиз|release|build|обновлен|актуал|последн)", subject.question
        ):
            return []
        series = self._release_series(_product_key(product))
        if len(series) < 2:
            return []
        out: List[Candidate] = []
        latest = _phrase(subject.lang, "latest", subject.staff, product=product)
        versions = _phrase(subject.lang, "versions", subject.staff, product=product)
        if latest:
            out.append(Candidate(latest, 6.0, "latest"))
        if versions:
            out.append(Candidate(versions, 5.0, "versions"))
        return out

    def _faq_candidates(self, subject: Subject) -> List[Candidate]:
        """Вопросы FAQ, которые делят с вопросом предмет, а не служебное слово."""
        out: List[Candidate] = []
        queries = [subject.question]
        if subject.asked_product:
            queries.append(f"{subject.question} {subject.asked_product}")
        seen: List[str] = []
        for query in queries[:2]:
            try:
                records = self._retriever.find_faq(query, limit=8) or []
            except Exception:  # noqa: BLE001
                records = []
            for record in records:
                question = " ".join(str(record.get("question") or "").split())
                if not question or question in seen:
                    continue
                seen.append(question)
                weight = self._faq_weight(
                    question, str(record.get("answer") or ""), subject
                )
                if weight <= 0:
                    continue
                out.append(Candidate(question, 3.5 + weight, "faq"))
        return out

    def _faq_weight(self, question: str, answer: str, subject: Subject) -> float:
        if _same_text(question, subject.question):
            return 0.0
        if subject.staff and (_SALES_RE.search(question) or _PITCH_RE.search(question)):
            return 0.0
        haystack = f"{question} {answer}".lower()
        build_hit = any(build.lower() in haystack for build in subject.builds)
        version_hit = any(version.lower() in haystack for version in subject.versions)
        product_hit = any(
            self._mentions_product(question, product) for product in subject.products
        )
        term_hit = any(term.lower() in haystack for term in subject.terms)
        # Канал считается привязкой только для вопроса «куда обратиться»:
        # иначе любой FAQ, где упомянут тот же адрес почты, попадал в кнопки.
        contact_hit = bool(_CHANNEL_RE.search(question)) and any(
            contact in haystack for contact in subject.contacts
        )
        # Пересечение считаем с самим вопросом: длинный ответ содержит почти все
        # слова подряд и превращал любое совпадение в «связанный» вопрос.
        shared = _related_count(_content_tokens(question), subject.focus_tokens)
        needed = max(1, (3 * len(subject.focus_tokens) + 9) // 10)

        weight = 0.0
        if build_hit:
            weight += 5.0
        if version_hit:
            weight += 2.0
        if product_hit:
            weight += 2.0
        if term_hit:
            weight += 2.0
        if contact_hit:
            weight += 3.0
        weight += min(shared, 3)

        specific = build_hit or version_hit or contact_hit or term_hit
        # Общего названия продукта мало: «Сколько стоит NGFW?» не продолжение
        # вопроса про сертификацию, если других пересечений нет.
        if not specific and shared < needed:
            return 0.0
        return weight

    def _faq_page_candidates(self, subject: Subject) -> List[Candidate]:
        """Соседние вопросы той же тематической карточки FAQ.

        Курированные FAQ-страницы сгруппированы по темам: сертификация,
        контакты, обучение, продукты, цены. Вопрос с той же страницы — это
        продолжение по теме, а не случайное совпадение слов.

        Страницу определяет лучшее попадание `find_faq`, а не сырые источники
        ответа: иначе в выдаче оказывается страница, чей фрагмент просто попал
        в контекст. И если в вопросе назван продукт, карточка должна говорить
        о нём же — иначе «версии WAF» уводили бы в вопросы про сертификацию.
        """
        try:
            records = self._retriever.find_faq(subject.question, limit=6) or []
        except Exception:  # noqa: BLE001
            records = []
        asked_products = [
            product
            for product in subject.products
            if self._mentions_product(subject.question, product)
        ]
        page = ""
        for record in records:
            source = str(record.get("source") or "")
            if not _FAQ_SOURCE_RE.search(source):
                continue
            question = " ".join(str(record.get("question") or "").split())
            if not question:
                continue
            if _same_text(question, subject.question):
                page = source
                break
            if asked_products and not any(
                self._mentions_product(question, product)
                for product in asked_products
            ):
                continue
            if self._faq_weight(question, str(record.get("answer") or ""), subject) <= 0:
                continue
            page = source
            break
        if not page:
            return []

        overlapping: List[Tuple[float, int, str]] = []
        rest: List[Tuple[float, int, str]] = []
        product_tokens: Set[str] = set()
        if asked_products:
            # Соседей сравниваем только с продуктами из вопроса: продукты из
            # длинного ответа иначе перетягивают карточку на свою тему.
            for product in asked_products:
                product_tokens |= _content_tokens(product)
            product_tokens.discard("usergate")
        for order, record in enumerate(self._faq_items()):
            if str(record.get("source") or "") != page:
                continue
            question = " ".join(str(record.get("question") or "").split())
            if not question or _same_text(question, subject.question):
                continue
            if subject.staff and (
                _SALES_RE.search(question) or _PITCH_RE.search(question)
            ):
                continue
            tokens = _content_tokens(question)
            product_overlap = len(tokens & product_tokens)
            focus_overlap = _related_count(tokens, subject.focus_tokens)
            score = 2.0 * product_overlap + focus_overlap
            target = overlapping if score > 0 else rest
            target.append((-score, order, question))

        overlapping.sort()
        rest.sort()
        if asked_products:
            # Продукт назван, а карточка о нём ни слова — не показываем вовсе.
            if not overlapping:
                return []
            ranked = overlapping
        else:
            # Карточка тематическая: сначала связанные словами, затем соседи.
            ranked = overlapping + rest
        out: List[Candidate] = []
        for _score, _order, question in ranked:
            if any(_same_text(question, item.text) for item in out):
                continue
            out.append(Candidate(question, 3.0, "faq_page"))
            if len(out) >= 3:
                break
        return out

    def _term_candidates(self, subject: Subject) -> List[Candidate]:
        """Соседний термин из ответа: «Что такое UGOS?».

        Показывается только для вопроса-определения и только если ответ
        действительно про этот термин, а не упомянул его один раз вскользь.
        """
        answer = subject.answer or ""
        if not answer or not _DEFINITION_RE.search(subject.question):
            return []
        if subject.builds or subject.versions:
            return []
        question_low = subject.question.lower()
        answer_low = answer.lower()
        products = {_product_key(product) for product in subject.products}
        best: Optional[Tuple[int, str]] = None
        for entry in self._glossary_items():
            term = " ".join(str(entry.get("term") or "").split())
            if not term or len(term) > 40:
                continue
            low = term.lower()
            if low in question_low:
                continue
            position = answer_low.find(low)
            if position < 0:
                continue
            if _product_key(term) in products:
                continue
            # Термин должен быть про ту же тему: иначе в ответ на «что такое
            # SUMMA» всплывает первое случайное слово ответа.
            definition = str(entry.get("definition") or "")
            if _related_count(_content_tokens(definition), subject.focus_tokens) < 1:
                continue
            if best is None or position < best[0]:
                best = (position, term)
        if best is None:
            return []
        text = _phrase(subject.lang, "term", subject.staff, term=best[1])
        return [Candidate(text, 4.0, "term")] if text else []

    def _channel_candidates(self, subject: Subject) -> List[Candidate]:
        """Если ответ признал нехватку данных — канал, названный в нём же."""
        if not subject.gap or not subject.contacts:
            return []
        for record in self._faq_items():
            answer = str(record.get("answer") or "").lower()
            if not any(contact in answer for contact in subject.contacts):
                continue
            question = " ".join(str(record.get("question") or "").split())
            if not question or _same_text(question, subject.question):
                continue
            # Каналом считается вопрос «куда обратиться», а не «сколько стоит»:
            # цена оставляет ответ без данных, но кнопкой канала не становится.
            if not _CHANNEL_RE.search(question):
                continue
            return [Candidate(question, 7.0, "channel")]
        return []

    def _section_candidates(self, subject: Subject) -> List[Candidate]:
        """Раздел документации, откуда взят ответ: навигация для сотрудника."""
        if not subject.staff:
            return []
        doc = subject.primary
        if doc is None or not doc.crumbs or " / " not in doc.crumbs:
            return []
        parent = doc.crumbs.rsplit(" / ", 1)[0].strip()
        section = doc.section.strip()
        if section.lower() in _BLANK_SECTIONS or not parent:
            return []
        others = [
            other
            for other in self._docs_index().values()
            if other.source != doc.source
            and other.crumbs.startswith(parent + " / ")
            and _product_key(other.product) in ("", _product_key(doc.product))
        ]
        if not others:
            return []
        text = _phrase(subject.lang, "section", True, section=section)
        return [Candidate(text, 1.5, "section")] if text else []

    # --- отбор ----------------------------------------------------------
    def _on_topic(self, text: str, subject: Subject) -> bool:
        low = text.lower()
        if any(build.lower() in low for build in subject.builds):
            return True
        if any(version in low for version in subject.versions if len(version) >= 3):
            return True
        # Соседняя сборка или версия — тоже продолжение разговора о релизах.
        if (subject.builds or subject.versions) and (
            _BUILD_RE.search(text) or _VERSION_RE.search(text)
        ):
            return True
        shared = len(_content_tokens(text) & subject.tokens)
        if any(
            self._mentions_product(text, product) for product in subject.products
        ):
            # Про одного только продукта мало, когда разговор о конкретной
            # сборке: «Сколько стоит NGFW?» — это не продолжение про 6.1.2.
            if not subject.builds and not subject.versions:
                return True
            if shared >= 1:
                return True
        if any(term.lower() in low for term in subject.terms):
            return True
        if any(contact in low for contact in subject.contacts):
            return True
        if shared >= 2:
            return True
        if len(_content_tokens(text) & subject.answer_tokens) >= 3:
            return True
        return False

    def _select(
        self,
        candidates: Sequence[Candidate],
        subject: Subject,
        keep: Sequence[str] = (),
    ) -> List[str]:
        chosen: List[str] = []
        for raw in keep:
            text = _ensure_question(raw)
            if not text or len(text) > MAX_ITEM_CHARS:
                continue
            if _same_text(text, subject.question):
                continue
            if any(_same_text(text, other) for other in chosen):
                continue
            chosen.append(text)
            if len(chosen) >= MAX_ITEMS:
                return chosen
        ordered = sorted(
            (item for item in candidates if item.text),
            key=lambda item: (-item.weight, item.text.lower()),
        )
        buckets: Dict[str, int] = {}
        for candidate in ordered:
            text = _ensure_question(candidate.text)
            if not text or len(text) > MAX_ITEM_CHARS:
                continue
            if _same_text(text, subject.question):
                continue
            if subject.staff:
                if candidate.kind != "channel" and (
                    _SALES_RE.search(text) or _PITCH_RE.search(text)
                ):
                    continue
            bucket = _BUCKETS.get(candidate.kind, candidate.kind)
            if buckets.get(bucket, 0) >= _BUCKET_LIMITS.get(bucket, 1):
                continue
            if any(_same_text(text, other) for other in chosen):
                continue
            buckets[bucket] = buckets.get(bucket, 0) + 1
            chosen.append(text)
            if len(chosen) >= MAX_ITEMS:
                break
        return chosen
