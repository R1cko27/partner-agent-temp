"""Обход сайта и раскладка материалов по структуре data-temp.

Инструмент внешний по отношению к RAG-движку: он только собирает и раскладывает
исходники, ничего не пишет в `data/company/` и не меняет индекс.

    python tools/crawl_site.py --profile usergate-docs
    python tools/crawl_site.py --profile usergate-docs --limit 40
    python tools/crawl_site.py --profile usergate-docs --dry
    python tools/crawl_site.py --url https://docs.usergate.com/glossary/ --limit 1

Что делает:
1. берёт список URL из sitemap.xml (или обходит по ссылкам от стартовой страницы);
2. проверяет robots.txt и соблюдает запреты и crawl-delay;
3. качает страницы с паузами, повторами и ограничением размера;
4. вычищает шаблон страницы: меню, «Поделиться», подсказки BBCode, счётчики,
   блок «Эта статья была», ссылки «Пред./След.»;
5. вытаскивает метаданные: заголовок, продукт, версия, ID статьи, дата обновления,
   ревизия, раздел (хлебные крошки);
6. раскладывает результат по каналам `data-temp/`: чистый Markdown в
   `09-company/docs/<продукт>/`, реестр обхода в `00-meta/`, готовые строки для
   `01-web/docs.csv` — в отдельный файл, чтобы не затирать заполненное руками.

Повторный запуск продолжает с места остановки: состояние лежит в
`data-temp/00-meta/.crawl-state-<профиль>.json`.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, urlunparse
from urllib.robotparser import RobotFileParser

ROOT = Path(__file__).resolve().parent.parent

UA = "PartnerAgent-Crawler/1.0 (+knowledge base for hackathon; polite crawl)"
TIMEOUT = 30.0
MAX_BYTES = 3 * 1024 * 1024
RETRIES = 3

# Профили сайтов. Для SPA-сайтов обход бессмысленен — это фиксируется в отчёте.
PROFILES: Dict[str, Dict[str, object]] = {
    "usergate-docs": {
        "start": "https://docs.usergate.com/",
        "sitemap": "https://docs.usergate.com/sitemap.xml",
        "hosts": ["docs.usergate.com"],
        "bucket": "docs",
        "note": "портал документации: серверный HTML, читается полностью",
    },
    "usergate-main": {
        "start": "https://usergate.com/",
        "sitemap": "https://usergate.com/sitemap.xml",
        "hosts": ["usergate.com", "www.usergate.com"],
        "bucket": "site-sections",
        "note": "основной сайт: SPA за SmartCaptcha, обход даст пустые оболочки",
    },
}

# Куда раскладывать по каналам data-temp (ключ → папка + имя файла).
BUCKETS = {
    "docs": ("01-web", "docs.crawled.csv"),
    "site-sections": ("01-web", "site-sections.crawled.csv"),
    "products": ("01-web", "products-pages.crawled.csv"),
    "academy": ("01-web", "academy.crawled.csv"),
    "newsroom": ("02-media", "newsroom.crawled.csv"),
}

# Признаки шаблонного мусора, который не должен попасть в материал.
NOISE_LINE = re.compile(
    r"^(?:"
    r"Печать|Поделиться|Twitter|Facebook|Отправить по email|Действия|Сохранить|"
    r"Закрепить|Добавить комментарий|Постоянная ссылка|Копировать|Скопировано|"
    r"BBCode.*|http://www\.kbpublisher\.com|-\s*|text|Жирный|Подчеркнутый|Курсивный|"
    r"Зачеркнутый|Цветной|Заголовок\.?|Код|Нумерованный список:|Неупорядоченный список:|"
    r"пункт\s*\d*|Эта статья была:|Полезна|Не полезна|Спасибо за Ваш отзыв!|"
    r"ID статьи:.*|Последнее обновление:.*|Ревизия:.*|Просмотры:.*|Комментарии:.*|"
    r"Теги|Пред\.|След\.|«|»|Опции|Подкатегории|О компании|Продукты|Поддержка|"
    r"Техническая документация|Обучение от Академии UserGate|Условия использования|"
    r"Конфиденциальность|Copyright ©.*|Powered by KBPublisher|,|"
    r"Главная|Документация|Описание версий|Глоссарий|FAQ|Загрузки|Обучение|Войти|"
    r"Закреплённый|Помощь в поиске|Расширенный поиск|Все|"
    r"\[\w+\].*|"
    r"\d+\s*/\s*\d+\s*\(Страница.*\)"
    r")$"
)
# Строки-индексы алфавита и фильтров: «B D G H I P Q R U V А Б И К М Р С У Ш».
LETTER_INDEX = re.compile(r"^(?:[A-Za-zА-Яа-яЁё]\s+){3,}[A-Za-zА-Яа-яЁё]$")
# Метаданные статьи: уже вынесены в шапку файла, в тексте дублируются.
META_LINE = re.compile(r"^(?:Product|Version):\s")
# Висячая дата в конце страницы: «11 Nov, 2026».
DATE_ONLY = re.compile(r"^\d{1,2}\s+[A-Za-zА-Яа-я]{3,9},?\s+\d{4}$")
# Мусорные контейнеры внутри тела статьи.
NOISE_SELECTOR = (
    "[class*=bbcode], [class*=share], [class*=social], [class*=comment], "
    "[class*=rating], [class*=vote], [class*=pagination], [class*=breadcrumb], "
    "[class*=toolbar], [class*=actions], [id*=bbcode], [id*=share]"
)
BOILERPLATE_TAGS = ("script", "style", "nav", "footer", "header", "aside", "form", "noscript")

CAPTCHA_MARKERS = ("smartcaptcha", "captcha.js", "window.onYandexSmartCaptchaLoad")
MIN_BODY = 300          # ниже этого страница считается навигационной, файл не пишем
REPORT_MIN = 120        # ниже этого — пустышка (SPA-оболочка), помечаем отдельно


def log(message: str) -> None:
    print(message, flush=True)


_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "j", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "c",
    "ч": "ch", "ш": "sh", "щ": "shh", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya",
}


def slugify(text: str, limit: int = 60) -> str:
    """Латинский slug: имена файлов остаются переносимыми между ОС и git."""
    lowered = (text or "").lower()
    transliterated = "".join(_TRANSLIT.get(char, char) for char in lowered)
    value = re.sub(r"[^a-z0-9]+", "-", transliterated).strip("-")
    return (value[:limit].rstrip("-") or "page")


def short_hash(text: str, size: int = 6) -> str:
    return hashlib.sha1(text.encode("utf-8", "replace")).hexdigest()[:size]


def canonical_url(url: str) -> str:
    """Убирает якорь, метки поиска и хвостовые слэши, чтобы не качать одно дважды."""
    parsed = urlparse(url)
    query = [
        part for part in parsed.query.split("&")
        if part and not re.match(r"^(utm_|ysclid|yclid|gclid|from|ref|_openstat)", part)
    ]
    path = parsed.path or "/"
    if len(path) > 1 and not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
        path = f"{path}/"
    return urlunparse((parsed.scheme, parsed.netloc.lower(), path, "", "&".join(query), ""))


# Служебные разделы: авторизация, поиск, печатные версии, админка.
EXCLUDE_URL = re.compile(r"(?:/auth\.php|/login|/admin|/print/|/print-cat/|/search/|#)")


def is_asset(url: str) -> bool:
    path = urlparse(url).path.lower()
    return path.endswith((
        ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
        ".woff", ".woff2", ".ttf", ".eot", ".map", ".xml", ".json", ".zip", ".gz",
    ))


@dataclass
class Page:
    url: str
    status: int = 0
    ok: bool = False
    title: str = ""
    body: str = ""
    meta: Dict[str, str] = field(default_factory=dict)
    crumbs: List[str] = field(default_factory=list)
    bucket: str = "site-sections"
    product: str = ""
    version: str = ""
    section: str = ""
    note: str = ""
    content_hash: str = ""


# --------------------------------------------------------------------------
# Список URL
# --------------------------------------------------------------------------

class Fetcher:
    """HTTP-клиент с повторами, ограничением размера и вежливой паузой."""

    def __init__(self, delay: float = 0.3) -> None:
        import httpx

        self.delay = delay
        self._lock = threading.Lock()
        self._last = 0.0
        self.client = httpx.Client(
            timeout=httpx.Timeout(TIMEOUT, connect=10.0),
            follow_redirects=True,
            headers={"User-Agent": UA, "Accept-Language": "ru,en;q=0.8"},
        )

    def _wait(self) -> None:
        if self.delay <= 0:
            return
        with self._lock:
            now = time.monotonic()
            pause = self.delay - (now - self._last)
            if pause > 0:
                time.sleep(pause)
            self._last = time.monotonic()

    def get(self, url: str):
        import httpx

        last_error = ""
        for attempt in range(1, RETRIES + 1):
            self._wait()
            try:
                response = self.client.get(url)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = f"{type(exc).__name__}"
                time.sleep(min(2 ** attempt * 0.5, 8))
                continue
            if response.status_code >= 500:
                last_error = f"HTTP {response.status_code}"
                time.sleep(min(2 ** attempt * 0.5, 8))
                continue
            return response
        raise RuntimeError(last_error or "не удалось загрузить")

    def close(self) -> None:
        self.client.close()


def urls_from_sitemap(fetcher: Fetcher, sitemap: str, hosts: List[str]) -> List[str]:
    seen: List[str] = []
    queue = [sitemap]
    visited: set[str] = set()
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        try:
            response = fetcher.get(current)
        except RuntimeError as exc:
            log(f"  ! sitemap {current}: {exc}")
            continue
        if response.status_code != 200:
            log(f"  ! sitemap {current}: HTTP {response.status_code}")
            continue
        text = response.text
        if "<sitemapindex" in text:                       # вложенные карты
            for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", text):
                if loc not in visited:
                    queue.append(loc)
            continue
        for loc in re.findall(r"<loc>\s*(.*?)\s*</loc>", text):
            host = urlparse(loc).netloc.lower()
            if host in hosts:
                seen.append(loc)
    return seen


def urls_from_links(fetcher: Fetcher, start: str, hosts: List[str], limit: int) -> List[str]:
    """Обход в ширину по ссылкам — если у сайта нет sitemap."""
    from bs4 import BeautifulSoup

    found: List[str] = [start]
    seen = {canonical_url(start)}
    index = 0
    while index < len(found) and len(found) < limit:
        url = found[index]
        index += 1
        try:
            response = fetcher.get(url)
        except RuntimeError:
            continue
        if "html" not in response.headers.get("content-type", ""):
            continue
        soup = BeautifulSoup(response.text, "html.parser")
        for anchor in soup.find_all("a", href=True):
            link = canonical_url(urljoin(url, anchor["href"]))
            if urlparse(link).netloc.lower() not in hosts:
                continue
            if is_asset(link) or link in seen:
                continue
            seen.add(link)
            found.append(link)
            if len(found) >= limit:
                break
    return found


# --------------------------------------------------------------------------
# Разбор страницы
# --------------------------------------------------------------------------

def clean_body(node, title: str = "") -> str:
    """Убирает шаблонные контейнеры и оставляет строки содержания."""
    for tag in node.select(NOISE_SELECTOR):
        tag.decompose()
    raw = node.get_text("\n", strip=True)
    lines: List[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or NOISE_LINE.match(line) or LETTER_INDEX.match(line):
            continue
        if META_LINE.match(line) or DATE_ONLY.match(line):
            continue
        if len(line) <= 2 and not line.isdigit():
            continue
        if lines and lines[-1] == line:          # повтор подряд
            continue
        if not lines and title and line == title.strip():
            continue                              # заголовок уже стоит в `# …`
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text


def parse_page(page: Page, html: str, full_url: str) -> None:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.title.get_text(" ", strip=True) if soup.title else ""
    page.title = re.sub(r"\s*[-|:]{1,2}\s*UserGate.*$", "", title_tag).strip() or title_tag

    # Хлебные крошки — источник раздела и продукта.
    # На портале документации это `div.navigation` одной строкой «Главная / … / NGFW / …».
    crumbs: List[str] = []
    for selector in ("div.navigation.view_left", "div.navigation"):
        node = soup.select_one(selector)
        if node is None:
            continue
        parsed = [
            part.strip()
            for part in re.split(r"\s+/\s+", node.get_text(" ", strip=True))
            if part.strip()
        ]
        if len(parsed) >= 2:
            crumbs = parsed
            break
    if not crumbs:
        for selector in ("[class*=breadcrumb] a", "#breadcrumbs a", "nav[aria-label*=Хлеб] a"):
            nodes = soup.select(selector)
            if nodes:
                crumbs = [n.get_text(" ", strip=True) for n in nodes if n.get_text(strip=True)]
                break
    page.crumbs = crumbs

    body_node = (
        soup.select_one("#content_div div.contentMain")
        or soup.select_one("div.contentMain")
        or soup.select_one("article")
        or soup.select_one("main")
        or soup.body
    )
    if body_node is None:
        page.note = "нет тела документа"
        return

    for tag in body_node.find_all(BOILERPLATE_TAGS):
        tag.decompose()

    page.meta = extract_meta(body_node.get_text("\n", strip=True))
    page.body = clean_body(body_node, page.title)
    page.content_hash = short_hash(re.sub(r"\s+", " ", page.body.lower()), 12)

    # SPA-оболочка: тело пустое, а в HTML есть признаки капчи.
    lowered = html.lower()
    if len(page.body) < REPORT_MIN:
        if any(marker.lower() in lowered for marker in CAPTCHA_MARKERS):
            page.note = "SPA/captcha: сервер отдал оболочку без текста"
        else:
            page.note = "почти нет текста"


def extract_meta(text: str) -> Dict[str, str]:
    patterns = {
        "product": r"(?:^|\n)\s*Product:\s*(.+?)(?:\n|$)",
        "version": r"(?:^|\n)\s*Version:\s*(.+?)(?:\n|$)",
        "article_id": r"ID статьи:\s*(\d+)",
        "updated": r"Последнее обновление:\s*([^\n]+)",
        "revision": r"Ревизия:\s*(\d+)",
        "views": r"Просмотры:\s*(\d+)",
    }
    meta: Dict[str, str] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            meta[key] = match.group(1).strip()
    # «Version: 6.1.9, 7.x, 8.x»
    if "version" in meta:
        meta["version"] = re.sub(r"\s+", " ", meta["version"]).strip()
    return meta


def detect_product(page: Page, hosts: List[str]) -> None:
    """Продукт и версия: метаданные → крошки → заголовок → адрес.

    Если страница относится сразу к нескольким продуктам (общая статья, обучение,
    конвертеры), продукт остаётся пустым, а список попадает в метаданные: иначе
    страница уедет в папку одного продукта и создаст ложное впечатление.
    """
    known = [
        "Management Center", "Log Analyzer", "UserGate Client", "Конвертеры конфигураций",
        "NGFW", "DCFW", "WAF", "SWG", "SIEM", "SUMMA", "UGOS",
    ]

    declared = page.meta.get("product", "")
    if "," in declared:
        page.meta["products"] = ", ".join(
            part.strip() for part in declared.split(",") if part.strip()
        )
        page.product = ""
    else:
        haystack = " ".join([declared, page.title, " ".join(page.crumbs)])
        for name in known:
            if re.search(rf"(?<!\w){re.escape(name)}(?!\w)", haystack, re.IGNORECASE):
                page.product = name
                break

    version = page.meta.get("version", "")
    if not version:
        for crumb in reversed(page.crumbs):
            match = re.search(r"\b(\d+\.(?:\d+|x|X))\b", crumb)
            if match:
                version = match.group(1)
                break
    if not version:
        match = re.search(r"\b(\d+\.(?:\d+|x|X))\b", page.title)
        version = match.group(1) if match else ""
    page.version = version

    # Раздел — последний осмысленный элемент крошек, иначе заголовок.
    section = ""
    for crumb in reversed(page.crumbs):
        if crumb.lower() in {"главная", "документация", "часто задаваемые вопросы", "/"}:
            continue
        if crumb.strip() != page.title.strip():
            section = crumb
            break
    page.section = section or page.title


def classify(page: Page, default_bucket: str) -> str:
    url = page.url.lower()
    haystack = f"{page.title} {' '.join(page.crumbs)}".lower()
    if "/academy" in url or "курс" in haystack and "экзамен" in haystack:
        return "academy"
    if "/news" in url or "/press" in url or "/blog" in url:
        return "newsroom"
    if "/products" in url:
        return "products"
    if "docs." in urlparse(url).netloc or "/dokumentaciya" in url:
        return "docs"
    return default_bucket


# --------------------------------------------------------------------------
# Сохранение
# --------------------------------------------------------------------------

def write_markdown(page: Page, docs_dir: Path) -> Path:
    folder = docs_dir / (slugify(page.product) if page.product else "_general")
    folder.mkdir(parents=True, exist_ok=True)
    name = f"{slugify(page.title)}-{short_hash(page.url)}.md"
    path = folder / name

    header = [
        "---",
        f"заголовок: {page.title}",
        f"url: {page.url}",
        f"получено: {datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M %z')}",
    ]
    if page.product:
        header.append(f"продукт: {page.product}")
    if page.meta.get("products"):
        header.append(f"продукты: {page.meta['products']}")
    if page.version:
        header.append(f"версия: {page.version}")
    if page.section:
        header.append(f"раздел: {page.section}")
    if page.meta.get("article_id"):
        header.append(f"id_статьи: {page.meta['article_id']}")
    if page.meta.get("updated"):
        header.append(f"обновлено: {page.meta['updated']}")
    if page.meta.get("revision"):
        header.append(f"ревизия: {page.meta['revision']}")
    if page.crumbs:
        header.append(f"крошки: {' / '.join(page.crumbs)}")
    header.append("---")

    text = "\n".join(header) + f"\n\n# {page.title}\n\n{page.body}\n\n## Источник\n\n{page.url}\n"
    path.write_text(text, encoding="utf-8")
    return path


def write_report(rows: List[Dict[str, str]], path: Path) -> None:
    """Пишет реестр, сохраняя результаты прошлых запусков (докатка не теряет данные)."""
    columns = [
        "url", "статус", "код", "символов", "заголовок", "продукт", "версия",
        "раздел", "id_статьи", "обновлено", "ревизия", "бакет", "файл", "хэш", "примечание",
    ]
    merged: Dict[str, Dict[str, str]] = {}
    order: List[str] = []
    if path.is_file():
        try:
            with path.open(encoding="utf-8", newline="") as handle:
                for old in csv.DictReader(handle, delimiter=";"):
                    url = old.get("url", "")
                    if url and url not in merged:
                        merged[url] = dict(old)
                        order.append(url)
        except (OSError, csv.Error):
            merged, order = {}, []
    for row in rows:
        url = row.get("url", "")
        if not url:
            continue
        if url not in merged:
            order.append(url)
        merged[url] = {**merged.get(url, {}), **row}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, delimiter=";")
        writer.writeheader()
        for url in order:
            writer.writerow({key: merged[url].get(key, "") for key in columns})


def read_report(path: Path) -> List[Dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def write_bucket_rows(rows: List[Dict[str, str]], out_dir: Path, stamp: str) -> List[Path]:
    """Строки под CSV data-temp: отдельные файлы, чтобы не затирать ручное."""
    written: List[Path] = []
    for bucket, (folder, filename) in BUCKETS.items():
        items = [row for row in rows if row.get("бакет") == bucket and row.get("файл")]
        if not items:
            continue
        path = out_dir / folder / filename.replace(".csv", f"-{stamp}.csv")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(["id", "продукт", "версия", "тип_документа", "url", "что_берём", "статус", "дата"])
            for index, row in enumerate(items, start=1):
                writer.writerow([
                    f"AUTO-{bucket}-{index:04d}",
                    row.get("продукт", ""),
                    row.get("версия", ""),
                    row.get("раздел", ""),
                    row.get("url", ""),
                    row.get("заголовок", ""),
                    "собрано_автоматически",
                    datetime.now().date().isoformat(),
                ])
        written.append(path)
    return written


def write_site_map(rows: List[Dict[str, str]], path: Path) -> None:
    """Дерево разделов собранных страниц — замена ручной карте сайта."""
    tree: Dict[str, Dict[str, List[str]]] = {}
    for row in rows:
        if not row.get("файл"):
            continue
        product = row.get("продукт") or "—"
        section = row.get("раздел") or row.get("заголовок") or "—"
        tree.setdefault(product, {}).setdefault(section, []).append(row.get("заголовок") or row["url"])

    lines = ["# Карта сайта, собранная обходом", "",
             f"Дата обхода: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %z')}", ""]
    for product in sorted(tree):
        lines.append(f"## {product}")
        lines.append("")
        for section in sorted(tree[product]):
            lines.append(f"- **{section}** — {len(tree[product][section])} стр.")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------
# Основной цикл
# --------------------------------------------------------------------------

def load_state(path: Path) -> Dict[str, str]:
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(path: Path, state: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=0), encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Обход сайта и раскладка в data-temp")
    parser.add_argument("--profile", choices=sorted(PROFILES), help="готовый профиль сайта")
    parser.add_argument("--url", help="конкретная стартовая страница")
    parser.add_argument("--out", default=str(ROOT / "data-temp"), help="корень data-temp")
    parser.add_argument("--limit", type=int, default=0, help="сколько страниц обойти (0 — все)")
    parser.add_argument("--delay", type=float, default=0.3, help="пауза между запросами, сек")
    parser.add_argument("--workers", type=int, default=2, help="параллельных загрузок")
    parser.add_argument("--dry", action="store_true", help="только показать список URL")
    parser.add_argument("--fresh", action="store_true", help="игнорировать состояние обхода")
    args = parser.parse_args(argv)

    if not args.profile and not args.url:
        parser.error("нужен --profile или --url")

    if args.profile:
        profile = PROFILES[args.profile]
        start = str(profile["start"])
        sitemap = str(profile["sitemap"])
        hosts = list(profile["hosts"])          # type: ignore[arg-type]
        default_bucket = str(profile["bucket"])
        log(f"Профиль: {args.profile} — {profile['note']}")
    else:
        parsed = urlparse(args.url)
        start = args.url
        sitemap = urljoin(f"{parsed.scheme}://{parsed.netloc}", "/sitemap.xml")
        hosts = [parsed.netloc]
        default_bucket = "site-sections"
        log(f"Разовый обход: {start}")

    out_dir = Path(args.out)
    docs_dir = out_dir / "09-company" / "docs"
    meta_dir = out_dir / "00-meta"
    stamp = datetime.now().strftime("%Y-%m-%d")
    state_path = meta_dir / f".crawl-state-{args.profile or 'custom'}.json"
    state = {} if args.fresh else load_state(state_path)

    fetcher = Fetcher(delay=args.delay)
    try:
        # --- robots.txt ---------------------------------------------------
        robots = RobotFileParser()
        robots_url = urljoin(f"{urlparse(start).scheme}://{urlparse(start).netloc}", "/robots.txt")
        try:
            response = fetcher.get(robots_url)
            if response.status_code == 200:
                robots.parse(response.text.splitlines())
                log(f"robots.txt прочитан: {robots_url}")
            delay_hint = robots.crawl_delay(UA)
            if delay_hint:
                log(f"  robots просит паузу {delay_hint} с — учитываю")
                fetcher.delay = max(fetcher.delay, float(delay_hint))
        except RuntimeError:
            log("robots.txt не прочитан — работаю по общим правилам вежливости")

        # --- список URL ----------------------------------------------------
        log("Собираю список страниц …")
        urls = urls_from_sitemap(fetcher, sitemap, hosts)
        if urls:
            log(f"  sitemap: {len(urls)} URL")
        else:
            log("  sitemap пуст — обхожу по ссылкам")
            urls = urls_from_links(fetcher, start, hosts, args.limit or 200)

        prepared: List[str] = []
        skipped_robots = 0
        skipped_service = 0
        seen: set[str] = set()
        for url in [start] + urls:
            clean = canonical_url(url)
            if clean in seen or is_asset(clean) or EXCLUDE_URL.search(clean):
                skipped_service += 1
                continue
            seen.add(clean)
            if not robots.can_fetch(UA, clean):
                skipped_robots += 1
                continue
            prepared.append(clean)
        if skipped_robots:
            log(f"  запрещено robots.txt: {skipped_robots}")
        if skipped_service:
            log(f"  отброшено служебных и дублей: {skipped_service}")
        if args.limit:
            prepared = prepared[: args.limit]
        log(f"  к обходу: {len(prepared)}")

        if args.dry:
            for url in prepared[:200]:
                print("   ", url)
            return 0

        # --- обход ---------------------------------------------------------
        rows: List[Dict[str, str]] = []
        hashes: Dict[str, str] = {}
        errors: List[str] = []
        # Продолжаем только с тех страниц, которые уже дали результат:
        # ошибки и пустышки пробуем снова.
        DONE_STATES = {"собрано", "навигация", "дубль"}
        queue = [url for url in prepared if state.get(url) not in DONE_STATES]
        log(f"  уже собрано ранее: {len(prepared) - len(queue)}, в очереди: {len(queue)}")

        counter = {"done": 0}
        lock = threading.Lock()
        started = time.monotonic()

        def work(url: str) -> Dict[str, str]:
            page = Page(url=url)
            row: Dict[str, str] = {"url": url, "бакет": default_bucket}
            try:
                response = fetcher.get(url)
            except RuntimeError as exc:
                row.update({"статус": "ошибка", "примечание": str(exc)[:80]})
                return row
            page.status = response.status_code
            row["код"] = str(response.status_code)
            if response.status_code != 200:
                row["статус"] = "ошибка"
                row["примечание"] = f"HTTP {response.status_code}"
                return row
            if len(response.content) > MAX_BYTES:
                row["статус"] = "пропуск"
                row["примечание"] = "файл больше лимита"
                return row
            content_type = response.headers.get("content-type", "")
            if "html" not in content_type:
                row["статус"] = "пропуск"
                row["примечание"] = f"тип {content_type[:30]}"
                return row

            parse_page(page, response.text, url)
            page.bucket = classify(page, default_bucket)
            detect_product(page, hosts)
            row.update({
                "заголовок": page.title[:110],
                "продукт": page.product,
                "версия": page.version,
                "раздел": page.section[:70],
                "id_статьи": page.meta.get("article_id", ""),
                "обновлено": page.meta.get("updated", ""),
                "ревизия": page.meta.get("revision", ""),
                "символов": str(len(page.body)),
                "хэш": page.content_hash,
                "бакет": page.bucket,
                "примечание": page.note,
            })

            with lock:
                counter["done"] += 1
                done = counter["done"]
                if done % 25 == 0 or done == len(queue):
                    speed = done / max(time.monotonic() - started, 0.1)
                    log(f"  {done}/{len(queue)} · {speed:.1f} стр/с")

            if len(page.body) < REPORT_MIN:
                row["статус"] = "пустышка"
                return row
            if page.content_hash in hashes:
                row["статус"] = "дубль"
                row["примечание"] = f"совпадает с {hashes[page.content_hash][:60]}"
                return row
            hashes[page.content_hash] = url

            if len(page.body) < MIN_BODY:
                row["статус"] = "навигация"
                return row

            path = write_markdown(page, docs_dir)
            row["файл"] = (
                path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
            )
            row["статус"] = "собрано"
            return row

        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(work, url): url for url in queue}
            try:
                for future in as_completed(futures):
                    url = futures[future]
                    try:
                        row = future.result()
                    except Exception as exc:  # noqa: BLE001
                        row = {"url": url, "статус": "ошибка", "примечание": f"{type(exc).__name__}: {exc}"[:80]}
                    rows.append(row)
                    state[url] = row.get("статус", "")
                    if row.get("статус") == "ошибка":
                        errors.append(url)
            except KeyboardInterrupt:
                log("\nОстановлено пользователем — состояние сохранено, можно продолжить.")
                save_state(state_path, state)
                raise
    finally:
        fetcher.close()

    # --- отчёты ------------------------------------------------------------
    report_path = meta_dir / f"crawl-report-{args.profile or 'custom'}-{stamp}.csv"
    write_report(rows, report_path)
    all_rows = read_report(report_path)
    bucket_files = write_bucket_rows(all_rows, out_dir, stamp)
    sitemap_path = docs_dir / "site-map.md"
    write_site_map(all_rows, sitemap_path)
    save_state(state_path, state)

    counts: Dict[str, int] = {}
    for row in rows:
        counts[row.get("статус", "?")] = counts.get(row.get("статус", "?"), 0) + 1
    elapsed = time.monotonic() - started

    log("")
    log("=" * 66)
    log(f"  Обходов за запуск: {len(rows)} · за {elapsed:.0f} с · ошибок {len(errors)}")
    for status, count in sorted(counts.items(), key=lambda item: -item[1]):
        log(f"    {status:12} {count}")
    log(f"  Материалы:  {docs_dir}")
    log(f"  Реестр:     {report_path}")
    for path in bucket_files:
        log(f"  Строки CSV: {path}")
    log(f"  Карта:      {sitemap_path}")
    log(f"  Состояние:  {state_path}")
    log("=" * 66)
    return 0 if not errors else 0


if __name__ == "__main__":
    sys.exit(main())
