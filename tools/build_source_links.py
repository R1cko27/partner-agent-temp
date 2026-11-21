"""Карта «файл материала → публичная ссылка».

Нужна, чтобы модель в блоке «Источники» давала ссылки, а не имена файлов:
у крауленных страниц URL лежит в шапке файла, у курируемых карточек — в тексте.

    python tools/build_source_links.py

Пишет `data/company/source-links.json`: {"путь относительно data/company": "url"}.
Запускать после изменения базы; в индекс файл не попадает (лежит вне папок материалов).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPANY = ROOT / "data" / "company"
TARGET = COMPANY / "source-links.json"

URL_RE = re.compile(r"https?://[^\s\)\]\"'<>«»]+", re.I)
# Домены, которые считаем подтверждающими источниками.
PREFERRED = (
    "docs.usergate.com",
    "usergate.com",
    "t.me/usergate",
    "habr.com",
    "vk.com",
)


def clean_url(value: str) -> str:
    url = value.strip().rstrip(".,;:)»\"'")
    # Убираем метки трекинга вместе с разделителем, иначе адрес склеивается.
    url = re.sub(
        r"[?&](utm_[^&]+|ysclid=[^&]+|yclid=[^&]+|from=[^&]+|etext=[^&]+|erid=[^&]+"
        r"|gclid=[^&]+|_openstat=[^&]+|fbclid=[^&]+)",
        "",
        url,
        flags=re.I,
    )
    return url.rstrip("?&")


def front_matter_url(text: str) -> str:
    match = re.search(r"^url:\s*(\S+)\s*$", text[:600], re.M)
    return clean_url(match.group(1)) if match else ""


def best_url(text: str) -> str:
    """Первый URL из предпочтительных доменов, иначе первый вообще."""
    found = [clean_url(item) for item in URL_RE.findall(text)]
    for url in found:
        if any(domain in url for domain in PREFERRED):
            return url
    return found[0] if found else ""


# Курируемые карточки — пересказ конкретных страниц. Автовыбор по тексту тут
# ошибается (берёт первую попавшуюся ссылку из блока «Источники»), поэтому
# каноническая страница задаётся явно.
EXACT = {
    "about/company.md": "https://usergate.com/",
    "about/history.md": "https://usergate.com/",
    "about/partners.md": "https://usergate.com/for-partners",
    "about/contacts.md": "https://usergate.com/contacts",
    "about/careers.md": "https://usergate.com/company/career",
    "about/ecosystem-summa.md": "https://usergate.com/summa",
    "faq/products.md": "https://usergate.com/products",
    "faq/certification.md": "https://usergate.com/registry-entry",
    "faq/pricing.md": "https://usergate.com/purchase",
    "faq/education.md": "https://usergate.com/academy",
    "faq/contacts.md": "https://usergate.com/contacts",
    "news/2026-04-certificate-ngfw.md": "https://usergate.com/registry-entry",
    "docs/versions-and-platforms.md": "https://docs.usergate.com/dokumentaciya-120/",
    "docs/source-registry.md": "https://docs.usergate.com/",
    "docs/limitations-and-unknowns.md": "https://usergate.com/registry-entry",
}
# Префиксные правила для однотипных папок.
PREFIX = (
    ("products/", "https://usergate.com/products"),
    ("docs/crawl/", ""),   # берём URL самой страницы из шапки
)

# Для выгрузок соцсетей ссылка — это адрес конкретного поста, а не первой
# попавшейся страницы из текста.
PREFERRED_DOMAIN = (
    ("news/telegram/", "t.me/"),
    ("news/vk/", "vk.com/"),
)


def preferred_url(relative: str, text: str) -> str:
    for prefix, domain in PREFERRED_DOMAIN:
        if not relative.startswith(prefix):
            continue
        for raw in URL_RE.findall(text):
            url = clean_url(raw)
            if domain in url:
                return url
    return ""


def override_for(relative: str) -> str:
    if relative in EXACT:
        return EXACT[relative]
    for prefix, url in PREFIX:
        if relative.startswith(prefix):
            return url
    return ""


def main() -> int:
    mapping: dict[str, str] = {}
    skipped = 0
    for path in sorted(COMPANY.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        relative = path.relative_to(COMPANY).as_posix()
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            skipped += 1
            continue
        url = front_matter_url(text) or preferred_url(relative, text) or best_url(text)
        url = override_for(relative) or url
        if not url:
            skipped += 1
            continue
        mapping[relative] = url

    # ссылки этих файлов не нужны: они не материалы
    for name in ("README.md", "urls.txt", "source-links.json"):
        mapping.pop(name, None)

    TARGET.write_text(
        json.dumps(mapping, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8"
    )
    print(f"файлов со ссылкой: {len(mapping)}")
    print(f"без ссылки (пропущено): {skipped}")
    print(f"записано: {TARGET.relative_to(ROOT)}")
    for sample in list(mapping.items())[:5]:
        print(f"  {sample[0]:38} -> {sample[1][:60]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
