"""Шаг 3: числовые факты компании, SNMP и запрет чужих платформ."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")

TOPIC_OLD = '    (("механизм", "аутентификац", "авторизац"), ("products/dcfw", "glossar")),'
TOPIC_NEW = TOPIC_OLD + """
    (("численност", "сотрудник", "клиент", "проект", "масштаб"), ("about/company",)),
    (("trap", "snmp", "мониторинг"), ("products/dcfw", "funkcional6nye")),"""

GUARD_OLD = '''        hits = self._search_hits(question, k=base_hits)'''
GUARD_NEW = '''        hits = self._search_hits(question, k=base_hits)
        hits = self._drop_foreign_platforms(question, hits)'''

GUARD_METHOD = '''    _PRODUCT_WORDS = ("ngfw", "waf", "dcfw", "swg", "siem", "client", "ucmc", "ugmc")
    _PLATFORM_RE = re.compile(
        r"\\b(b50|c100|c150|c151|d200|d250|d500|e1000|e1010|e3000|e3010|"
        r"f8000|f8010|fg|x1|x10)\\b",
        re.I,
    )

    def _drop_foreign_platforms(
        self, question: str, hits: Sequence[SearchHit]
    ) -> List[SearchHit]:
        """Вопрос про продукт не должен подмешивать даташиты платформ.

        Иначе сертификат или характеристики чужой модели попадают в ответ про
        WAF или SIEM: в даташитах те же слова «сертификат», «порты», «версия».
        """
        lowered = (question or "").lower()
        if self._PLATFORM_RE.search(lowered):
            return list(hits)
        if not any(word in lowered for word in self._PRODUCT_WORDS):
            return list(hits)
        filtered = [
            hit for hit in hits
            if "docs/hardware" not in str(hit.chunk.get("source") or "")
        ]
        return filtered or list(hits)

'''


def main() -> int:
    text = AGENT.read_text(encoding="utf-8")
    changed = []

    if "about/company" not in text:
        text = text.replace(TOPIC_OLD, TOPIC_NEW, 1)
        changed.append("тематические проходы")

    if "_drop_foreign_platforms" not in text:
        anchor = "    def _search_hits(self, question: str, k: int) -> List[SearchHit]:"
        text = text.replace(anchor, GUARD_METHOD + anchor, 1)
        text = text.replace(GUARD_OLD, GUARD_NEW, 1)
        changed.append("фильтр чужих платформ")

    AGENT.write_text(text, encoding="utf-8")
    print("агент:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
