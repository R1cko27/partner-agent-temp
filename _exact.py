"""Точные формулировки: журналы DCFW, интерфейсы, PDF-раздел WAF, матрицы WAF."""
from __future__ import annotations

import re
import sys

import httpx
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
HEADERS = {"User-Agent": UA, "Accept-Language": "ru,en;q=0.9"}

PAGES = [
    ("DCFW функциональные возможности", "https://docs.usergate.com/funkcional6nye-vozmozhnosti_2248.html",
     ["журнал", "userid", "истории поиска", "dns", "веб-доступ"]),
    ("NGFW интерфейсы", "https://docs.usergate.com/nastrojka-interfejsov_383.html",
     ["интерфейс", "vlan", "бонд", "агрег"]),
    ("PDF-руководства по версиям", "https://docs.usergate.com/dokumentaciya-k-versiyam-po-v-pdf_769.html",
     ["waf", "общий раздел"]),
    ("WAF совместимость 3406", "https://docs.usergate.com/sovmestimost6-versij-usergate-waf-s-apparatnymi-platformami_3406.html",
     ["waf", "платформ"]),
    ("WAF совместимость 3409", "https://docs.usergate.com/sovmestimost6-versij-usergate-waf-s-apparatnymi-platformami_3409.html",
     ["waf", "платформ"]),
]


def fetch(client: httpx.Client, url: str):
    response = client.get(url)
    content_type = response.headers.get("content-type", "")
    soup = BeautifulSoup(response.text, "html.parser")
    node = soup.select_one("#kbp_article_body") or soup.select_one(".articleContainer")
    text = ""
    if node is not None:
        for tag in node(["script", "style"]):
            tag.decompose()
        text = re.sub(r"\s+", " ", node.get_text(" ", strip=True))
    return response, content_type, text, soup


with httpx.Client(timeout=60, follow_redirects=True, headers=HEADERS) as client:
    for name, url, keywords in PAGES:
        print("=" * 78)
        print(name)
        print(url)
        try:
            response, content_type, text, soup = fetch(client, url)
        except Exception as exc:  # noqa: BLE001
            print("  ОШИБКА:", type(exc).__name__, exc)
            continue
        print(f"  HTTP {response.status_code} | content-type: {content_type[:60]}")
        print(f"  текста в статье: {len(text)} символов, всего в ответе: {len(response.text)}")
        if not text:
            title = soup.title.get_text(strip=True) if soup.title else "—"
            print("  title:", title)
            print("  начало ответа:", re.sub(r"\s+", " ", response.text)[:200])
            continue
        print("  начало текста:", text[:400])
        for keyword in keywords:
            positions = [m.start() for m in re.finditer(re.escape(keyword), text, re.I)][:3]
            if not positions:
                print(f"  [{keyword}] — нет")
                continue
            for position in positions:
                start = max(0, position - 110)
                print(f"  [{keyword}] …{text[start:position + 170]}…")
