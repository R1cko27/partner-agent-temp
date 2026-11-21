"""Кнопки-продолжения: очистка, привязка к вопросу и роль пользователя.

Старые тесты проверяют уборку подписей. Новые — главное свойство: кнопка
должна продолжать именно этот вопрос, а не быть случайным совпадением слов.
"""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from partner.agent import _clean_followups, _client_text, _followups_from_calls  # noqa: E402
from partner.followups import FollowupPlanner, _ensure_question  # noqa: E402


def _doc(source: str, heading: str, product: str = "NGFW", extra: str = "") -> dict:
    """Фрагмент страницы документации с шапкой краулера."""
    text = (
        f"{source.rsplit('/', 1)[-1].replace('.md', '')}\n"
        "---\n"
        f"заголовок: {heading}\n"
        f"продукт: {product}\n"
        "версия: 6.x\n"
        "раздел: Релизы\n"
        + extra
        + "---\n"
        "Текст страницы документации."
    )
    return {
        "id": source,
        "doc_id": source,
        "index": 0,
        "kind": "doc",
        "title": source.rsplit("/", 1)[-1].replace(".md", ""),
        "source": source,
        "text": text,
    }


def _chunk(source: str, text: str, kind: str = "doc", title: str = "") -> dict:
    return {
        "id": source,
        "doc_id": source,
        "index": 0,
        "kind": kind,
        "title": title or source.rsplit("/", 1)[-1],
        "source": source,
        "text": text,
    }


class FakeKB:
    """Минимальная база: релизы NGFW, карточка изменений и несколько FAQ."""

    def __init__(self) -> None:
        self.chunks = [
            _doc("docs/ngfw/usergate-6-1-0.md", "UserGate 6.1.0 (сборка 6.1.0.10409R 9/04/2021)."),
            _doc("docs/ngfw/usergate-6-1-1.md", "UserGate 6.1.1 (сборка 6.1.1.10462R 26/04/2021)."),
            _doc("docs/ngfw/usergate-6-1-2.md", "UserGate 6.1.2 (сборка 6.1.2.10523R, 19/05/2021)."),
            _doc("docs/ngfw/usergate-6-1-3.md", "UserGate 6.1.3 (сборка 6.1.3.10787R, 19/08/2021)."),
            _doc(
                "docs/ngfw/izmeneniya-ngfw-6.md",
                "Изменения в UserGate NGFW 6",
                extra="",
            ),
            _doc(
                "docs/mc/usergate-mc-6-1-2.md",
                "UserGate Management Center 6.1.2 (build 6.1.2.10523R, 19/05/2021)",
                product="Management Center",
            ),
        ]
        self.faq = [
            {
                "question": "Сколько стоит UserGate NGFW?",
                "answer": "Цены в материалах нет. Точные условия — sales@usergate.com.",
                "source": "faq/pricing.md",
            },
            {
                "question": "Сколько стоит UserGate DCFW?",
                "answer": "Данных о цене в материалах нет — sales@usergate.com.",
                "source": "faq/pricing.md",
            },
            {
                "question": "Куда написать по вопросам покупки и лицензий?",
                "answer": "Клиентские вопросы — sales@usergate.com.",
                "source": "faq/pricing.md",
            },
            {
                "question": "Куда обратиться по поводу партнёрства?",
                "answer": "Партнёрские вопросы ведёт отдел продаж: sales@usergate.com.",
                "source": "faq/contacts.md",
            },
            {
                "question": "Какой сертификат у UserGate NGFW?",
                "answer": "Сертификат ФСТЭК России № 3905.",
                "source": "faq/certification.md",
            },
            {
                "question": "Все продукты UserGate сертифицированы ФСТЭК?",
                "answer": "Так утверждать нельзя: сертификат подтверждён для NGFW.",
                "source": "faq/certification.md",
            },
            {
                "question": "Какой у UserGate телефон?",
                "answer": "8 495 150 97 48, будни с 9:00 до 18:00.",
                "source": "faq/contacts.md",
            },
            {
                "question": "Есть ли у UserGate офис в Новосибирске?",
                "answer": "Да, штаб-квартира — ул. Николаева, д. 11.",
                "source": "faq/contacts.md",
            },
            {
                "question": "Как связаться с UserGate?",
                "answer": "Телефон 8 495 150 97 48 или sales@usergate.com.",
                "source": "faq/contacts.md",
            },
        ]
        self.terms = [
            {
                "term": "SUMMA",
                "definition": "Экосистема решений UserGate, объединённых общей платформой.",
                "source": "docs/glossary.md",
            },
            {
                "term": "UGOS",
                "definition": "Операционная система UserGate, ядро экосистемы SUMMA.",
                "source": "docs/glossary.md",
            },
        ]

    # --- интерфейс, который использует планировщик ---------------------
    def products(self):
        return [
            {"name": "UserGate NGFW"},
            {"name": "UserGate WAF"},
            {"name": "UserGate Management Center"},
        ]

    def find_term(self, query, limit=2):
        found = [term for term in self.terms if term["term"].lower() in (query or "").lower()]
        return found[:limit]

    def find_faq(self, query, limit=5):
        words = set((query or "").lower().replace("?", " ").split())

        def score(record):
            return len(words & set(record["question"].lower().replace("?", " ").split()))

        ranked = sorted(self.faq, key=score, reverse=True)
        return [record for record in ranked if score(record) > 0][:limit]

    def faq_items(self):
        return list(self.faq)

    def glossary_items(self):
        return list(self.terms)


