"""Блок 4+: проход по карточкам-спискам и карточке упомянутого продукта."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("partner/agent.py")

HINTS = '''# Какие карточки отвечают на перечисления: городá, платформы, курсы, продукты.
_LIST_HINTS = (
    (("город", "офис", "адрес"), ("about/contacts",)),
    (("платформ", "аппаратн", "модел"), ("docs/versions-and-platforms",)),
    (("курс", "обучен", "фгос", "академ", "экзамен"), ("faq/education",)),
    (("продукт", "экосистем", "summa", "линейк"), ("faq/products", "about/ecosystem")),
)

'''

METHODS = '''    def _enumeration_hits(self, question: str) -> List[SearchHit]:
        """Для перечислений подтягиваем карточку-список по теме вопроса."""
        if not _is_enumeration(question):
            return []
        lowered = (question or "").lower()
        terms = [term for term in query_terms(question) if len(term) >= 4]
        found: List[SearchHit] = []
        seen: set[str] = set()
        for keywords, sources in _LIST_HINTS:
            if not any(word in lowered for word in keywords):
                continue
            for pattern in sources:
                for hit in self.retriever.chunks_by_source(pattern, limit=3):
                    chunk_id = str(hit.chunk.get("id"))
                    if chunk_id in seen:
                        continue
                    text = str(hit.chunk.get("text") or "").lower()
                    if terms and not any(term in text for term in terms):
                        continue
                    seen.add(chunk_id)
                    found.append(hit)
        return found[:2]

    def _product_card_hits(self, question: str) -> List[SearchHit]:
        """Карточка упомянутого продукта: в ней версии, кластеры и параметры."""
        mentioned = [str(item.get("name") or "") for item in self.retriever.find_product(question, limit=2)]
        if not mentioned:
            return []
        terms = [term for term in query_terms(question) if len(term) >= 4]
        found: List[SearchHit] = []
        seen: set[str] = set()
        for name in mentioned:
            slug = "".join(ch for ch in name.lower() if ch.isalnum() or ch in "-_")
            if not slug:
                continue
            for hit in self.retriever.chunks_by_source(f"products/{slug}", limit=4):
                chunk_id = str(hit.chunk.get("id"))
                if chunk_id in seen:
                    continue
                text = str(hit.chunk.get("text") or "").lower()
                if terms and not any(term in text for term in terms):
                    continue
                seen.add(chunk_id)
                found.append(hit)
        return found[:2]

'''

ANCHOR = "    def _search_hits(self, question: str, k: int) -> List[SearchHit]:"


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []
    if "_LIST_HINTS" not in text:
        text = text.replace("# Новости и телеграм полезны", HINTS + "# Новости и телеграм полезны", 1)
        changed.append("подсказки карточек")
    if "_enumeration_hits" not in text:
        text = text.replace(ANCHOR, METHODS + ANCHOR, 1)
        changed.append("проходы по карточкам")

    old = '''        # Точечная попытка по редкому термину'''
    new = '''        # Карточки-списки и карточка продукта: там таблицы и перечни.
        for extra in (self._enumeration_hits(question), self._product_card_hits(question)):
            if not extra:
                continue
            known_extra = {hit.chunk.get("id") for hit in extra}
            hits = extra + [hit for hit in hits if hit.chunk.get("id") not in known_extra]

        # Точечная попытка по редкому термину'''
    if old in text and "_enumeration_hits(question)" not in text.split(old)[0][-400:]:
        text = text.replace(old, new, 1)
        changed.append("подключение проходов")

    if not changed:
        print("изменений не требуется")
        return 0
    PATH.write_text(text, encoding="utf-8")
    print("применено:", ", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
