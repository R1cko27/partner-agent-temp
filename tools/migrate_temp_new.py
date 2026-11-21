"""Миграция новых файлов из data-temp в data: отзывы, Академия, версии."""

from __future__ import annotations

import csv
import io
import json
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = pathlib.Path(".")
TEMP = ROOT / "data-temp"
DATA = ROOT / "data/company"
REVIEWS = DATA / "about" / "reviews"


def write(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")
    print("записан:", path.relative_to(DATA))


def migrate_reviews() -> None:
    source = TEMP / "02-media" / "reviews.json"
    if not source.is_file():
        print("reviews.json не найден")
        return
    payload = json.loads(source.read_text(encoding="utf-8"))
    meta = payload.get("meta") or {}
    sources = payload.get("sources") or []
    aggregates = payload.get("aggregates") or []
    reviews = payload.get("reviews") or []

    lines = [
        "# Отзывы о работодателе UserGate",
        "",
        f"Данные собраны {meta.get('collected_at', '—')} с площадок отзывов. "
        "Шкала приведена к 1–5.",
        "",
        "## Важно про выборку",
        "",
        f"{meta.get('selection', '')} {meta.get('bias_note', '')}".strip(),
        "",
        "## Сводные оценки площадок",
        "",
        "| Площадка | Оценка (1–5) | Отзывов | Рекомендуют | Ссылка |",
        "|---|---:|---:|---:|---|",
    ]
    for item in aggregates:
        lines.append(
            f"| {item.get('source')} | {item.get('rating_5')} | {item.get('reviews_count')} "
            f"| {item.get('recommend_pct') if item.get('recommend_pct') is not None else '—'} "
            f"| {item.get('url')} |"
        )
    lines += ["", "## Площадки", ""]
    for item in sources:
        note = item.get("note") or ""
        lines.append(
            f"- {item.get('name')} — {item.get('url')} (проверено: {item.get('checked_at')}, "
            f"статус: {item.get('status')}){' — ' + note if note else ''}"
        )
    lines += [
        "",
        "## Как отвечать",
        "",
        "- Это отзывы сотрудников о работодателе, а не отзывы клиентов о продуктах.",
        "- Выборка смещена в положительную сторону: средняя по файлу не равна реальному рейтингу.",
        "- Для честной картины нужны все отзывы площадки, а не только отобранные.",
    ]
    write(REVIEWS / "aggregates.md", "\n".join(lines))

    for review in reviews:
        title = f"Отзыв {review.get('source')} от {review.get('date', '—')}"
        body = [
            f"# {title}",
            "",
            f"Оценка: {review.get('rating_5')} из 5. Автор: {review.get('author_display')}. "
            f"Роль: {review.get('role') or '—'}. Город: {review.get('city') or '—'}. "
            f"Занятость: {review.get('employment') or '—'}.",
            "",
            f"Плюсы: {review.get('pros') or '—'}",
            "",
            f"Минусы: {review.get('cons') or '—'}",
            "",
            f"Текст: {review.get('text') or '—'}",
        ]
        if review.get("company_reply"):
            body += ["", f"Ответ компании: {review['company_reply']}"]
        body += [
            "",
            f"Источник: {review.get('url')}",
            f"Собрано: {review.get('collected_at')}",
        ]
        write(REVIEWS / f"{review.get('id', 'review')}.md", "\n".join(body))


def read_csv_rows(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    return [row for row in reader]


def migrate_academy() -> None:
    temp_academy = TEMP / "about" / "academy.md"
    target = DATA / "about" / "academy.md"
    base = temp_academy.read_text(encoding="utf-8") if temp_academy.is_file() else ""
    current = target.read_text(encoding="utf-8") if target.is_file() else ""

    merged = base or current
    # Сохраняем мои добавления про экзамен WAF и цены, если их нет в новом файле.
    additions = []
    if "WAF 7" not in merged:
        additions.append(
            "Экзамен **«Сертифицированный специалист UserGate WAF 7.Х»** подтверждает "
            "подготовку по защите веб-приложений."
        )
    if "35 000" not in merged:
        additions.append(
            "Стоимость: курсы — от 35 000 до 161 000 ₽, экзамены — от 9 000 до 17 500 ₽."
        )

    rows = read_csv_rows(TEMP / "01-web" / "academy.crawled-2026-11-20.csv")
    useful = [
        row for row in rows
        if row.get("id") and row.get("id") not in {"AC-CATALOG", "AC-ACADEMY", "AC-PARTNERSHIP"}
        and (row.get("курс_или_экзамен") or "").strip()
    ]
    if useful and "## Каталог курсов и экзаменов" not in merged:
        table = [
            "",
            "## Каталог курсов и экзаменов",
            "",
            "| Программа | Продукт | Версия | Формат | Длительность | Стоимость | Ссылка |",
            "|---|---|---|---|---|---:|---|",
        ]
        for row in useful:
            table.append(
                f"| {row.get('курс_или_экзамен','').strip()} | {row.get('продукт','').strip() or '—'} "
                f"| {row.get('версия','').strip() or '—'} | {row.get('формат','').strip() or '—'} "
                f"| {row.get('длительность','').strip() or '—'} | {row.get('стоимость','').strip() or '—'} "
                f"| {row.get('url','').strip()} |"
            )
        merged = merged.rstrip() + "\n" + "\n".join(table)

    if additions:
        merged = merged.rstrip() + "\n\n## Дополнительно\n\n" + "\n".join(f"- {item}" for item in additions)

    write(target, merged)


def migrate_versions() -> None:
    temp_versions = TEMP / "docs" / "versions-and-platforms.md"
    target = DATA / "docs" / "versions-and-platforms.md"
    merged = temp_versions.read_text(encoding="utf-8") if temp_versions.is_file() else ""
    if not merged:
        print("versions-and-platforms.md в data-temp нет")
        return
    current = target.read_text(encoding="utf-8") if target.is_file() else ""
    if "## Платформы с отдельными руководствами" not in merged and "Платформы с отдельными" not in merged:
        platforms = sorted(
            item.name.upper() for item in (DATA / "docs" / "hardware").iterdir()
            if item.is_dir() and item.name != "shared"
        )
        if platforms:
            merged = merged.rstrip() + (
                "\n\n## Платформы с отдельными руководствами\n\n"
                f"В базе есть материалы по платформам: {', '.join(platforms)}.\n\n"
                "Каталог и ссылки — `products/hardware-platforms.md`, документы — `docs/hardware/<платформа>/`.\n"
            )
    write(target, merged)


def main() -> int:
    migrate_reviews()
    migrate_academy()
    migrate_versions()
    return 0


if __name__ == "__main__":
    sys.exit(main())
