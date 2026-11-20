"""Автовыбор режима по сложности вопроса."""

import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from partner.engine.complexity import heuristic_mode, parse_mode  # noqa: E402


class ModeTests(unittest.TestCase):
    def test_greeting_is_fast(self):
        self.assertEqual(heuristic_mode("Привет!")[0], "fast")

    def test_comparison_is_thinking(self):
        mode, reason = heuristic_mode("Сравни тарифы Бизнес и Старт по цене")
        self.assertEqual(mode, "thinking")
        self.assertTrue(reason)

    def test_short_fact_is_fast(self):
        self.assertEqual(heuristic_mode("Сколько стоит Вектор TMS?")[0], "fast")

    def test_long_question_is_thinking(self):
        question = " ".join(["Расскажи подробно"] + ["условие"] * 25)
        self.assertEqual(heuristic_mode(question)[0], "thinking")

    def test_parse_clarify(self):
        self.assertEqual(parse_mode("CLARIFY"), "clarify")
        self.assertEqual(parse_mode("уточнение"), "clarify")

    def test_parse_classifier(self):
        self.assertEqual(parse_mode("FAST"), "fast")
        self.assertEqual(parse_mode(" thinking\n"), "thinking")
        self.assertIsNone(parse_mode("не понял"))


if __name__ == "__main__":
    unittest.main()
