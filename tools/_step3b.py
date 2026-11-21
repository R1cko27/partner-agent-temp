"""Шаг 3, доработка: год основания, LACP и запрет переноса сертификата."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")

TOPIC_OLD = '    (("trap", "snmp", "мониторинг"), ("products/dcfw", "funkcional6nye")),'
TOPIC_NEW = TOPIC_OLD + """
    (("основан", "год", "истори", "2006"), ("about/history",)),
    (("lacp", "агрегир", "бонд", "канал"), ("products/ngfw", "products/swg")),"""

CERT_OLD = '''        if _is_enumeration(question):
            # Элементы ищем во фрагментах до ответа'''
CERT_NEW = '''        if _asks_certificate(question):
            lines.append(
                "СЕРТИФИКАТ: в материалах подтверждён только сертификат UserGate NGFW "
                "(№ 3905, 4-й уровень доверия). На другие продукты он не переносится: "
                "если для WAF, SIEM, Client или DCFW номера в контексте нет — так и скажи."
            )
        if _is_enumeration(question):
            # Элементы ищем во фрагментах до ответа'''

HELPER = '''def _asks_certificate(question: str) -> bool:
    """Вопрос про сертификат конкретного продукта."""
    text = (question or "").lower()
    return "сертификат" in text and any(
        word in text for word in ("waf", "siem", "client", "dcfw", "swg", "ngfw")
    )


'''


def main() -> int:
    text = AGENT.read_text(encoding="utf-8")
    changed = []

    if "about/history" not in text:
        text = text.replace(TOPIC_OLD, TOPIC_NEW, 1)
        changed.append("проходы: история и LACP")

    if "_asks_certificate" not in text:
        anchor = "def _looks_like_injection(question: str) -> bool:"
        text = text.replace(anchor, HELPER + anchor, 1)
        changed.append("детектор сертификата")

    if "СЕРТИФИКАТ: в материалах подтверждён" not in text:
        text = text.replace(CERT_OLD, CERT_NEW, 1)
        changed.append("директива о сертификате")

    AGENT.write_text(text, encoding="utf-8")
    print("агент:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
