"""Экспорт постов сообщества ВКонтакте в файлы.

Два режима:

* **по токену** (`VK_TOKEN` или `--token`) — официальный `wall.get`, вся стена
  с пагинацией по 100 постов. Это рабочий путь для полной выгрузки;
* **без токена** — разбор страницы сообщества. VK отдаёт её гостем, но кладёт
  в prefetch-кэш только первые 10 постов, поэтому режим годится лишь для
  проверки формата и свежих новостей.

    python tools/export_vk.py                     # без токена, последние 10
    set VK_TOKEN=vk1.a.xxxx                       # service token
    python tools/export_vk.py --limit 0           # вся стена

Готовые markdown попадают в `data-temp/02-media/vk/`, каталог источников —
в `data-temp/02-media/vk.csv` (формат остальных CSV проекта: `;`, utf-8-sig).
"""

from __future__ import annotations

import argparse
import csv
import html as htmllib
import json
import os
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from bs4 import BeautifulSoup

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
HEADERS = {"User-Agent": UA, "Accept-Language": "ru,en;q=0.9"}
API_VERSION = "5.199"
API_URL = "https://api.vk.com/method/wall.get"

KIND_RULES = (
    ("разбор угрозы", ("уязвим", "cve-", "эксплуат", "вредонос", "угроз")),
    ("анонс", ("вебинар", "конференц", "медиатур", "регистрац", "приглаша", "мероприят", "встреч")),
    ("релиз", ("релиз", "верси", "обновлен", "выпустил", "вышл", "доступн")),
    ("исследование", ("исследован", "отчёт", "отчет", "аналитик")),
)


@dataclass
class Post:
    id: int
    owner_id: int
    date: str
    text: str
    url: str
    views: int = 0
    likes: int = 0
    photos: List[str] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    is_pinned: bool = False
    copy_from: str = ""

    @property
    def iso_date(self) -> str:
        return self.date[:10] if self.date else ""

    @property
    def has_content(self) -> bool:
        return bool(self.text or self.photos or self.links or self.videos)


def force_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def post_kind(post: Post) -> str:
    text = (post.text or "").lower()
    for label, markers in KIND_RULES:
        if any(marker in text for marker in markers):
            return label
    return "новость"


