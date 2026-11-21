"""VRID и таблица совместимости версий NGFW с платформами."""
from __future__ import annotations

import re
import sys

import httpx
from bs4 import BeautifulSoup

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
HEADERS = {"User-Agent": UA, "Accept-Language": "ru,en;q=0.9"}


def body(url: str) -> str:
    with httpx.Client(timeout=60, follow_redirects=True, headers=HEADERS) as client:
        response = client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    node = soup.select_one("#kbp_article_body") or soup.select_one(".articleContainer")
    if node is None:
        return ""
    for tag in node(["script", "style"]):
        tag.decompose()
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True))


print("=" * 70)
print("КЛАСТЕРЫ: VRID, диапазон, коллизии")
text = body("https://docs.usergate.com/nastrojka-klasterov-(versiya-750-i-vyshe)_2798.html")
print("текста:", len(text))
for pattern in ("vrid", "VRID", "255", "уникал", "коллиз", "диапазон", "1–", "1-" ):
    for match in re.finditer(re.escape(pattern), text):
        start = max(0, match.start() - 120)
        print(f"  [{pattern}] …{text[start:match.start() + 180]}…")
        break

print()
print("=" * 70)
print("СОВМЕСТИМОСТЬ ВЕРСИЙ NGFW С ПЛАТФОРМАМИ")
text2 = body("https://docs.usergate.com/sovmestimost6-versij-usergate-ngfw-s-apparatnymi-platformami_3408.html")
print("текста:", len(text2))
print(text2[:2500])
