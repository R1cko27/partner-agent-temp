"""Профиль компании: поведение задаётся конфигом, а не кодом."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from partner import compat  # noqa: E402

compat.ensure_workable_tempdir()

from partner.domain.agent_profile import build_profile  # noqa: E402
from partner.prompts import build_fast_prompt, build_system_prompt, tools_for  # noqa: E402

CONFIG = {
    "company": "Ромашка",
    "persona": {
        "role": "Ты — ассистент «{company}», отвечаешь на вопросы о цветах.",
        "audience": "покупатели",
        "tone": "тёплый и короткий",
    },
    "style": {"heading": False, "max_bullets": 3, "allow_tables": False, "observations": 0},
    "citations": {"required": True, "style": "section", "section_title": "Откуда данные"},
    "rules": ["Не называй цены без источника."],
    "topics": {"focus": ["букеты"], "avoid": ["доставка в другие страны"]},
    "fallback": "Этого нет в материалах «Ромашки».",
    "cta": {"text": "Напишите нам:", "contact": "hi@romashka.example"},
    "glossary": {"микс": "готовый букет из разных цветов"},
    "retrieval": {"top_k": 4, "context_hits": 2, "excerpt_chars": 300},
    "limits": {"max_tokens": 1200, "fast_max_tokens": 400, "max_steps": 3},
    "tools": ["search_knowledge", "find_product"],
    "branding": {
        "title": "Ассистент Ромашка",
        "brand": "romashka",
        "avatar": "R",
        "heading": "Что подсказать?",
        "subtitle": "Спросите про букеты.",
        "placeholder": "Ваш вопрос…",
        "examples": ["Какие есть букеты?"],
    },
}


class TestAgentProfile(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="profile-"))
        self.data = self.tmp / "data"
        (self.data / "company").mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write(self, payload: dict) -> None:
        (self.data / "company" / "agent.json").write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8"
        )

    def test_defaults_without_config(self):
        profile = build_profile(self.data, company_name="Без конфига")
        self.assertEqual(profile.company_name, "Без конфига")
        self.assertIn("Без конфига", profile.persona.role)
        self.assertTrue(profile.citations.required)
        self.assertEqual(profile.language, "auto")
        self.assertIn("search_knowledge", profile.tools)
        self.assertTrue(profile.fallback)

    def test_config_overrides_everything(self):
        self._write(CONFIG)
        profile = build_profile(self.data)
        self.assertEqual(profile.company_name, "Ромашка")
        self.assertIn("Ромашка", profile.persona.role)
        self.assertNotIn("{company}", profile.persona.role)
        self.assertEqual(profile.style.max_bullets, 3)
        self.assertFalse(profile.style.heading)
        self.assertEqual(profile.citations.style, "section")
        self.assertEqual(profile.citations.section_title, "Откуда данные")
        self.assertEqual(profile.fallback, "Этого нет в материалах «Ромашки».")
        self.assertEqual(profile.retrieval.context_hits, 2)
        self.assertEqual(profile.limits.max_steps, 3)
        self.assertEqual(profile.tools, ["search_knowledge", "find_product"])

    def test_tools_are_filtered(self):
        self._write(CONFIG)
        profile = build_profile(self.data)
        names = [tool["function"]["name"] for tool in tools_for(profile)]
        self.assertEqual(sorted(names), ["find_product", "search_knowledge"])

    def test_prompt_uses_company_config_not_hardcode(self):
        self._write(CONFIG)
        profile = build_profile(self.data)
        prompt = build_system_prompt({"chunks": 12}, profile, lang="ru")
        self.assertIn("Ромашка", prompt)
        self.assertIn("Не называй цены без источника", prompt)
        self.assertIn("Откуда данные", prompt)
        self.assertIn("микс", prompt)
        self.assertIn("hi@romashka.example", prompt)
        self.assertIn("букеты", prompt)
        self.assertIn("доставка в другие страны", prompt)
        # код не должен протаскивать чужую компанию
        self.assertNotIn("Вектор", prompt)

    def test_fast_prompt_uses_style_and_fallback(self):
        self._write(CONFIG)
        profile = build_profile(self.data)
        prompt = build_fast_prompt("Пара фактов", profile, lang="ru")
        self.assertIn("Этого нет в материалах «Ромашки»", prompt)
        self.assertIn("Пара фактов", prompt)

    def test_profile_merges_into_profile_json(self):
        (self.data / "company" / "profile.json").write_text(
            json.dumps(
                {"name": "Ромашка", "agent": {"style": {"max_bullets": 2}}},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        profile = build_profile(self.data)
        self.assertEqual(profile.company_name, "Ромашка")
        self.assertEqual(profile.style.max_bullets, 2)
        self.assertEqual(profile.style.max_sentences, 4)  # умолчание сохранилось


if __name__ == "__main__":
    unittest.main(verbosity=2)
