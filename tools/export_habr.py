"""Экспорт статей компании с Habr в файлы.

Блог компании на Habr — обычный серверный HTML, авторизация не нужна:
листинг `https://habr.com/ru/companies/<company>/articles/?page=N` отдаёт по
20 статей, каждая статья доступна отдельной страницей. Скрипт обходит листинг,
затем скачивает полный текст каждой статьи и сохраняет его в markdown.

    python tools/export_habr.py                      # все статьи компании
    python tools/export_habr.py --limit 10           # только свежие 10
    python tools/export_habr.py --from-archive data-temp/habr/usergate.jsonl

Готовые markdown попадают в `data-temp/02-media/habr/`, каталог источников —
в `data-temp/02-media/habr.csv` (формат остальных CSV проекта: `;`, utf-8-sig).
"""

from __future__ import annotations

import argparse
import csv
import html as htmllib
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru,en;q=0.9",
}
BASE = "https://habr.com"
MAX_PAGES = 60

BLOCK_TAGS = {
    "p", "div", "section", "article", "blockquote", "figure", "figcaption",
    "table", "thead", "tbody", "tr", "ul", "ol", "li",
    "h1", "h2", "h3", "h4", "h5", "h6", "pre", "hr",
}


@dataclass
class Article:
    id: int
    title: str
    url: str
    date: str
    summary: str = ""
    text: str = ""
    author: str = ""
    reading_time: str = ""
    views: int = 0
    tags: List[str] = field(default_factory=list)
    image: str = ""

    @property
    def iso_date(self) -> str:
        return self.date[:10] if self.date else ""

    @property
    def slug(self) -> str:
        return f"{self.iso_date or 'без-даты'}-{self.id}"


def force_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


# --- HTML → текст --------------------------------------------------------
def html_to_text(node) -> str:
    """Превращает тело статьи в текст с markdown-разметкой заголовков и списков."""
    parts: List[str] = []

    def walk(element, inline: bool = False) -> None:
        for child in element.children:
            name = getattr(child, "name", None)
            if name is None:
                text = str(child)
                if text.strip():
                    parts.append(re.sub(r"[ \t\r\n]+", " ", text))
                continue

            if name == "br":
                parts.append("\n")
                continue
            if name == "hr":
                parts.append("\n\n---\n\n")
                continue
            if name == "img":
                src = child.get("src") or child.get("data-src") or ""
                if src:
                    parts.append(f"\n[изображение: {src}]\n")
                continue
            if name == "a":
                href = child.get("href") or ""
                label = child.get_text(" ", strip=True)
                if href.startswith("/"):
                    href = BASE + href
                if href.startswith("http") and label and href != label:
                    parts.append(f"[{label}]({href})")
                else:
                    parts.append(label or href)
                continue
            if name in ("script", "style", "noscript"):
                continue

            if name == "pre":
                parts.append("\n\n```\n" + child.get_text("\n", strip=False).strip() + "\n```\n\n")
                continue

            if not inline:
                if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                    parts.append("\n\n" + "#" * int(name[1]) + " ")
                elif name == "li":
                    parts.append("\n- ")
                    walk(child, inline=True)
                    continue
                elif name in ("p", "blockquote", "tr", "figcaption"):
                    parts.append("\n\n")

            # Внутри пункта списка переносы абзацев не нужны — иначе «-» остаётся
            # на отдельной строке, а текст уезжает на следующую.
            walk(child, inline=inline or name == "li")

            if not inline and name in BLOCK_TAGS and name != "li":
                parts.append("\n")

    walk(node)
    text = "".join(parts)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# --- листинг -------------------------------------------------------------
