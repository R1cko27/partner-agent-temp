"""Сбор эталонных фактов для проверки модели.

Три группы:
1. редкие термины из глоссария документации (в базе есть — проверяем извлечение);
2. технические детали из конкретных руководств (в базе есть);
3. datasheet PDF с static.usergate.com (в базе НЕТ — проверяем честность).
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUT = Path("tools/_ground_truth.json")
HEADERS = {"User-Agent": "PartnerAgent-Probe/1.0 (+knowledge base check)"}


def text_of(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()
    for selector in ("[class*=bbcode]", "[class*=share]", "[class*=comment]"):
        for node in soup.select(selector):
            node.decompose()
    return " ".join(soup.get_text(" ", strip=True).split())


def grab(client: httpx.Client, url: str) -> str:
    try:
        response = client.get(url)
    except Exception as exc:  # noqa: BLE001
        print(f"  ERR {url}: {type(exc).__name__}")
        return ""
    return text_of(response.text)


def around(text: str, needle: str, size: int = 320) -> str:
    index = text.lower().find(needle.lower())
    if index < 0:
        return ""
    return text[max(0, index - 40): index + size]


def main() -> int:
    facts: dict[str, dict[str, str]] = {"in_base": {}, "not_in_base": {}}

    with httpx.Client(timeout=30, follow_redirects=True, headers=HEADERS) as client:
        print("=== глоссарий: редкие термины ===")
        glossary = grab(client, "https://docs.usergate.com/glossary/")
        for term in ("BATV", "BFD", "Hairpin", "SAML", "WCCP"):
            snippet = around(glossary, term)
            if snippet:
                facts["in_base"][f"glossary:{term}"] = snippet
                print(f"  {term:8} {snippet[:150]}")

        print("\n=== DCFW 8.x: кластеры и мониторинг ===")
        features = grab(client, "https://docs.usergate.com/funkcional6nye-vozmozhnosti_2248.html")
        for needle, key in (
            ("кластер конфигурации", "dcfw:clusters"),
            ("SNMP v2c", "dcfw:snmp"),
            ("UserID", "dcfw:userid"),
            ("СОВ", "dcfw:ips"),
        ):
            snippet = around(features, needle)
            if snippet:
                facts["in_base"][key] = snippet
                print(f"  {key:16} {snippet[:150]}")

        print("\n=== аппаратные платформы ===")
        platforms = grab(client, "https://docs.usergate.com/apparatnye-platformy-274/")
        facts["in_base"]["platforms:list"] = platforms[:900]
        print("  ", platforms[:260])

        print("\n=== datasheet F8010 (в базе нет) ===")
        try:
            pdf = client.get(
                "https://static.usergate.com/docs/overviews/usergate-ngfw-f8010-datasheet-ru.pdf"
            )
            pdf_path = Path("tools/_f8010.pdf")
            pdf_path.write_bytes(pdf.content)
            from pypdf import PdfReader

            reader = PdfReader(str(pdf_path))
            pdf_text = "\n".join((page.extract_text() or "") for page in reader.pages[:3])
            pdf_text = " ".join(pdf_text.split())
            facts["not_in_base"]["datasheet:f8010"] = pdf_text[:1500]
            print("  ", pdf_text[:400])
            pdf_path.unlink(missing_ok=True)
        except Exception as exc:  # noqa: BLE001
            print("  ERR pdf:", type(exc).__name__, exc)

    OUT.write_text(json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nэталон сохранён: {OUT} · фактов: {sum(len(v) for v in facts.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
