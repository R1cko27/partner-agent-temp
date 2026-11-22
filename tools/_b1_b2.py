"""B1: запрет достраивать коды и цены. B2: проходы поиска под параметры."""

from __future__ import annotations

import io
import json
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")
PROFILE = pathlib.Path("data/company/agent.json")

RULE = (
    "Код программы, цену, номер сертификата и телефон называй только дословно из контекста. "
    "Если их там нет — не называй и не достраивай: лучше сказать, что точное значение "
    "подтверждает официальный канал."
)

TOPIC_OLD = '    (("основан", "год", "истори", "2006"), ("about/history",)),'
TOPIC_NEW = TOPIC_OLD + """
    (("node-sync", "delivery-mode", "vrid", "кластер"), ("products/dcfw",)),
    (("экзамен", "курс", "академи", "ug.", "стоимость обучения"),
     ("about/usergate_academy_prices", "about/academy", "faq/education")),
    (("адрес", "телефон", "офис", "контакт"), ("about/contacts", "faq/contacts")),"""

CONSTS = '''CODE_GUARD_RE = re.compile(r"\\bUG\\.[A-Za-z0-9._]{2,}")
PRICE_GUARD_RE = re.compile(r"\\b\\d[\\d\\s]{2,}\\s?₽")


'''

FILTER = '''        # Коды программ и цены, которых нет в источниках, — выдумка модели.
        if self._source_texts:
            body = " ".join(self._source_texts.values()).lower()
            invented_values: List[str] = []

            def _guard(pattern: re.Pattern):
                def repl(match: re.Match) -> str:
                    value = match.group(0)
                    if value.lower() in body:
                        return value
                    invented_values.append(value)
                    return ""

                return repl

            text = CODE_GUARD_RE.sub(_guard(CODE_GUARD_RE), text)
            text = PRICE_GUARD_RE.sub(_guard(PRICE_GUARD_RE), text)
            if invented_values:
                text = re.sub(r"\\s{2,}", " ", text)
                text = re.sub(r"\\s+([.,;:])", r"\\1", text)
                write_log(f"  ! убраны неподтверждённые коды и цены: {len(invented_values)}")

'''


def patch_rules() -> None:
    data = json.loads(PROFILE.read_text(encoding="utf-8-sig"))
    rules = data.get("rules") or []
    if RULE in rules:
        print("правила: уже есть")
        return
    rules.append(RULE)
    data["rules"] = rules
    PROFILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("правила: добавлен запрет достраивать коды и цены")


def patch_agent() -> None:
    text = AGENT.read_text(encoding="utf-8")
    changed = []

    if "about/usergate_academy_prices" not in text:
        text = text.replace(TOPIC_OLD, TOPIC_NEW, 1)
        changed.append("тематические проходы")

    if "CODE_GUARD_RE" not in text:
        anchor = "ANSWER_URL_RE = "
        index = text.find(anchor)
        if index < 0:
            print("не найден ANSWER_URL_RE")
            return
        text = text[:index] + CONSTS + text[index:]
        changed.append("регулярки")

    if "invented_values" not in text:
        anchor = "        return _normalize_tables(text).strip()"
        if anchor in text:
            text = text.replace(anchor, FILTER + anchor, 1)
            changed.append("фильтр кодов и цен")
        else:
            print("не найден возврат _verified_answer")

    AGENT.write_text(text, encoding="utf-8")
    print("агент:", ", ".join(changed) or "без изменений")


def main() -> int:
    patch_rules()
    patch_agent()
    return 0


if __name__ == "__main__":
    sys.exit(main())
