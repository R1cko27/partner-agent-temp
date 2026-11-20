"""Уточняющие вопросы: очистка вопроса и вариантов."""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from partner.agent import _clean_clarification  # noqa: E402


class ClarificationTests(unittest.TestCase):
    def test_builds_three_options_and_custom(self):
        clar = _clean_clarification(
            {
                "question": "  Какой у вас парк машин? ",
                "options": ["До 30", "31–150", "Больше 150", "лишний"],
                "placeholder": "Например, 45",
            }
        )
        self.assertIsNotNone(clar)
        self.assertEqual(clar["question"], "Какой у вас парк машин?")
        self.assertEqual(len(clar["options"]), 3)
        self.assertTrue(clar["allow_custom"])
        self.assertEqual(clar["placeholder"], "Например, 45")

    def test_builds_multiple_questions(self):
        clar = _clean_clarification(
            {
                "intro": "Пара вопросов для подбора",
                "questions": [
                    {"question": "Цель?", "options": ["Работа", "Рост"]},
                    {"question": "Уровень?", "options": ["С нуля", "Есть опыт"]},
                ],
            }
        )
        self.assertEqual(len(clar["questions"]), 2)
        self.assertEqual(clar["question"], "Цель?")
        self.assertIn("Пара вопросов", clar["summary"])

    def test_caps_at_ten_questions(self):
        clar = _clean_clarification(
            {
                "questions": [
                    {"question": f"Вопрос {index}?", "options": ["A", "B"]}
                    for index in range(12)
                ]
            }
        )
        self.assertEqual(len(clar["questions"]), 10)

    def test_rejects_too_few_options(self):
        self.assertIsNone(_clean_clarification({"question": "Что?", "options": ["Один"]}))

    def test_rejects_empty_question(self):
        self.assertIsNone(_clean_clarification({"question": " ", "options": ["A", "B"]}))

    def test_default_placeholder(self):
        clar = _clean_clarification({"question": "Что?", "options": ["A", "B"]})
        self.assertEqual(clar["placeholder"], "Свой вариант")


if __name__ == "__main__":
    unittest.main()