def parse_listing(html: str) -> List[Dict[str, Any]]:
    """Из страницы листинга достаёт ссылки, заголовки и даты статей."""
    soup = BeautifulSoup(html, "html.parser")
    found: List[Dict[str, Any]] = []
    seen: set[int] = set()

    # Дата и заголовок берём внутри одного сниппета, иначе они разъезжаются.
    for snippet in soup.select(".tm-articles-list__item, article.tm-articles-list__item"):
        link = snippet.select_one('a.tm-title__link[href*="/articles/"]')
        if link is None:
            continue
        href = link.get("href") or ""
        match = re.search(r"/articles/(\d+)/", href)
        if not match:
            continue
        article_id = int(match.group(1))
        if article_id in seen:
            continue
        seen.add(article_id)
        time_tag = snippet.select_one("time[datetime]")
        found.append(
            {
                "id": article_id,
                "title": " ".join(link.get_text(" ", strip=True).split()),
                "url": href if href.startswith("http") else BASE + href,
                "date": (time_tag.get("datetime") if time_tag else "") or "",
            }
        )

    if found:
        return found

    # Запасной путь: если Habr сменил разметку сниппетов.
    for link in soup.select('a.tm-title__link[href*="/articles/"]'):
        href = link.get("href") or ""
        match = re.search(r"/articles/(\d+)/", href)
        if not match:
            continue
        article_id = int(match.group(1))
        if article_id in seen:
            continue
        seen.add(article_id)
        found.append(
            {
                "id": article_id,
                "title": " ".join(link.get_text(" ", strip=True).split()),
                "url": href if href.startswith("http") else BASE + href,
                "date": "",
            }
        )
    return found


def _page_urls(company: str, page: int) -> List[str]:
    """Habr принимает разные формы пагинации; пробуем по очереди."""
    base = f"{BASE}/ru/companies/{company}/articles/"
    if page == 1:
        return [base]
    return [f"{base}page{page}/", f"{base}?page={page}"]


def fetch_listing(
    company: str,
    limit: int = 0,
    delay: float = 0.7,
    progress=print,
) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen: set[int] = set()

    with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        for page in range(1, MAX_PAGES + 1):
            batch: List[Dict[str, Any]] = []
            used_url = ""
            for url in _page_urls(company, page):
                try:
                    response = client.get(url)
                except httpx.HTTPError as exc:
                    progress(f"  ! страница {page}: {exc}")
                    continue
                if response.status_code == 429:
                    progress("  ! Habr ограничил частоту запросов (429) — останавливаюсь")
                    return items[:limit] if limit else items
                if response.status_code != 200:
                    continue
                batch = [item for item in parse_listing(response.text) if item["id"] not in seen]
                if batch:
                    used_url = url
                    break
                time.sleep(0.3)

            if not batch:
                if page > 1:
                    progress(f"  страница {page}: новых статей нет — листинг закончился")
                break

            for item in batch:
                item.setdefault("date", "")
                seen.add(item["id"])
            items.extend(batch)
            progress(f"  страница {page}: +{len(batch)} (всего {len(items)})  [{used_url.rsplit('/', 2)[-2]}]")

            if limit and len(items) >= limit:
                break
            time.sleep(delay)

    return items[:limit] if limit else items


# --- статья --------------------------------------------------------------
def _views(soup, html: str) -> int:
    for selector in (
        ".tm-article-stats__views-value",
        ".views-count",
        ".tm-article-snippet__statistics-item--views",
    ):
        node = soup.select_one(selector)
        if node:
            digits = re.sub(r"[^\d]", "", node.get_text(" ", strip=True))
            if digits:
                return int(digits)
    match = re.search(r"([\d\s]{2,})\s*(?:просмотр|views)", html, re.I)
    if match:
        digits = re.sub(r"[^\d]", "", match.group(1))
        if digits:
            return int(digits)
    return 0


