"""Блок 4 и 5: синонимы продуктов, переранжирование по началу фрагмента,
ограничение контекста одним фрагментом на заголовок.
"""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("partner/agent.py")
ALIASES = '''# Как пользователи называют продукты: запрос расширяем каноническим именем.
_ALIASES = {
    "мэ": "NGFW",
    "межсетевой экран": "NGFW",
    "веб-экран": "WAF",
    "веб экран": "WAF",
    "файрвол": "NGFW",
    "фаервол": "NGFW",
    "тг": "Telegram",
    "телеграм": "Telegram",
    "телега": "Telegram",
    "вк": "VK",
    "вконтакте": "VK",
    "хабр": "Habr",
    "коллектор": "log-collector",
}

'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if "_ALIASES" not in text:
        text = text.replace("# Новости и телеграм полезны", ALIASES + "# Новости и телеграм полезны")
        changed.append("синонимы")

    old_probe = '''        for part in re.split(r"\\s+и\\s+|,\\s*|\\s+или\\s+", question):
            clean = " ".join(word for word in query_terms(part) if len(word) >= 3)
            if clean and clean not in probes:
                probes.append(clean)
        return probes[:4]'''
    new_probe = '''        for part in re.split(r"\\s+и\\s+|,\\s*|\\s+или\\s+", question):
            clean = " ".join(word for word in query_terms(part) if len(word) >= 3)
            if clean and clean not in probes:
                probes.append(clean)
        # Синонимы: «МЭ», «веб-экран», «тг» ищутся по каноническому названию.
        lowered = (question or "").lower()
        for alias, canonical in _ALIASES.items():
            if alias in lowered and canonical not in probes:
                probes.append(canonical)
        return probes[:5]'''
    if old_probe in text and "Синонимы:" not in text:
        text = text.replace(old_probe, new_probe)
        changed.append("синонимы в подзапросах")

    # переранжирование по началу фрагмента + дедупликация по заголовку в контексте
    old_tail = '''            if self._coverage(question, hits) >= 0.6:
                break
        return hits[: max(k, 6)]'''
    new_tail = '''            if self._coverage(question, hits) >= 0.6:
                break

        # Переранжирование: если термин стоит в начале фрагмента, это чаще
        # заголовок раздела или определение, а не упоминание в перечислении.
        terms = [term for term in query_terms(question) if len(term) >= 4]
        if terms:
            def lead_rank(hit: SearchHit) -> int:
                head = str(hit.chunk.get("text") or "")[:250].lower()
                return -sum(1 for term in terms if term in head)

            hits.sort(key=lead_rank)
        return hits[: max(k, 6)]'''
    if old_tail in text and "lead_rank" not in text:
        text = text.replace(old_tail, new_tail)
        changed.append("переранжирование")

    # не больше одного фрагмента на заголовок в контексте
    old_ctx = '''        for hit in hits:
            text = str(hit.chunk.get("text") or "")
            if not text:
                continue'''
    new_ctx = '''        used_titles: set[str] = set()
        for hit in hits:
            text = str(hit.chunk.get("text") or "")
            if not text:
                continue
            # Один заголовок — один фрагмент: соседние куски той же статьи
            # повторяют друг друга и вытесняют другие источники.
            title_key = str(hit.chunk.get("title") or "").strip().lower()
            if title_key and title_key in used_titles:
                continue
            used_titles.add(title_key)'''
    if old_ctx in text and "used_titles" not in text:
        text = text.replace(old_ctx, new_ctx)
        changed.append("контроль заголовков")

    if not changed:
        print("изменений не требуется")
        return 0

    PATH.write_text(text, encoding="utf-8")
    print("применено:", ", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
