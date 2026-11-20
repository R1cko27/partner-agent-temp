"""Экспорт постов публичного Telegram-канала в файлы.

Источник — веб-превью `https://t.me/s/<channel>`, которое Telegram отдаёт без
авторизации и постранично: `?before=<id>` возвращает посты старше указанного.
Скрипт забирает всю доступную историю, сохраняет сырой архив в JSONL и
генерирует markdown-файлы, которые подхватывает `ingest.py`.

    python tools/export_telegram.py                        # весь канал
    python tools/export_telegram.py --limit 100            # последние 100 постов
    python tools/export_telegram.py --md-dir ""            # только архив, без markdown

Готовые markdown попадают в `data/company/news/telegram/`: папка `news`
превращает их в карточки-новости (`domain/sources.py`, `FOLDER_KIND`), поэтому
после экспорта достаточно пересобрать индекс — `python ingest.py`.

Ограничения превью: посты, которые Telegram не показывает в веб-версии
(стикеры, гифки, часть медиа), приходят заглушкой «Please open Telegram to view
this post». Такие посты попадают в архив с `unsupported: true`, но markdown для
них не создаётся — переносить в базу нечего.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

BASE = "https://t.me"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
    ),
    "Accept-Language": "ru,en;q=0.9",
}
MAX_PAGES = 600

# Служебные подписи веб-превью, которые попадают в текст и мешают поиску.
NOISE = (
    "Please open Telegram to view this post",
    "VIEW IN TELEGRAM",
    "Media is too big",
)

# Служебные сообщения канала: в базе знаний они бесполезны.
SERVICE_TEXTS = {
    "channel created",
    "channel photo updated",
    "channel photo removed",
    "channel name was changed",
    "channel name changed",
    "message pinned",
    "pinned a message",
}


@dataclass
class Post:
    id: int
    date: str
    text: str
    url: str
    views: int = 0
    photos: List[str] = field(default_factory=list)
    has_video: bool = False
    forwarded_from: str = ""
    link_title: str = ""
    link_url: str = ""
    reply_to: str = ""
    unsupported: bool = False

    @property
    def iso_date(self) -> str:
        return self.date[:10] if self.date else ""

    @property
    def has_content(self) -> bool:
        if self.is_service:
            return False
        return bool(self.text or self.photos or self.has_video or self.link_title)

    @property
    def is_service(self) -> bool:
        """«Channel created» и подобные системные записи канала."""
        flat = " ".join(self.text.split()).lower()
        return flat in SERVICE_TEXTS


def _views(raw: str) -> int:
    """«1.2K» / «3 757» → число."""
    digits = re.sub(r"[^\d.,KkMm]", "", raw or "").replace(",", ".")
    if not digits:
        return 0
    multiplier = 1
    if digits[-1] in "Kk":
        multiplier, digits = 1000, digits[:-1]
    elif digits[-1] in "Mm":
        multiplier, digits = 1_000_000, digits[:-1]
    try:
        return int(float(digits) * multiplier)
    except ValueError:
        return 0


def _clean(text: str) -> str:
    for noise in NOISE:
        text = text.replace(noise, "")
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _text_of(node) -> str:
    """Текст узла: переносы строк сохраняются, ссылки — в виде markdown."""
    if node is None:
        return ""
    for br in node.find_all("br"):
        br.replace_with("\n")
    for link in node.find_all("a"):
        href = html.unescape((link.get("href") or "").strip())
        label = link.get_text(" ", strip=True)
        if href.startswith(("http://", "https://")) and label and href != label:
            link.replace_with(f"[{label}]({href})")
        elif href and not label:
            link.replace_with(href)
    return _clean(node.get_text("", strip=False))


def _main_text(message) -> str:
    """Текст самого поста, а не цитаты ответа: у ответов два блока текста."""
    for node in message.select("div.tgme_widget_message_text"):
        classes = node.get("class") or []
        if "js-message_reply_text" in classes:
            continue
        text = _text_of(node)
        if text:
            return text
    return ""


def _reply_text(message) -> str:
    node = message.select_one(".tgme_widget_message_reply .js-message_reply_text")
    return _text_of(node)[:300]


def _date(message) -> str:
    """Дата поста. У части сообщений разметка битая, поэтому есть запасной regex."""
    time_tag = message.find("time")
    if time_tag and time_tag.get("datetime"):
        return str(time_tag["datetime"])
    match = re.search(r'datetime="([^"]+)"', str(message))
    return match.group(1) if match else ""


def _photos(message) -> List[str]:
    urls: List[str] = []
    for wrap in message.select("a.tgme_widget_message_photo_wrap"):
        style = wrap.get("style") or ""
        match = re.search(r"url\(['\"]?(.+?)['\"]?\)", style)
        if match:
            url = match.group(1).replace("\\", "")
            if url not in urls:
                urls.append(url)
    return urls


def parse_page(html: str, channel: str) -> List[Post]:
    """Разбирает одну страницу превью (посты идут от старых к новым)."""
    soup = BeautifulSoup(html, "html.parser")
    posts: List[Post] = []

    for message in soup.select("div.tgme_widget_message[data-post]"):
        if message.select_one(".service_message"):
            continue
        data_post = message.get("data-post") or ""
        tail = data_post.rsplit("/", 1)[-1]
        if not tail.isdigit():
            continue
        post_id = int(tail)

        views_node = message.select_one(".tgme_widget_message_views")
        forwarded = message.select_one(".tgme_widget_message_forwarded_from_name")
        preview = message.select_one("a.tgme_widget_message_link_preview")

        post = Post(
            id=post_id,
            date=_date(message),
            text=_main_text(message),
            url=f"{BASE}/{channel}/{post_id}",
            views=_views(views_node.get_text(strip=True) if views_node else ""),
            photos=_photos(message),
            has_video=bool(
                message.select_one(".tgme_widget_message_video_player")
                or message.select_one(".tgme_widget_message_roundvideo_player")
            ),
            forwarded_from=forwarded.get_text(" ", strip=True) if forwarded else "",
            link_title=(
                preview.select_one(".link_preview_title").get_text(" ", strip=True)
                if preview and preview.select_one(".link_preview_title")
                else ""
            ),
            link_url=(preview.get("href") or "") if preview else "",
            reply_to=_reply_text(message),
            unsupported=bool(message.select_one(".message_media_not_supported_wrap")),
        )
        posts.append(post)

    return posts


def fetch_all(
    channel: str,
    limit: int = 0,
    delay: float = 0.5,
    progress=print,
) -> List[Post]:
    """Листает превью назад по `?before=<id>`, пока не кончится история."""
    seen: Dict[int, Post] = {}
    url = f"{BASE}/s/{channel}"

    with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        for page in range(1, MAX_PAGES + 1):
            try:
                response = client.get(url)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                progress(f"  ! страница {page}: {exc}")
                break

            fresh = [post for post in parse_page(response.text, channel) if post.id not in seen]
            if not fresh:
                break
            for post in fresh:
                seen[post.id] = post

            ids = sorted(seen)
            progress(
                f"  страница {page}: +{len(fresh)} (всего {len(seen)}, "
                f"диапазон {ids[0]}–{ids[-1]})"
            )
            if limit and len(seen) >= limit:
                break
            if ids[0] <= 1:
                break

            url = f"{BASE}/s/{channel}?before={ids[0]}"
            time.sleep(delay)

    ordered = [seen[key] for key in sorted(seen, reverse=True)]
    return ordered[:limit] if limit else ordered


def _excerpt(post: Post, channel: str, width: int = 90) -> str:
    """Короткий уникальный заголовок: первая содержательная строка поста."""
    flat = " ".join(post.text.split())
    if flat:
        first = re.split(r"(?<=[.!?])\s+", flat)[0]
        if len(first) > width:
            first = first[: width - 1].rsplit(" ", 1)[0] + "…"
        return first
    kind = "видео" if post.has_video else ("фото" if post.photos else "пост")
    stamp = post.iso_date or "без даты"
    return f"UserGate News: {kind} от {stamp} (№{post.id})"


def render_markdown(post: Post, channel: str) -> str:
    """Markdown для RAG: заголовок, метаданные, текст, источник."""
    lines = [f"# {_excerpt(post, channel)}", ""]

    meta = [f"Дата: {post.iso_date or '—'}", f"Пост: {post.id}"]
    if post.views:
        meta.append(f"Просмотры: {post.views}")
    lines.append(" · ".join(meta))

    if post.forwarded_from:
        lines.append(f"Переслано из: {post.forwarded_from}")
    if post.reply_to:
        lines.append(f"Ответ на пост: {post.reply_to}")
    lines.append("")

    if post.text:
        lines.append(post.text)
        lines.append("")

    if post.link_title or post.link_url:
        link = post.link_title or post.link_url
        lines.append(f"Ссылка в посте: {link}" + (f" — {post.link_url}" if post.link_url else ""))
        lines.append("")

    media: List[str] = []
    if post.photos:
        media.append(f"изображений {len(post.photos)}")
    if post.has_video:
        media.append("видео")
    if media:
        lines.append("Медиа: " + ", ".join(media))
        lines.extend(post.photos)
        lines.append("")

    lines.append(f"Источник: {post.url}")
    return "\n".join(lines).strip() + "\n"


def _force_utf8_stdout() -> None:
    """Русская консоль Windows отдаёт cp1251, а в выводе есть «→» и «·»."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