def _source(path: str, kind: str = "doc", title: str = "") -> dict:
    return {"id": path, "source": path, "kind": kind, "title": title, "url": ""}


class FollowupCleanupTests(unittest.TestCase):
    def test_cleans_and_limits(self):
        items = _clean_followups(
            ["  Сколько стоит?  ", "Сколько стоит", "", "x" * 120, "Пилот", "Интеграции"]
        )
        self.assertEqual(items, ["Сколько стоит?", "Пилот?", "Интеграции?"])

    def test_adds_question_mark(self):
        self.assertEqual(_clean_followups(["Как связаться"]), ["Как связаться?"])

    def test_restores_from_tool_calls(self):
        calls = [
            {"name": "search_knowledge", "arguments": {"query": "цена"}},
            {"name": "offer_followups", "arguments": {"items": ["Пилот?", "Пилот"]}},
        ]
        self.assertEqual(_followups_from_calls(calls), ["Пилот?"])

    def test_client_text_strips_sources(self):
        text = (
            "«Бизнес» — 55 000 ₽ в месяц для парка до 150 машин `faq/faq.md`\n"
            "Поддержка 24/7 (faq/faq.md)\n"
            "Источники: faq/faq.md"
        )
        cleaned = _client_text(text)
        self.assertNotIn(".md", cleaned)
        self.assertNotIn("Источник", cleaned)
        self.assertIn("55 000", cleaned)

    def test_caps_at_eight(self):
        items = _clean_followups([f"Вариант {index}" for index in range(12)])
        self.assertEqual(len(items), 8)

    def test_empty(self):
        self.assertEqual(_clean_followups(None), [])
        self.assertEqual(_followups_from_calls(None), [])

    def test_ensure_question(self):
        self.assertEqual(_ensure_question("  Что нового  "), "Что нового?")
        self.assertEqual(_ensure_question("Уже вопрос?"), "Уже вопрос?")
        self.assertEqual(_ensure_question(""), "")


