"""Переносит материалы аппаратных платформ из data-temp в базу знаний.

Структура результата:

    data/company/docs/hardware/
      shared/                       общие документы (IPMI, рельсы) — один раз
      <platform>/                   datasheet + руководство по эксплуатации
    data/company/products/hardware-platforms.md   каталог платформ

Оригиналы PDF остаются в data-temp: в индекс идут только разобранные тексты.
"""

from __future__ import annotations

import io
import pathlib
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SRC = pathlib.Path("data-temp/09-company/products")
DATA = pathlib.Path("data/company")
DOCS = DATA / "docs" / "hardware"
CATALOG = DATA / "products" / "hardware-platforms.md"
VERSIONS = DATA / "docs" / "versions-and-platforms.md"

SHARED_PREFIXES = ("instruction-usergate-ipmi", "instruction-usergate-e-f", "sw-update", "pmc")


def read_csv(path: pathlib.Path) -> dict[str, dict[str, str]]:
    """sources.csv: разделитель ;, первая строка — заголовки."""
    if not path.is_file():
        return {}
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return {}
    header = [item.strip() for item in lines[0].split(";")]
    rows: dict[str, dict[str, str]] = {}
    for line in lines[1:]:
        values = [item.strip() for item in line.split(";")]
        record = dict(zip(header, values))
        parsed = record.get("разобранный_файл") or ""
        if parsed:
            rows[parsed.split("/")[-1]] = record
    return rows


def front_matter(meta: dict[str, str]) -> str:
    order = ("заголовок", "url", "источник", "продукт", "версия", "раздел", "обновлено", "страниц", "получено")
    lines = ["---"]
    for key in order:
        value = meta.get(key)
        if value:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def first_heading(text: str) -> str:
    match = re.search(r"(?m)^#\s+(.+)$", text)
    return match.group(1).strip() if match else ""


def docs_page(folder: pathlib.Path) -> str:
    readme = folder / "README.md"
    if not readme.is_file():
        return ""
    match = re.search(r"Страница документации:\s*\[[^\]]*\]\((https?://[^\s)]+)\)", readme.read_text(encoding="utf-8"))
    return match.group(1) if match else ""


def main() -> int:
    platforms = [
        path for path in SRC.iterdir()
        if path.is_dir() and path.name.startswith("usergate-")
    ]
    platforms.sort(key=lambda item: item.name)

    # Какие разобранные файлы встречаются у нескольких платформ → общие документы.
    usage: dict[str, int] = {}
    for platform in platforms:
        for path in (platform / "parsed").glob("*.md"):
            usage[path.name] = usage.get(path.name, 0) + 1

    DOCS.mkdir(parents=True, exist_ok=True)
    shared_dir = DOCS / "shared"
    shared_dir.mkdir(exist_ok=True)

    imported = 0
    skipped_shared: set[str] = set()
    catalog_rows: list[tuple[str, str, str]] = []

    for platform in platforms:
        slug = platform.name.replace("usergate-", "")
        meta_map = read_csv(platform / "metadata" / "sources.csv")
        page = docs_page(platform)
        target_dir = DOCS / slug
        target_dir.mkdir(exist_ok=True)
        imported_here = 0

        for index, path in enumerate(sorted((platform / "parsed").glob("*.md")), 1):
            record = meta_map.get(path.name, {})
            shared = usage.get(path.name, 0) > 1 or path.name.startswith(SHARED_PREFIXES)

            if shared:
                if path.name in skipped_shared:
                    continue
                skipped_shared.add(path.name)
                target = shared_dir / path.name
            else:
                target = target_dir / f"{index:02d}-{path.name}"

            body = path.read_text(encoding="utf-8").strip()
            title = first_heading(body) or record.get("название") or path.stem
            meta = {
                "заголовок": title,
                "url": record.get("url") or page,
                "источник": "docs.usergate.com / static.usergate.com (PDF)",
                "продукт": f"Платформа {slug.upper()}",
                "версия": record.get("версия") or "",
                "раздел": "Аппаратные платформы",
                "обновлено": record.get("дата_документа") or "",
                "страниц": record.get("страниц") or "",
                "получено": "2026-11-21",
            }
            target.write_text(front_matter(meta) + "\n\n" + body + "\n", encoding="utf-8")
            imported += 1
            imported_here += 1

        catalog_rows.append((slug, page, str(imported_here)))

    # Каталог платформ
    lines = [
        "# Аппаратные платформы UserGate",
        "",
        "Перечень аппаратных платформ, по которым в базе есть отдельные руководства.",
        "Для каждой платформы — технические характеристики и руководство по эксплуатации;",
        "общие документы (IPMI, установка рельс, обновление через PMC) вынесены в `docs/hardware/shared/`.",
        "",
        "| Платформа | Документы в базе | Страница документации |",
        "|---|---|---|",
    ]
    for slug, page, count in catalog_rows:
        lines.append(f"| {slug.upper()} | `docs/hardware/{slug}/` ({count}) | {page or '—'} |")
    lines += [
        "",
        "## Как отвечать",
        "",
        "- Характеристики относятся к конкретной модели: нельзя переносить цифры с одной платформы на другую.",
        "- Если модель не названа в вопросе — уточнить модель, а не давать «средние» значения.",
        "- Измерения в даташитах могут быть выполнены на другой версии ПО; это указывается в документе.",
        "",
        "## Общие документы",
        "",
        "- `docs/hardware/shared/` — IPMI, установка рельс, обновление компонентов ПО через PMC.",
    ]
    CATALOG.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Дополняем карточку версий перечнем платформ
    if VERSIONS.is_file():
        text = VERSIONS.read_text(encoding="utf-8")
        if "hardware-platforms" not in text:
            names = ", ".join(item[0].upper() for item in catalog_rows)
            text = text.rstrip() + (
                "\n\n## Платформы с отдельными руководствами\n\n"
                f"В базе есть материалы по платформам: {names}.\n\n"
                "Каталог и ссылки — `products/hardware-platforms.md`, документы — `docs/hardware/<платформа>/`.\n"
            )
            VERSIONS.write_text(text, encoding="utf-8")
            print("карточка версий дополнена перечнем платформ")

    print(f"платформ: {len(catalog_rows)} · документов импортировано: {imported}")
    print(f"общих документов (один раз): {len(skipped_shared)}")
    print("каталог:", CATALOG.relative_to(DATA))
    return 0


if __name__ == "__main__":
    sys.exit(main())
