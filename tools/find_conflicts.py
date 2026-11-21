"""Поиск противоречий и дублей в базе знаний.

    python tools/find_conflicts.py            # отчёт
    python tools/find_conflicts.py --strict   # код возврата 1, если есть противоречия

Что проверяет:

1. **Дубли страниц** — курируемый файл ссылается на тот же URL, который уже
   сохранён краулом. Такие пары расходятся со временем и дают разные значения.
2. **Телефоны** — все номера в базе, сгруппированные по нормализованному виду.
3. **Цены** — любые денежные суммы: база заявляет, что цен в ней нет.
4. **Номера сертификатов и реестровых записей** — все значения с файлами.
5. **Устойчивые факты** — год основания и число сотрудников: если в разных
   местах стоят разные значения, это надо увидеть до защиты.

Инструмент ничего не меняет: только читает `data/company/` и печатает отчёт.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
COMPANY = ROOT / "data" / "company"

PHONE_RE = re.compile(
    r"(?:\+7|\+375|8)[\s\-()]*\d{3}[\s\-()]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}"
)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]{2,}")
PRICE_RE = re.compile(r"\d[\d\s]{2,}\s?(?:₽|руб\.?|рублей|тыс\.?\s?руб|\$|€)")
CERT_RE = re.compile(r"№\s?(\d{3,5})")
FOUNDED_RE = re.compile(r"(?:основан\w*|год основания)[^\d\n]{0,25}(\d{4})", re.I)
STAFF_RE = re.compile(r"(\d{2,4})\+?\s*(?:сотрудник|человек|специалист)", re.I)
URL_RE = re.compile(r"https?://[\w./-]+", re.I)
WORDS_RE = re.compile(r"\w{4,}", re.UNICODE)

# Заведомо примеры и служебные номера из документации и статей.
FAKE_PHONES = {"79123456789", "78005553535", "70000000000", "74950000000"}
CONTACT_FILES = ("about/", "faq/")
CURATED_ROOT_FILES = ("profile.json", "urls.txt")


def human(path: Path) -> str:
    try:
        return path.relative_to(COMPANY).as_posix()
    except ValueError:
        return str(path)


def is_curated(relative: str) -> bool:
    """Материал, который проверили руками, а не сырой обход."""
    if relative.startswith("docs/crawl/"):
        return False
    if relative.startswith(("news/telegram/", "news/vk/")):
        return False
    return True


def iter_files() -> Iterable[Tuple[str, str]]:
    for path in sorted(COMPANY.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".json"}:
            continue
        relative = human(path)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        yield relative, text


def is_contact_file(relative: str) -> bool:
    return relative.startswith(CONTACT_FILES) or relative in CURATED_ROOT_FILES


def is_real_phone(digits: str) -> bool:
    """Отсекает примеры: +7 912 345-67-89, 8 800 555-35-35, нули и несуществующие коды."""
    if digits in FAKE_PHONES:
        return False
    if len(set(digits)) <= 2:
        return False
    if len(digits) == 11 and digits.startswith("7"):
        return digits[1] in "3456789"          # реальные коды РФ начинаются с 3–9
    if len(digits) == 12 and digits.startswith("375"):
        return True
    return False


def containment(small: str, big: str) -> float:
    """Доля слов малого текста, которые встречаются в большом."""
    first = set(WORDS_RE.findall(small.lower()))
    if not first:
        return 0.0
    second = set(WORDS_RE.findall(big.lower()))
    return len(first & second) / len(first)


def front_matter_url(text: str) -> str:
    match = re.search(r"^url:\s*(\S+)\s*$", text[:600], re.M)
    return match.group(1).rstrip("/") if match else ""


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits[0] in "78":
        digits = "7" + digits[1:]
    return digits


def fmt_phone(raw: str) -> str:
    digits = normalize_phone(raw)
    if len(digits) == 11 and digits.startswith("7"):
        return f"+7 {digits[1:4]} {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    if len(digits) == 12 and digits.startswith("375"):
        return f"+375 {digits[3:5]} {digits[5:8]}-{digits[8:10]}-{digits[10:12]}"
    return raw.strip()


def collect() -> Dict[str, object]:
    crawled: Dict[str, str] = {}
    texts: Dict[str, str] = {}
    curated_urls: Dict[str, List[str]] = defaultdict(list)
    phones_contact: Dict[str, Set[str]] = defaultdict(set)
    phones_other: Dict[str, Set[str]] = defaultdict(set)
    emails: Dict[str, Set[str]] = defaultdict(set)
    prices: Dict[str, Set[str]] = defaultdict(set)
    certs: Dict[str, Set[str]] = defaultdict(set)
    founded: Dict[str, Set[str]] = defaultdict(set)
    staff: Dict[str, Set[str]] = defaultdict(set)

    for relative, text in iter_files():
        curated = is_curated(relative)
        texts[relative] = text
        url = front_matter_url(text)
        if url and not curated:
            crawled[url.rstrip("/")] = relative

        if curated:
            for found in URL_RE.findall(text):
                clean = found.rstrip("/")
                if clean.startswith(("https://usergate.com", "https://docs.usergate.com")):
                    curated_urls[clean].append(relative)

        for raw in PHONE_RE.findall(text):
            digits = normalize_phone(raw)
            if not is_real_phone(digits):
                continue
            bucket = phones_contact if is_contact_file(relative) else phones_other
            bucket[digits].add(relative)
        for mail in EMAIL_RE.findall(text):
            emails[mail.lower()].add(relative)
        for price in PRICE_RE.findall(text):
            prices[price.strip()].add(relative)
        for number in CERT_RE.findall(text):
            certs[number].add(relative)
        for year in FOUNDED_RE.findall(text):
            founded[year].add(relative)
        for count in STAFF_RE.findall(text):
            number = int(count)
            if 1900 <= number <= 2100:      # это год, а не численность
                continue
            if 50 <= number <= 20000:
                staff[count].add(relative)

    duplicates = []
    for url, files in curated_urls.items():
        if url not in crawled:
            continue
        crawled_file = crawled[url]
        crawled_text = texts.get(crawled_file, "")
        for curated_file in sorted(set(files)):
            share = containment(texts.get(curated_file, ""), crawled_text)
            duplicates.append((url, crawled_file, curated_file, share))
    duplicates.sort(key=lambda item: -item[3])

    return {
        "crawled": crawled,
        "duplicates": duplicates,
        "phones_contact": phones_contact,
        "phones_other": phones_other,
        "emails": emails,
        "prices": prices,
        "certs": certs,
        "founded": founded,
        "staff": staff,
        "texts": texts,
    }


def section(title: str, lines: List[str]) -> None:
    print()
    print(title)
    if not lines:
        print("  — нет")
        return
    for line in lines:
        print(f"  {line}")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Противоречия и дубли в базе знаний")
    parser.add_argument("--strict", action="store_true", help="вернуть 1 при находках")
    args = parser.parse_args(argv)

    data = collect()
    problems = 0

    # 1. Пересечение курируемого файла и крауленной страницы.
    dup_lines = []
    quote_lines = []
    for url, crawled_file, curated_file, share in data["duplicates"]:  # type: ignore[union-attr]
        line = f"{url}\n      краул: {crawled_file}\n      курируемое: {curated_file}"
        if share >= 0.6:
            problems += 1
            dup_lines.append(f"[{share:.0%} текста совпадает] {line}")
        else:
            quote_lines.append(f"[{share:.0%}] {curated_file} -> {url}")

    # 2. Телефоны: сначала те, что в контактных файлах.
    contact: Dict[str, Set[str]] = data["phones_contact"]  # type: ignore[assignment]
    other: Dict[str, Set[str]] = data["phones_other"]  # type: ignore[assignment]
    phone_lines = []
    for digits, files in sorted(contact.items()):
        files_list = sorted(files)
        phone_lines.append(
            f"{fmt_phone(digits):22} {len(files_list)} файл(ов): {', '.join(files_list)}"
        )
    if len(contact) > 1:
        problems += 1
    other_lines = [
        f"{fmt_phone(digits):22} {len(files)} файл(ов), напр. {sorted(files)[0]}"
        for digits, files in sorted(other.items(), key=lambda item: -len(item[1]))[:6]
    ]

    # 3. Цены: база заявляет, что их нет для продуктов — проверяем формулировку FAQ.
    prices: Dict[str, Set[str]] = data["prices"]  # type: ignore[assignment]
    price_lines = []
    if prices:
        academy = 0
        for files in prices.values():
            if any("akadem" in name or "kursy" in name or "ekzamen" in name for name in files):
                academy += 1
        price_lines.append(
            f"всего видов цен: {len(prices)}, из них на страницах Академии: {academy}"
        )
        for value, files in sorted(prices.items(), key=lambda item: -len(item[1]))[:5]:
            price_lines.append(f"{value[:24]:26} напр. {sorted(files)[0]}")
        texts: Dict[str, str] = data["texts"]  # type: ignore[assignment]
        claim = texts.get("faq/pricing.md", "")
        if prices and "не указана" in claim:
            problems += 1
            price_lines.append(
                "! faq/pricing.md утверждает, что цен нет, а они в базе есть — нужно уточнить формулировку"
            )

    # 4. Сертификаты и реестровые номера.
    certs: Dict[str, Set[str]] = data["certs"]  # type: ignore[assignment]
    cert_lines = [f"№ {number:8} {', '.join(sorted(files)[:3])}" for number, files in sorted(certs.items())]

    # 5. Устойчивые факты: основание и численность.
    founded: Dict[str, Set[str]] = data["founded"]  # type: ignore[assignment]
    staff: Dict[str, Set[str]] = data["staff"]  # type: ignore[assignment]
    fact_lines = []
    if len(founded) > 1:
        problems += 1
        fact_lines.append("год основания расходится: " + "; ".join(
            f"{year} — {', '.join(sorted(files)[:2])}" for year, files in sorted(founded.items())
        ))
    if len(staff) > 1:
        problems += 1
        fact_lines.append("численность расходится: " + "; ".join(
            f"{value} — {', '.join(sorted(files)[:2])}" for value, files in sorted(staff.items(), key=lambda i: i[0])
        ))

    print("=" * 78)
    print("Противоречия и дубли в базе знаний")
    print(f"файлов просмотрено: {len(data['texts'])} · страниц в крауле: {len(data['crawled'])}")
    print("=" * 78)

    section("1. Один и тот же материал: курируемый файл и крауленная страница", dup_lines)
    section("   (для сравнения) курируемые файлы ссылаются на крауленные страницы:", quote_lines[:10])
    section(f"2. Телефоны в контактных файлах (значений: {len(contact)}):", phone_lines)
    section("   прочие номера в базе (примеры, партнёры, документация):", other_lines)
    section(f"3. Денежные суммы (видов: {len(prices)}):", price_lines)
    section(f"4. Номера сертификатов и реестров ({len(certs)}):", cert_lines)
    section("5. Устойчивые факты:", fact_lines)

    print()
    print(f"Итого замечаний: {problems}")
    if args.strict and problems:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