# Тип поста выводится из его текста, без домыслов: если признаков нет — «новость».
KIND_RULES = (
    ("разбор угрозы", ("уязвим", "cve-", "эксплуат", "атак", "вредонос", "угроз")),
    ("анонс", ("вебинар", "конференц", "медиатур", "регистрац", "приглаша", "мероприят", "встреч")),
    ("релиз", ("релиз", "верси", "обновлен", "выпустил", "вышл", "доступн")),
    ("исследование", ("исследован", "отчёт", "отчет", "аналитик")),
)


def post_kind(post: Post) -> str:
    text = (post.text or "").lower()
    for label, markers in KIND_RULES:
        if any(marker in text for marker in markers):
            return label
    return "новость"


def write_catalog(posts: List[Post], path: Path, channel: str, opened: str) -> int:
    """Каталог источников в формате остальных CSV из data-temp (разделитель «;»)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            ["id", "дата", "заголовок", "url", "тип", "что_берём", "куда", "статус", "примечание"]
        )
        for post in posts:
            if post.is_service:
                status = "служебный"
                note = "системное сообщение канала"
            elif not post.has_content:
                status = "нет данных"
                note = "Telegram не отдаёт пост в веб-превью"
            else:
                status = "собран"
                note = f"канал @{channel}, просмотров {post.views}, обращение {opened}"
            writer.writerow(
                [
                    f"TG-{post.id}",
                    post.iso_date or "—",
                    _excerpt(post, channel),
                    post.url,
                    post_kind(post),
                    "—",
                    "02-media/telegram/, news/",
                    status,
                    note,
                ]
            )
    return len(posts)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Экспорт постов Telegram-канала")
    parser.add_argument("--channel", default="usergatenews", help="имя канала без @")
    parser.add_argument("--limit", type=int, default=0, help="сколько последних постов взять (0 — все)")
    parser.add_argument("--delay", type=float, default=0.5, help="пауза между страницами, сек")
    parser.add_argument("--archive", default="data-temp/telegram", help="каталог сырого архива JSONL")
    parser.add_argument("--md-dir", default="data/company/news/telegram", help="каталог markdown для ingest")
    parser.add_argument("--catalog", default="", help="CSV-каталог источников (пусто — не писать)")
    parser.add_argument(
        "--from-archive",
        default="",
        help="пересобрать markdown из готового JSONL, не обращаясь к t.me",
    )
    args = parser.parse_args(argv)
    _force_utf8_stdout()

    channel = args.channel.lstrip("@").strip()
    print(f"→ Канал: {channel} · лимит: {args.limit or 'все посты'}")
    started = time.perf_counter()

    if args.from_archive:
        source = Path(args.from_archive)
        if not source.is_file():
            print(f"! архив не найден: {source}")
            return 1
        rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
        posts = [Post(**row) for row in rows]
        print(f"  из архива: {len(posts)} постов")
    else:
        posts = fetch_all(channel, limit=args.limit, delay=args.delay)
    if not posts:
        print("! постов не найдено — проверьте имя канала и доступность t.me")
        return 1

    ordered = sorted(posts, key=lambda post: post.id)

    archive_dir = Path(args.archive)
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{channel}.jsonl"
    with archive_path.open("w", encoding="utf-8") as handle:
        for post in ordered:
            handle.write(json.dumps(asdict(post), ensure_ascii=False) + "\n")

    written = 0
    if args.md_dir:
        md_dir = Path(args.md_dir)
        md_dir.mkdir(parents=True, exist_ok=True)
        fresh: set[str] = set()
        for post in ordered:
            if not post.has_content:
                continue
            name = f"{post.id}.md"
            (md_dir / name).write_text(render_markdown(post, channel), encoding="utf-8")
            fresh.add(name)
            written += 1

        # Убираем файлы прошлых прогонов, которых больше нет в выдаче
        # (например, пост отфильтрован как служебный). Трогаем только
        # числовые имена — чужие файлы в каталоге остаются.
        for stale in md_dir.glob("*.md"):
            if stale.stem.isdigit() and stale.name not in fresh:
                stale.unlink()

    catalog_rows = 0
    if args.catalog:
        catalog_rows = write_catalog(
            ordered,
            Path(args.catalog),
            channel,
            time.strftime("%Y-%m-%d"),
        )

    dates = [post.iso_date for post in ordered if post.iso_date]
    with_text = sum(1 for post in ordered if post.text)
    with_media = sum(1 for post in ordered if post.photos or post.has_video)
    service = sum(1 for post in ordered if post.is_service)
    empty = sum(1 for post in ordered if not post.has_content and not post.is_service)
    total_views = sum(post.views for post in ordered)
    elapsed = time.perf_counter() - started

    print("")
    print("=" * 62)
    print(f"  Готово за {elapsed:.1f} с")
    print(f"  Постов      : {len(ordered)}")
    print(f"    с текстом : {with_text}")
    print(f"    с медиа   : {with_media}")
    print(f"    без данных: {empty} (Telegram не отдаёт их в превью)")
    if service:
        print(f"    служебных : {service} (в базу не идут)")
    if dates:
        print(f"  Период      : {min(dates)} — {max(dates)}")
    print(f"  Просмотры   : {total_views:,}".replace(",", " "))
    print(f"  Архив       : {archive_path}")
    if written:
        print(f"  Markdown    : {args.md_dir} ({written} файлов)")
    if catalog_rows:
        print(f"  Каталог CSV : {args.catalog} ({catalog_rows} строк)")
    print("=" * 62)
    print("")
    print("Дальше: .venv\\Scripts\\python.exe ingest.py   — пересобрать базу знаний")
    return 0


if __name__ == "__main__":
    sys.exit(main())