def _iso(stamp: Any) -> str:
    try:
        return datetime.fromtimestamp(int(stamp), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    except (TypeError, ValueError, OSError):
        return ""


def _pick_photo(photo: Dict[str, Any]) -> str:
    """Самый крупный размер, но не больше 1280 по ширине — чтобы файл не раздувался."""
    sizes = [size for size in photo.get("sizes") or [] if size.get("url")]
    if not sizes:
        return ""
    fitting = [size for size in sizes if int(size.get("width") or 0) <= 1280]
    chosen = max(fitting or sizes, key=lambda size: int(size.get("width") or 0))
    return str(chosen["url"])


def post_from_vk(item: Dict[str, Any], group: str) -> Post:
    """Одна запись `wall.get` → Post."""
    post_id = int(item.get("id") or 0)
    owner_id = int(item.get("owner_id") or 0)
    photos: List[str] = []
    links: List[Dict[str, str]] = []
    videos: List[str] = []

    for attachment in item.get("attachments") or []:
        kind = attachment.get("type")
        if kind == "photo":
            url = _pick_photo(attachment.get("photo") or {})
            if url:
                photos.append(url)
        elif kind == "link":
            link = attachment.get("link") or {}
            links.append(
                {
                    "title": htmllib.unescape(str(link.get("title") or "")),
                    "url": str(link.get("url") or ""),
                }
            )
        elif kind in ("video", "short_video"):
            video = attachment.get("video") or {}
            videos.append(str(video.get("title") or "видео"))

    copy_from = ""
    history = item.get("copy_history") or []
    if history and isinstance(history[0], dict):
        copy_from = str(history[0].get("owner_id") or "")

    return Post(
        id=post_id,
        owner_id=owner_id,
        date=_iso(item.get("date")),
        # В prefetch-кэше страницы текст приходит с HTML-сущностями (&#9889;),
        # хотя официальный API отдаёт обычный текст. Декодируем в обоих случаях.
        text=htmllib.unescape(str(item.get("text") or "")).strip(),
        url=f"https://vk.com/wall{owner_id}_{post_id}",
        views=int((item.get("views") or {}).get("count") or 0),
        likes=int((item.get("likes") or {}).get("count") or 0),
        photos=photos,
        links=links,
        videos=videos,
        is_pinned=bool(item.get("is_pinned")),
        copy_from=copy_from,
    )


# --- режим 1: официальный API по токену ---------------------------------
def fetch_api(
    domain: str,
    token: str,
    limit: int = 0,
    delay: float = 0.35,
    progress=print,
) -> List[Post]:
    posts: List[Post] = []
    offset = 0
    with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        while True:
            params = {
                "domain": domain,
                "count": 100,
                "offset": offset,
                "access_token": token,
                "v": API_VERSION,
            }
            try:
                response = client.get(API_URL, params=params)
                payload = response.json()
            except Exception as exc:  # noqa: BLE001
                progress(f"  ! запрос {offset}: {type(exc).__name__}: {exc}")
                break
            if "error" in payload:
                error = payload["error"]
                progress(f"  ! VK API {error.get('error_code')}: {error.get('error_msg')}")
                break
            body = payload.get("response") or {}
            items = body.get("items") or []
            total = body.get("count") or 0
            if not items:
                break
            posts.extend(post_from_vk(item, domain) for item in items)
            progress(f"  {len(posts)}/{total} постов (offset {offset})")
            if limit and len(posts) >= limit:
                break
            if len(posts) >= total:
                break
            offset += len(items)
            time.sleep(delay)
    return posts[:limit] if limit else posts


# --- режим 2: страница сообщества без токена ----------------------------
def _slice_object(text: str, start: int) -> Optional[str]:
    """Вырезает сбалансированный JSON-объект, начиная с фигурной скобки."""
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def _prefetch_value(text: str, method: str, key: str) -> Optional[Any]:
    """Достаёт `key` из ответа метода в prefetch-кэше страницы."""
    marker = f'"method":"{method}"'
    index = text.find(marker)
    if index == -1:
        return None
    key_index = text.find(f'"{key}":', index)
    if key_index == -1:
        return None
    brace = text.find("{", key_index)
    if brace == -1:
        return None
    raw = _slice_object(text, brace)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def fetch_page(domain: str, limit: int = 0, progress=print) -> Tuple[List[Post], int]:
    """Без токена: только те посты, что VK положил в prefetch-кэш страницы."""
    with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        response = client.get(f"https://vk.com/{domain}")
    html = response.text

    response_json = _prefetch_value(html, "wall.get", "response") or {}
    items = response_json.get("items") or []
    total = int(response_json.get("count") or 0)
    progress(f"  страница отдала {len(items)} постов из {total} (гостю больше не показывает)")
    posts = [post_from_vk(item, domain) for item in items]
    return (posts[:limit] if limit else posts), total


# --- вывод --------------------------------------------------------------
def _excerpt(post: Post, width: int = 90) -> str:
    flat = " ".join(post.text.split())
    if flat:
        first = re.split(r"(?<=[.!?])\s+", flat)[0]
        if len(first) > width:
            first = first[: width - 1].rsplit(" ", 1)[0] + "…"
        return first
    kind = "видео" if post.videos else ("фото" if post.photos else "пост")
    return f"UserGate ВКонтакте: {kind} от {post.iso_date or 'без даты'} (№{post.id})"


def render_markdown(post: Post) -> str:
    lines = [f"# {_excerpt(post)}", ""]

    meta = [f"Дата: {post.iso_date or '—'}", f"Пост: {post.id}"]
    if post.views:
        meta.append(f"Просмотры: {post.views}")
    if post.likes:
        meta.append(f"Лайки: {post.likes}")
    if post.is_pinned:
        meta.append("закреплён")
    lines.append(" · ".join(meta))

    if post.copy_from:
        lines.append(f"Репост из: {post.copy_from}")
    lines.append("")

    if post.text:
        lines.append(post.text)
        lines.append("")

    for link in post.links:
        title = link.get("title") or link.get("url") or ""
        url = link.get("url") or ""
        lines.append(f"Ссылка в посте: {title}" + (f" — {url}" if url and url != title else ""))
    if post.links:
        lines.append("")

    media: List[str] = []
    if post.photos:
        media.append(f"изображений {len(post.photos)}")
    if post.videos:
        media.append(f"видео {len(post.videos)}")
    if media:
        lines.append("Медиа: " + ", ".join(media))
        lines.extend(post.photos)
        lines.append("")

    lines.append(f"Источник: {post.url}")
    return "\n".join(lines).strip() + "\n"


def write_catalog(posts: List[Post], path: Path, total: int, mode: str, opened: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["id", "дата", "заголовок", "url", "тип", "что_берём", "куда", "статус", "примечание"]
        )
        for post in posts:
            note = f"ВКонтакте, просмотров {post.views}, обращение {opened}"
            if mode == "page":
                note += f"; выгружено {len(posts)} из {total} — без токена VK отдаёт только свежие"
            writer.writerow(
                [
                    f"VK-{post.id}",
                    post.iso_date or "—",
                    _excerpt(post),
                    post.url,
                    post_kind(post),
                    "—",
                    "02-media/vk/, news/",
                    "собран" if post.has_content else "нет данных",
                    note,
                ]
            )
    return len(posts)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Экспорт постов сообщества ВКонтакте")
    parser.add_argument("--group", default="usergaterus", help="короткое имя сообщества")
    parser.add_argument("--token", default="", help="access token VK (иначе берётся VK_TOKEN)")
    parser.add_argument("--limit", type=int, default=0, help="сколько постов взять (0 — все)")
    parser.add_argument("--delay", type=float, default=0.35, help="пауза между запросами, сек")
    parser.add_argument("--archive", default="data-temp/vk", help="каталог сырого архива JSONL")
    parser.add_argument("--md-dir", default="data-temp/02-media/vk", help="каталог markdown")
    parser.add_argument("--catalog", default="data-temp/02-media/vk.csv", help="CSV-каталог источников")
    parser.add_argument(
        "--from-archive",
        default="",
        help="пересобрать markdown из готового JSONL, не обращаясь к VK",
    )
    args = parser.parse_args(argv)
    force_utf8_stdout()

    group = args.group.lstrip("@").strip()
    started = time.perf_counter()
    total = 0
    mode = "api"

    if args.from_archive:
        source = Path(args.from_archive)
        if not source.is_file():
            print(f"! архив не найден: {source}")
            return 1
        rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
        posts = [Post(**{key: value for key, value in row.items() if key in Post.__dataclass_fields__}) for row in rows]
        total = len(posts)
        print(f"→ Сообщество: {group} · из архива {len(posts)} постов")
    else:
        token = args.token or os.environ.get("VK_TOKEN", "").strip()
        mode = "api" if token else "page"
        print(f"→ Сообщество: {group} · режим: {'API по токену' if token else 'страница без токена'}")
        if token:
            posts = fetch_api(group, token, limit=args.limit, delay=args.delay)
            total = len(posts)
        else:
            posts, total = fetch_page(group, limit=args.limit)
            print("  подсказка: для полной стены нужен service token VK — см. README инструмента")

    if not posts:
        print("! постов не найдено")
        return 1

    ordered = sorted(posts, key=lambda post: (post.date, post.id))

    archive_dir = Path(args.archive)
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{group}.jsonl"
    with archive_path.open("w", encoding="utf-8") as handle:
        for post in ordered:
            handle.write(json.dumps(asdict(post), ensure_ascii=False) + "\n")

    written = 0
    if args.md_dir:
        md_dir = Path(args.md_dir)
        md_dir.mkdir(parents=True, exist_ok=True)
        fresh = set()
        for post in ordered:
            if not post.has_content:
                continue
            name = f"{post.id}.md"
            (md_dir / name).write_text(render_markdown(post), encoding="utf-8")
            fresh.add(name)
            written += 1
        for stale in md_dir.glob("*.md"):
            if stale.stem.isdigit() and stale.name not in fresh:
                stale.unlink()

    catalog_rows = 0
    if args.catalog:
        catalog_rows = write_catalog(
            ordered, Path(args.catalog), total, mode, time.strftime("%Y-%m-%d")
        )

    dates = [post.iso_date for post in ordered if post.iso_date]
    elapsed = time.perf_counter() - started

    print("")
    print("=" * 62)
    print(f"  Готово за {elapsed:.1f} с")
    print(f"  Постов      : {len(ordered)}" + (f" из {total} в сообществе" if total else ""))
    print(f"    с текстом : {sum(1 for post in ordered if post.text)}")
    print(f"    с медиа   : {sum(1 for post in ordered if post.photos or post.videos)}")
    if dates:
        print(f"  Период      : {min(dates)} — {max(dates)}")
    print(f"  Просмотры   : {sum(post.views for post in ordered):,}".replace(",", " "))
    print(f"  Архив       : {archive_path}")
    if written:
        print(f"  Markdown    : {args.md_dir} ({written} файлов)")
    if catalog_rows:
        print(f"  Каталог CSV : {args.catalog} ({catalog_rows} строк)")
    print("=" * 62)
    if mode == "page" and total and len(ordered) < total:
        print("")
        print(f"  ВНИМАНИЕ: выгружено {len(ordered)} из {total}.")
        print("  Для полной стены нужен service token VK (см. README инструмента).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