def parse_article(html: str, fallback: Dict[str, Any]) -> Article:
    soup = BeautifulSoup(html, "html.parser")

    title_node = soup.select_one("h1.tm-title span") or soup.select_one("h1.tm-title")
    title = " ".join(title_node.get_text(" ", strip=True).split()) if title_node else fallback.get("title", "")

    date_tag = soup.select_one(
        "time.tm-article-datetime-published, .tm-article-datetime-published time"
    ) or soup.select_one("time[datetime]")
    date = date_tag.get("datetime") if date_tag else fallback.get("date", "")

    body = soup.select_one(".article-formatted-body")
    text = html_to_text(body) if body else ""

    # Отдельного лида на странице статьи нет: похожий блок в сайдбаре относится
    # к другой публикации, поэтому summary не заполняем.
    summary = ""

    author_node = soup.select_one(".tm-user-info__username")
    author = author_node.get_text(" ", strip=True) if author_node else ""

    reading_node = soup.select_one(".tm-article-reading-time__counter")
    reading = reading_node.get_text(" ", strip=True) if reading_node else ""

    tags = [
        node.get_text(" ", strip=True).rstrip("*").strip()
        for node in soup.select(".tm-publication-hubs__hub, .tm-article-snippet__hubs a, .tm-tags-list__tag")
        if node.get_text(strip=True)
    ]
    if not tags:
        tags = [
            node.get_text(" ", strip=True).rstrip("*").strip()
            for node in soup.select('a[href*="/hubs/"], a[href*="/tags/"]')
            if node.get_text(strip=True)
        ]
    # «Хабы», «Теги» — подписи блоков, а не значения.
    skip = {"хабы", "теги", "хабы и теги", "компании", "блоги"}
    tags = [tag for tag in dict.fromkeys(tags) if tag and tag.lower() not in skip][:8]

    image = ""
    meta_image = soup.find("meta", property="og:image")
    if meta_image:
        image = meta_image.get("content") or ""

    return Article(
        id=int(fallback["id"]),
        title=title or fallback.get("title", ""),
        url=fallback.get("url", ""),
        date=date or "",
        summary=summary,
        text=text,
        author=author,
        reading_time=reading,
        views=_views(soup, html),
        tags=tags,
        image=image,
    )


def fetch_articles(
    items: List[Dict[str, Any]],
    delay: float = 0.7,
    progress=print,
) -> List[Article]:
    articles: List[Article] = []
    with httpx.Client(timeout=40, follow_redirects=True, headers=HEADERS) as client:
        for index, item in enumerate(items, start=1):
            try:
                response = client.get(item["url"])
            except httpx.HTTPError as exc:
                progress(f"  ! {item['id']}: {exc}")
                continue
            if response.status_code == 429:
                progress("  ! Habr ограничил частоту запросов (429) — останавливаюсь")
                break
            if response.status_code != 200:
                progress(f"  ! {item['id']}: HTTP {response.status_code}")
                continue
            articles.append(parse_article(response.text, item))
            if index % 10 == 0 or index == len(items):
                progress(f"  статей: {len(articles)}/{len(items)}")
            time.sleep(delay)
    return articles


# --- вывод ---------------------------------------------------------------
def _kind(article: Article) -> str:
    text = f"{article.title} {article.text[:600]}".lower()
    if any(word in text for word in ("кейс", "внедрен", "опыт эксплуатац")):
        return "кейс"
    if any(word in text for word in ("исследован", "аналитик", "отчёт", "отчет")):
        return "исследование"
    if any(word in text for word in ("вебинар", "конференц", "приглаша")):
        return "анонс"
    return "статья"


def _excerpt(article: Article, width: int = 90) -> str:
    flat = " ".join((article.title or "").split())
    if not flat:
        flat = " ".join((article.text or "").split())[:width]
    if len(flat) > width:
        flat = flat[: width - 1].rsplit(" ", 1)[0] + "…"
    return flat


def render_markdown(article: Article) -> str:
    lines = [f"# {article.title or _excerpt(article)}", ""]

    meta = [f"Дата: {article.iso_date or '—'}"]
    if article.reading_time:
        meta.append(f"Чтение: {article.reading_time}")
    if article.views:
        meta.append(f"Просмотры: {article.views}")
    if article.author:
        meta.append(f"Автор: {article.author}")
    lines.append(" · ".join(meta))

    if article.tags:
        lines.append("Хабы и теги: " + ", ".join(article.tags))
    lines.append("")

    if article.summary:
        lines.append("> " + article.summary)
        lines.append("")

    if article.text:
        lines.append(article.text)
        lines.append("")

    lines.append(f"Источник: {article.url}")
    return "\n".join(lines).strip() + "\n"


