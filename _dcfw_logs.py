"""Поиск главы DCFW «Журналы и отчеты» и точных названий журналов."""
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
OUT = Path(r"D:\hacaton\partner-agent-temp\dcfw_logs.txt")
lines: list[str] = []


def say(text: str = "") -> None:
    lines.append(text)


with httpx.Client(timeout=60, follow_redirects=True, headers=HEADERS) as client:
    sitemap = client.get("https://docs.usergate.com/sitemap.xml").text
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap) or re.findall(r"https://docs\.usergate\.com/[^\s<\"']+", sitemap)
    say(f"в карте сайта URL: {len(urls)}")
    candidates = [u for u in urls if re.search(r"zhurnal|otchet", u, re.I)]
    say(f"похожих на журналы/отчёты: {len(candidates)}")
    for url in candidates:
        say("  " + url)

    say("=" * 78)
    say("СОДЕРЖИМОЕ ГЛАВ DCFW ПРО ЖУРНАЛЫ")
    for url in candidates:
        response = client.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        node = soup.select_one("#kbp_article_body") or soup.select_one(".articleContainer")
        if node is None:
            continue
        for tag in node(["script", "style"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
        if "DCFW" not in response.text and "DCFW" not in url:
            continue
        say("-" * 78)
        say(url)
        say(f"  текста: {len(text)}")
        say("  " + text[:1200])
        for match in re.finditer(r"[^.]{0,90}журнал[^.]{0,150}\.", text, re.I):
            say("  • " + match.group(0).strip())

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("готово, строк:", len(lines))
