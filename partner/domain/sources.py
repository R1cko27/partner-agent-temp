"""Источники знаний: файлы от партнёра, публичные URL и структурированные материалы.

База неизвестна заранее, поэтому коннекторы максимально общие:

* `data/company/**` — всё, что прислали представители компании (PDF, DOCX,
  Markdown, TXT, HTML, JSON, CSV);
* `data/company/urls.txt` — открытые источники (сайт, блог, пресс-центр),
  по одному URL на строку; страница скачивается и очищается от разметки;
* `data/company/profile.json` — карточка компании, если её дали явно.

Никакой привязки к конкретной компании: тип документа определяется папкой.
"""

from __future__ import annotations

import csv
import io
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

SUPPORTED_EXTENSIONS = {".md", ".txt", ".html", ".htm", ".pdf", ".docx", ".json", ".csv"}

# Ссылка внутри материала — это адрес источника. Из неё извлекается и адрес
# страницы, и канал (t.me/канал/123 → канал), если он есть в тексте.
_URL_RE = re.compile(r"https?://[^\s)\]>»«\"']+")

# Папка → тип документа. Если папки нет, документ считается материалом.
FOLDER_KIND = {
    "about": "about",
    "company": "about",
    "profile": "about",
    "products": "product",
    "product": "product",
    "services": "product",
    "team": "person",
    "people": "person",
    "staff": "person",
    "news": "news",
    "press": "news",
    "blog": "news",
    "faq": "faq",
    "docs": "doc",
    "materials": "doc",
}

_WS_RE = re.compile(r"[ \t\u00a0]+")
_BLANK_RE = re.compile(r"\n{3,}")


@dataclass
class RawSource:
    """Текст источника до превращения в карточку знания."""

    source_id: str
    title: str
    text: str
    kind: str
    origin: str
    is_url: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WS_RE.sub(" ", text)
    text = _BLANK_RE.sub("\n\n", text)
    return text.strip()


def _first_url(text: str) -> str:
    """Адрес источника: сначала строка «Источник: …», иначе первый URL в тексте.

    Именно строка «Источник» указывает на страницу или пост, тогда как первый
    URL может быть внутренней ссылкой из середины материала.
    """
    marker = re.search(r"(?im)^\s*(?:источник|ссылка|url)\s*:\s*(https?://\S+)", text or "")
    if marker:
        return marker.group(1).rstrip(".,;:»\"'")
    for match in _URL_RE.findall(text or ""):
        clean = match.rstrip(".,;:»\"'")
        if clean.startswith(("http://", "https://")):
            return clean
    return ""


def kind_for_path(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return "doc"
    for part in relative.parts[:-1]:
        kind = FOLDER_KIND.get(part.lower())
        if kind:
            return kind
    return "doc"


def read_pdf(path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001
            continue
    return "\n".join(pages)


def read_docx(path: Path) -> str:
    import docx

    document = docx.Document(str(path))
    parts = [paragraph.text for paragraph in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells))
    return "\n".join(part for part in parts if part.strip())


def read_html(path: Path) -> Tuple[str, str]:
    from bs4 import BeautifulSoup

    raw = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    title = (soup.title.get_text(" ", strip=True) if soup.title else "") or path.stem
    for heading in soup.find_all(["h1", "h2", "h3"]):
        heading.insert_before("\n\n")
        heading.insert_after("\n")
    text = soup.get_text("\n", strip=True)
    return title, text


def read_csv(path: Path) -> str:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    reader = csv.reader(io.StringIO(raw))
    rows = [" | ".join(cell.strip() for cell in row) for row in reader]
    return "\n".join(rows)


def read_file(path: Path, root: Path) -> Optional[RawSource]:
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        return None
    try:
        if suffix == ".pdf":
            text = read_pdf(path)
        elif suffix == ".docx":
            text = read_docx(path)
        elif suffix in (".html", ".htm"):
            _title, text = read_html(path)
        elif suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
            text = json.dumps(payload, ensure_ascii=False, indent=1)
        elif suffix == ".csv":
            text = read_csv(path)
        else:
            text = path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception:  # noqa: BLE001
        return None

    text = _clean(text)
    if len(text) < 40:
        return None
    title = path.stem.replace("_", " ").replace("-", " ").strip()
    first_line = next((line.strip("# ").strip() for line in text.splitlines() if line.strip()), "")
    if len(first_line) > 3 and len(first_line) <= 120:
        title = first_line
    return RawSource(
        source_id=f"file:{path.relative_to(root).as_posix()}",
        title=title,
        text=text,
        kind=kind_for_path(path, root),
        origin=path.relative_to(root).as_posix(),
        metadata={"size": path.stat().st_size, "url": _first_url(text)},
    )


def fetch_url(url: str, timeout: int = 20) -> Optional[RawSource]:
    """Скачивает публичную страницу и превращает её в текст."""
    import httpx
    from bs4 import BeautifulSoup

    try:
        response = httpx.get(
            url,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "PartnerAgent/0.1 (+knowledge base)"},
        )
        response.raise_for_status()
    except Exception:  # noqa: BLE001
        return None

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type and "text" not in content_type:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    title = (soup.title.get_text(" ", strip=True) if soup.title else "") or url
    for heading in soup.find_all(["h1", "h2", "h3"]):
        heading.insert_before("\n\n")
    text = _clean(soup.get_text("\n", strip=True))
    if len(text) < 80:
        return None

    return RawSource(
        source_id=f"url:{url}",
        title=title[:200],
        text=text,
        kind="web",
        origin=url,
        is_url=True,
        metadata={"status": response.status_code},
    )


def read_urls_file(path: Path) -> List[str]:
    if not path.is_file():
        return []
    urls: List[str] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("http://", "https://")):
            urls.append(line)
    return urls


def collect_sources(
    data_dir: Path,
    fetch_web: bool = True,
    progress: Optional[Any] = None,
) -> Tuple[List[RawSource], Dict[str, Any]]:
    """Собирает все источники: файлы, URL и профиль компании."""
    data_dir = Path(data_dir)
    root = data_dir / "company"
    sources: List[RawSource] = []
    report: Dict[str, Any] = {"files": 0, "urls": 0, "skipped": 0, "errors": []}

    if root.is_dir():
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.name.startswith("."):
                continue
            if path.name in ("urls.txt", "profile.json", "agent.json"):
                continue
            # README в корне — инструкция для людей, а не материал компании.
            if path == root / "README.md":
                continue
            source = read_file(path, root)
            if source is None:
                report["skipped"] += 1
                continue
            sources.append(source)
            report["files"] += 1

    if fetch_web:
        for url in read_urls_file(data_dir / "company" / "urls.txt"):
            if progress:
                progress(f"  загружаю {url}")
            source = fetch_url(url)
            if source is None:
                report["errors"].append(url)
                continue
            sources.append(source)
            report["urls"] += 1

    report["total"] = len(sources)
    report["kinds"] = _count_kinds(sources)
    return sources, report


def _count_kinds(sources: Iterable[RawSource]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for source in sources:
        counts[source.kind] = counts.get(source.kind, 0) + 1
    return counts


def load_profile(data_dir: Path) -> Dict[str, Any]:
    path = Path(data_dir) / "company" / "profile.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