class PlannerTests(unittest.TestCase):
    def setUp(self):
        self.kb = FakeKB()
        self.planner = FollowupPlanner(self.kb)
        self.build_question = "Расскажи про сборка 6.1.2.10523R, 19/05/2021"
        self.build_answer = (
            "Релиз от 19 мая 2021 года для трёх продуктов: UserGate (NGFW), "
            "Management Center и Log Analyzer. Предыдущая сборка — 6.1.1, "
            "следующая — 6.1.3."
        )
        self.build_sources = [
            _source("docs/mc/usergate-mc-6-1-2.md"),
            _source("docs/ngfw/usergate-6-1-2.md"),
        ]

    # --- привязка к сборке --------------------------------------------
    def test_build_question_continues_with_neighbour_builds(self):
        items = self.planner.plan(
            self.build_question, self.build_answer, self.build_sources, staff=True
        )
        self.assertIn("Что изменилось в сборке 6.1.3.10787R?", items)
        self.assertIn("Что изменилось в сборке 6.1.1.10462R?", items)
        self.assertIn("Какие изменения были в UserGate NGFW 6?", items)

    def test_build_question_has_no_random_buttons(self):
        items = self.planner.plan(
            self.build_question, self.build_answer, self.build_sources, staff=True
        )
        joined = " ".join(items).lower()
        for noise in ("сколько стоит", "телефон", "офис", "сертификат", "siem"):
            self.assertNotIn(noise, joined)

    def test_client_wording_differs_from_staff(self):
        staff = self.planner.plan(
            self.build_question, self.build_answer, self.build_sources, staff=True
        )
        client = self.planner.plan(
            self.build_question, self.build_answer, self.build_sources, staff=False
        )
        self.assertTrue(any("Что изменилось" in item for item in staff))
        self.assertTrue(any("Что нового" in item for item in client))

    def test_primary_release_is_of_asked_product(self):
        # В источниках первым лежит релиз Management Center, но вопрос про
        # сборку UserGate — продолжение должно быть по линейке NGFW.
        items = self.planner.plan(
            self.build_question, self.build_answer, self.build_sources, staff=True
        )
        self.assertIn("Какие изменения были в UserGate NGFW 6?", items)
        self.assertNotIn("Какие изменения были в UserGate Management Center 6?", items)

    # --- привязка к продукту и теме -----------------------------------
    def test_certification_question_gets_certification_buttons(self):
        items = self.planner.plan(
            "Сертифицирован ли UserGate NGFW по ФСТЭК?",
            "Сертификат ФСТЭК России № 3905 подтверждён для NGFW.",
            [_source("faq/certification.md", kind="faq")],
            staff=True,
        )
        self.assertTrue(items)
        self.assertTrue(all("сертифи" in item.lower() for item in items))

    def test_unrelated_faq_is_not_offered(self):
        items = self.planner.plan(
            "Как настроить кластер из двух ПАК с разной версией ПО?",
            "Кластер настраивается в разделе управления устройствами.",
            [],
            staff=True,
        )
        self.assertNotIn("Сколько стоит UserGate NGFW?", items)
        self.assertNotIn("Какой у UserGate телефон?", items)

    def test_no_anchors_means_no_buttons(self):
        items = self.planner.plan(
            "Расскажи что-нибудь интересное",
            "Короткий ответ без конкретики про материалы.",
            [],
            staff=True,
        )
        self.assertEqual(items, [])

    def test_asked_question_is_never_repeated(self):
        items = self.planner.plan(
            "Чем NGFW отличается от WAF?",
            "NGFW защищает сеть, WAF — веб-приложение.",
            [_source("faq/products.md", kind="faq")],
            staff=True,
        )
        self.assertNotIn("Чем NGFW отличается от WAF?", items)

    def test_at_most_four_unique_buttons(self):
        items = self.planner.plan(
            self.build_question, self.build_answer, self.build_sources, staff=True
        )
        self.assertLessEqual(len(items), 4)
        self.assertEqual(len(items), len(set(items)))

    # --- роль пользователя --------------------------------------------
    def test_staff_does_not_get_sales_buttons(self):
        items = self.planner.plan(
            "Сколько стоит UserGate NGFW?",
            "В материалах цены нет, коммерческие условия подтверждает sales@usergate.com.",
            [_source("faq/pricing.md", kind="faq")],
            staff=True,
        )
        for item in items:
            self.assertNotIn("скидк", item.lower())
            self.assertNotIn("стоит UserGate DCFW", item)

    def test_client_may_get_price_neighbours(self):
        # Клиенту цена соседнего продукта — законное продолжение разговора
        # о стоимости; сотруднику такие кнопки не нужны.
        items = self.planner.plan(
            "Сколько стоит UserGate NGFW?",
            "Цены в материалах базы нет: стоимость зависит от состава лицензии.",
            [_source("faq/pricing.md", kind="faq")],
            staff=False,
        )
        self.assertIn("Сколько стоит UserGate DCFW?", items)

    def test_gap_answer_offers_channel(self):
        items = self.planner.plan(
            "Сколько стоит UserGate NGFW?",
            "В материалах базы цены нет. Точные условия подтверждает sales@usergate.com.",
            [_source("faq/pricing.md", kind="faq")],
            staff=True,
        )
        self.assertTrue(any("sales" in item.lower() or "лицензи" in item.lower() for item in items))

    # --- проверка кнопок модели ---------------------------------------
    def test_review_keeps_context_buttons(self):
        items = self.planner.review(
            ["Что изменилось в сборке 6.1.3.10787R?"],
            self.build_question,
            self.build_answer,
            self.build_sources,
            staff=True,
        )
        self.assertEqual(items, ["Что изменилось в сборке 6.1.3.10787R?"])

    def test_review_drops_random_and_sales_buttons(self):
        items = self.planner.review(
            [
                "Сколько стоит UserGate NGFW?",
                "Какой у UserGate телефон?",
                "Какие продукты входят в SUMMA?",
                "Что изменилось в 6.1.3?",
            ],
            self.build_question,
            self.build_answer,
            self.build_sources,
            staff=True,
        )
        self.assertEqual(items, ["Что изменилось в 6.1.3?"])

    def test_review_returns_empty_for_offtopic(self):
        items = self.planner.review(
            ["Сколько стоит UserGate NGFW?", "Какой у UserGate телефон?"],
            self.build_question,
            self.build_answer,
            self.build_sources,
            staff=False,
        )
        self.assertEqual(items, [])

    # --- прочее --------------------------------------------------------
    def test_english_templates(self):
        items = self.planner.plan(
            "What changed in build 6.1.2.10523R?",
            "Release of 19 May 2021. Next build is 6.1.3.",
            self.build_sources,
            staff=True,
            lang="latin",
        )
        self.assertTrue(items)
        self.assertTrue(all(item.isascii() for item in items))

    def test_unknown_language_returns_nothing(self):
        items = self.planner.plan(
            self.build_question, self.build_answer, self.build_sources, staff=True, lang="zh"
        )
        self.assertEqual(items, [])

    def test_keep_is_preserved_and_not_duplicated(self):
        items = self.planner.plan(
            self.build_question,
            self.build_answer,
            self.build_sources,
            staff=True,
            keep=["Что изменилось в сборке 6.1.3.10787R?"],
        )
        self.assertEqual(items[0], "Что изменилось в сборке 6.1.3.10787R?")
        self.assertEqual(len(items), len(set(items)))
        self.assertLessEqual(len(items), 4)


if __name__ == "__main__":
    unittest.main()
