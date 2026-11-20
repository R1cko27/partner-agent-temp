"""Кнопки-продолжения: очистка и восстановление из истории."""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from partner.agent import _clean_followups, _client_text, _followups_from_calls  # noqa: E402


class FollowupTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
