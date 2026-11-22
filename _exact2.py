"""Точные формулировки и таблицы: DCFW-журналы, интерфейсы, WAF-матрицы, числа Академии."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
HEADERS = {"User-Agent": UA, "Accept-Language": "ru,en;q=0.9"}
OUT = Path(r"D:\hacaton\partner-agent-temp\exact_report.txt")
lines: list[str] = []


def say(text: str = "") -> None:
    lines.append(text)


def article(soup: BeautifulSoup):
    return soup.select_one("#kbp_article_body") or soup.select_one(".articleContainer")


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def dump_tables(soup: BeautifulSoup, limit: int = 4) -> None:
    for index, table in enumerate(soup.find_all("table")[:limit], start=1):
        rows = []
        for tr in table.find_all("tr"):
            cells = [flat(cell.get_text(" ", strip=True)) for cell in tr.find_all(["th", "td"])]
            if any(cells):
                rows.append(cells)
        if not rows:
            continue
        say(f"  таблица {index}: {len(rows)} строк")
        for row in rows[:8]:
            say("    | " + " | ".join(row))


with httpx.Client(timeout=60, follow_redirects=True, headers=HEADERS) as client:
    # 1. Журналы DCFW
    say("=" * 78)
    say("1. ЖУРНАЛЫ DCFW 8.x")
    response = client.get("https://docs.usergate.com/funkcional6nye-vozmozhnosti_2248.html")
    soup = BeautifulSoup(response.text, "html.parser")
    node = article(soup)
    text = flat(node.get_text(" ", strip=True)) if node else ""
    say(f"  HTTP {response.status_code}, текста {len(text)}")
    for match in re.finditer(r"Журнал[^.]{0,120}", text):
        say("  •", match.group(0).strip())
    dump_tables(soup, limit=2)

    # 2. Интерфейсы
    say("=" * 78)
    say("2. РАЗДЕЛ «ИНТЕРФЕЙСЫ»")
    response = client.get("https://docs.usergate.com/nastrojka-interfejsov_383.html")
    soup = BeautifulSoup(response.text, "html.parser")
    node = article(soup)
    text = flat(node.get_text(" ", strip=True)) if node else ""
    say(f"  HTTP {response.status_code}, текста {len(text)}")
    for pattern in (
        r"Раздел отображает[^.]{0,220}\.",
        r"При создании VLAN необходимо указать[^.]{0,200}\.",
        r"При создании бонда необходимо указать[^.]{0,220}\.",
        r"Кнопка Добавить позволяет[^.]{0,200}\.",
    ):
        for match in re.finditer(pattern, text):
            say("  • " + match.group(0).strip())

    # 3. WAF-матрицы
    say("=" * 78)
    say("3. МАТРИЦЫ СОВМЕСТИМОСТИ WAF")
    for name, url in (
        ("3406 (7.6.0)", "https://docs.usergate.com/sovmestimost6-versij-usergate-waf-s-apparatnymi-platformami_3406.html"),
        ("3409 (7.x)", "https://docs.usergate.com/sovmestimost6-versij-usergate-waf-s-apparatnymi-platformami_3409.html"),
    ):
        response = client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        node = article(soup)
        text = flat(node.get_text(" ", strip=True)) if node else ""
        say(f"  --- {name}: HTTP {response.status_code}, текста {len(text)}")
        say("  " + text[:500])
        dump_tables(soup, limit=2)

    # 4. Числа Академии
    say("=" * 78)
    say("4. ЧИСЛА АКАДЕМИИ (архив)")
    try:
        response = client.get("https://web.archive.org/web/2026/https://usergate.com/academy")
        soup = BeautifulSoup(response.text, "html.parser")
        text = flat(soup.get_text(" ", strip=True))
        say(f"  HTTP {response.status_code}, текста {len(text)}")
        for pattern in (r"\d+\s*авторизованн[^.]{0,60}", r"\d+\s*учебных завед[^.]{0,40}",
                        r"6800[^.]{0,80}", r"2800[^.]{0,60}", r"\d+\s*преподавател[^.]{0,40}"):
            for match in re.finditer(pattern, text) if False else re.finditer(pattern, text):
                say("  • " + match.group(0).strip())
    except Exception as exc:  # noqa: BLE001
        say("  ОШИБКА:", type(exc).__name__, exc)

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("готово:", OUT.name, "строк:", len(lines))