def write_catalog(articles: List[Article], path: Path, opened: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["id", "дата", "заголовок", "url", "тип", "что_берём", "куда", "статус", "примечание"]
        )
        for article in articles:
            # Просмотры Habr показывает только авторизованным, поэтому ноль
            # означачает «неизвестно», а не «никто не читал».
            note = f"Habr, обращение {opened}"
            if article.reading_time:
                note = f"Habr, {article.reading_time}, обращение {opened}"
            elif article.views:
                note = f"Habr, просмотров {article.views}, обращение {opened}"
            writer.writerow(
                [
                    f"HABR-{article.id}",
                    article.iso_date or "—",
                    _excerpt(article),
                    article.url,
                    _kind(article),
                    "—",
                    "02-media/habr/, docs/",
                    "собран" if article.text else "нет текста",
                    note,
                ]
            )
    return len(articles)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Экспорт статей компании с Habr")
    parser.add_argument("--company", default="usergate", help="слаг компании в URL Habr")
    parser.add_argument("--limit", type=int, default=0, help="сколько статей взять (0 — все)")
    parser.add_argument("--delay", type=float, default=0.7, help="пауза между запросами, сек")
    parser.add_argument("--archive", default="data-temp/habr", help="каталог сырого архива JSONL")
    parser.add_argument("--md-dir", default="data-temp/02-media/habr", help="каталог markdown")
    parser.add_argument("--catalog", default="data-temp/02-media/habr.csv", help="CSV-каталог")
    parser.add_argument(
        "--from-archive",
        default="",
        help="пересобрать markdown из готового JSONL, не обращаясь к habr.com",
    )
    args = parser.parse_args(argv)
    force_utf8_stdout()

    company = args.company.strip()
    started = time.perf_counter()

    if args.from_archive:
        source = Path(args.from_archive)
        if not source.is_file():
            print(f"! архив не найден: {source}")
            return 1
        rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
        articles = [Article(**{k: v for k, v in row.items() if k in Article.__dataclass_fields__}) for row in rows]
        print(f"→ Компания: {company} · из архива {len(articles)} статей")
    else:
        print(f"→ Компания: {company} · лимит: {args.limit or 'все статьи'}")
        items = fetch_listing(company, limit=args.limit, delay=args.delay)
        if not items:
            print("! статьи не найдены — проверьте слаг компании")
            return 1
        print(f"  в листинге: {len(items)} статей")
        articles = fetch_articles(items, delay=args.delay)

    if not articles:
        print("! не удалось скачать ни одной статьи")
        return 1

    ordered = sorted(articles, key=lambda article: (article.date, article.id))

    archive_dir = Path(args.archive)
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{company}.jsonl"
    with archive_path.open("w", encoding="utf-8") as handle:
        for article in ordered:
            handle.write(json.dumps(asdict(article), ensure_ascii=False) + "\n")

    written = 0
    if args.md_dir:
        md_dir = Path(args.md_dir)
        md_dir.mkdir(parents=True, exist_ok=True)
        fresh: set[str] = set()
        for article in ordered:
            name = f"{article.slug}.md"
            (md_dir / name).write_text(render_markdown(article), encoding="utf-8")
            fresh.add(name)
            written += 1
        for stale in md_dir.glob("*.md"):
            if stem_date(stale.stem) and stale.name not in fresh:
                stale.unlink()

    catalog_rows = 0
    if args.catalog:
        catalog_rows = write_catalog(ordered, Path(args.catalog), time.strftime("%Y-%m-%d"))

    dates = [article.iso_date for article in ordered if article.iso_date]
    elapsed = time.perf_counter() - started

    print("")
    print("=" * 62)
    print(f"  Готово за {elapsed:.1f} с")
    print(f"  Статей      : {len(ordered)}")
    print(f"    с текстом : {sum(1 for a in ordered if a.text)}")
    if dates:
        print(f"  Период      : {min(dates)} — {max(dates)}")
    print(f"  Просмотры   : {sum(a.views for a in ordered):,}".replace(",", " "))
    print(f"  Архив       : {archive_path}")
    if written:
        print(f"  Markdown    : {args.md_dir} ({written} файлов)")
    if catalog_rows:
        print(f"  Каталог CSV : {args.catalog} ({catalog_rows} строк)")
    print("=" * 62)
    return 0


def stem_date(stem: str) -> bool:
    """Наши файлы называются ГГГГ-ММ-ДД-<id>; чужие не трогаем."""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}-\d+$", stem))


if __name__ == "__main__":
    sys.exit(main())
