"""Тесты генерации и кеша вопросов к странице.

Запуск:
    python tests/test_page_questions.py
"""

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

from partner.page_questions import (  # noqa: E402
    PageQuestionService,
    PageQuestionStore,
    fallback_questions,
    format_chat_context,
    normalize_url,
    parse_questions,
    prepare_page,
)


class PageQuestionHelpersTest(unittest.TestCase):
    def test_normalize_url_is_shared_across_hosts(self) -> None:
        self.assertEqual(
            normalize_url("https://docs.usergate.com/x.html?utm_source=tg&v=1#toc"),
            "/x.html",
        )
        self.assertEqual(
            normalize_url("https://other-tunnel.trycloudflare.com/x.html"),
            "/x.html",
        )
        self.assertEqual(normalize_url("x.html"), "/x.html")
        self.assertEqual(
            normalize_url("https://host.example/page3.html"),
            "/docs.html",
        )
        self.assertEqual(normalize_url(""), "")

    def test_prepare_page_deduplicates_headings(self) -> None:
        page = prepare_page(
            url="https://example.com/article",
            title="  Статья  ",
            headings=["Раздел", "Раздел", "  Ещё раздел  "],
            text="  Первый   абзац.\n\nВторой абзац.  ",
        )
        self.assertEqual(page["title"], "Статья")
        self.assertEqual(page["headings"], ["Раздел", "Ещё раздел"])
        self.assertEqual(page["text"], "Первый абзац. Второй абзац.")
        self.assertTrue(page["fingerprint"])

    def test_parse_questions_from_json_and_lines(self) -> None:
        raw = '```json\n{"questions": ["1. Первый вопрос?", "Второй вопрос?", "Третий вопрос?"]}\n```'
        self.assertEqual(
            parse_questions(raw),
            ["Первый вопрос?", "Второй вопрос?", "Третий вопрос?"],
        )
        self.assertEqual(
            parse_questions("1. Первый вопрос?\n2. Второй вопрос?\n3. Третий вопрос?"),
            ["Первый вопрос?", "Второй вопрос?", "Третий вопрос?"],
        )

    def test_fallback_uses_page_headings(self) -> None:
        page = prepare_page(
            url="https://example.com/update",
            title="Политика обновления",
            headings=[
                "Таблица совместимости версий",
                "Варианты обновления",
                "Общие рекомендации",
                "Обновление до версии 7.5.1",
            ],
            text="",
        )
        questions = fallback_questions(page)
        self.assertGreaterEqual(len(questions), 3)
        self.assertTrue(any("совместим" in item.lower() for item in questions))
        self.assertTrue(any("обновлен" in item.lower() for item in questions))

    def test_format_chat_context(self) -> None:
        note = format_chat_context(
            url="https://example.com/update",
            title="Политика обновления",
        )
        self.assertEqual(note, "Страница: Политика обновления")
        # Содержимое страницы не дублируется в промпте, URL тоже не нужен.
        self.assertNotIn("https://example.com/update", note)
        self.assertNotIn("Фрагмент страницы", note)
        self.assertLessEqual(len(note), 400)
        self.assertEqual(format_chat_context(url="", title=""), "")


class PageQuestionStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        base = ROOT / "storage"
        base.mkdir(parents=True, exist_ok=True)
        self.tmp = Path(tempfile.mkdtemp(prefix="pageq-", dir=str(base)))
        self.store = PageQuestionStore(self.tmp / "questions.db", ttl_days=30)

    def tearDown(self) -> None:
        self.store.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_roundtrip_and_fingerprint(self) -> None:
        questions = ["Первый?", "Второй?", "Третий?"]
        self.store.put(
            url="https://example.com/a",
            title="Страница",
            fingerprint="abc",
            questions=questions,
            model="test",
        )
        found = self.store.get("https://example.com/a", "abc")
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found["questions"], questions)
        self.assertIsNone(self.store.get("https://example.com/a", "other"))
        self.store.clear()
        self.assertEqual(self.store.stats()["entries"], 0)


class FakeClient:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.calls = 0

    def complete(self, *args, **kwargs):
        self.calls += 1
        return {"choices": [{"message": {"content": self.payload}}]}


class PageQuestionServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        base = ROOT / "storage"
        base.mkdir(parents=True, exist_ok=True)
        self.tmp = Path(tempfile.mkdtemp(prefix="pageq-svc-", dir=str(base)))
        self.service = PageQuestionService(self.tmp / "questions.db")

    def tearDown(self) -> None:
        self.service.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_model_result_is_cached(self) -> None:
        client = FakeClient(
            json.dumps(
                {
                    "questions": [
                        "С каких версий можно обновиться?",
                        "Что сделать перед обновлением?",
                        "Какие есть способы обновления?",
                    ]
                },
                ensure_ascii=False,
            )
        )
        first = self.service.suggest(
            url="https://example.com/update",
            title="Обновление",
            headings=["Совместимость версий"],
            text="Обновление до 7.5.1 возможно с 7.4.3.",
            client=client,
            model="fake",
        )
        self.assertFalse(first["cached"])
        self.assertEqual(first["source"], "model")
        self.assertEqual(len(first["questions"]), 3)
        self.assertEqual(client.calls, 1)

        second = self.service.suggest(
            url="https://example.com/update",
            title="Обновление",
            headings=["Совместимость версий"],
            text="Обновление до 7.5.1 возможно с 7.4.3.",
            client=client,
            model="fake",
        )
        self.assertTrue(second["cached"])
        self.assertEqual(second["source"], "cache")
        self.assertEqual(client.calls, 1)

    def test_cache_shared_across_hosts_and_text_variations(self) -> None:
        client = FakeClient(
            json.dumps(
                {
                    "questions": [
                        "С каких версий можно обновиться?",
                        "Что сделать перед обновлением?",
                        "Какие есть способы обновления?",
                    ]
                },
                ensure_ascii=False,
            )
        )
        first = self.service.suggest(
            url="https://first-tunnel.trycloudflare.com/docs.html",
            title="Политика обновления",
            headings=["Варианты обновления"],
            text="Текст страницы, извлечённый в desktop-браузере.",
            client=client,
            model="fake",
        )
        self.assertFalse(first["cached"])
        self.assertEqual(client.calls, 1)

        # Другой хост туннеля и чуть другой извлечённый текст (например,
        # мобильная вёрстка) — это всё та же страница, вопросы общие.
        second = self.service.suggest(
            url="http://127.0.0.1:8020/docs.html",
            title="Политика обновления",
            headings=["Варианты обновления"],
            text="Текст страницы, извлечённый в мобильном браузере.",
            client=client,
            model="fake",
        )
        self.assertTrue(second["cached"])
        self.assertEqual(second["source"], "cache")
        self.assertEqual(client.calls, 1)

    def test_fallback_without_client(self) -> None:
        result = self.service.suggest(
            url="https://example.com/update",
            title="Обновление",
            headings=["Совместимость версий", "Общие рекомендации"],
            text="",
            client=None,
        )
        self.assertFalse(result["cached"])
        self.assertEqual(result["source"], "fallback")
        self.assertGreaterEqual(len(result["questions"]), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
