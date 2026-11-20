"""Тесты Partner-Agent: источники, карточки, поиск, агент, API.

Запуск:
    python tests/test_partner.py
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

from partner import compat  # noqa: E402

compat.ensure_workable_tempdir()

from partner.agent import PartnerAgent  # noqa: E402
from partner.config import Settings  # noqa: E402
from partner.domain.agent_profile import build_profile  # noqa: E402
from partner.domain.loaders import build_knowledge  # noqa: E402
from partner.prompts import build_fast_prompt, build_system_prompt, tools_for  # noqa: E402
from partner.domain.retriever import Retriever  # noqa: E402
from partner.engine.bm25 import BM25  # noqa: E402
from partner.engine.chunking import Chunker  # noqa: E402
from partner.engine.tokenize import tokenize  # noqa: E402

COMPANY_FILES = {
    "profile.json": json.dumps(
        {
            "name": "Тест Софт",
            "industry": "Разработка ПО",
            "description": "Облачная платформа для склада.",
            "products": ["Тест WMS"],
            "contacts": {"sales": "sales@test.example"},
        },
        ensure_ascii=False,
    ),
    "about/about.md": "# О компании Тест Софт\n\nОснована в 2020 году, 40 сотрудников.\n",
    "products/test-wms.md": (
        "# Тест WMS\n\nСистема управления складом.\n\n"
        "## Тарифы\n\n| Тариф | Цена |\n|---|---|\n| Старт | 10 000 ₽ |\n| Про | 30 000 ₽ |\n"
    ),
    "team/anna.md": "# Анна Смирнова\n\nДолжность: Директор по продажам\n\nОтвечает за крупных клиентов.\n",
    "faq/faq.md": (
        "# FAQ\n\nQ: Сколько стоит Тест WMS?\nA: Тариф «Старт» — 10 000 ₽ в месяц.\n\n"
        "Q: Есть ли интеграция с 1С?\nA: Да, есть готовая интеграция с 1С.\n"
    ),
    "news/2026-04-01-release.md": "# Релиз 2.0\n\n2026-04-01\n\nДобавили прогноз загрузки склада.\n",
}


def make_fixture(root: Path) -> Path:
    """Создаёт материалы и возвращает каталог данных (внутри него company/)."""
    company = root / "data" / "company"
    for relative, content in COMPANY_FILES.items():
        path = company / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root / "data"


def build_index(data_dir: Path, storage_dir: Path) -> None:
    knowledge = build_knowledge(data_dir, fetch_web=False)
    chunker = Chunker(chunk_size=900, chunk_overlap=120)
    chunks = chunker.split_documents(knowledge.documents)
    bm25 = BM25().fit([tokenize(chunk.text, unique=False) for chunk in chunks])
    index_dir = storage_dir / "index"
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / "chunks.json").write_text(
        json.dumps([chunk.to_dict() for chunk in chunks], ensure_ascii=False), encoding="utf-8"
    )
    (index_dir / "bm25.json").write_text(
        json.dumps(bm25.to_dict(), ensure_ascii=False), encoding="utf-8"
    )
    (index_dir / "entities.json").write_text(
        json.dumps(knowledge.entities.as_dict(), ensure_ascii=False), encoding="utf-8"
    )
    (index_dir / "meta.json").write_text(
        json.dumps({"built_at": "2026-01-01T00:00:00", "embedding": "test", "vectors": len(chunks)}),
        encoding="utf-8",
    )


class TestSources(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="partner-"))
        self.data = make_fixture(self.tmp)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_knowledge_builds_cards(self):
        knowledge = build_knowledge(self.data, fetch_web=False)
        kinds = {document.kind for document in knowledge.documents}
        self.assertIn("company", kinds)
        self.assertIn("product", kinds)
        self.assertIn("person", kinds)
        self.assertIn("faq", kinds)
        self.assertIn("news", kinds)

        entities = knowledge.entities
        self.assertEqual(entities.company["name"], "Тест Софт")
        self.assertEqual(len(entities.products), 1)
        self.assertEqual(len(entities.people), 1)
        self.assertEqual(len(entities.faq), 2)
        self.assertEqual(len(entities.news), 1)

    def test_faq_pairs_are_split(self):
        knowledge = build_knowledge(self.data, fetch_web=False)
        questions = [item["question"] for item in knowledge.entities.faq]
        self.assertTrue(any("Сколько стоит" in question for question in questions))
        self.assertTrue(any("1С" in question for question in questions))

    def test_person_role_extracted(self):
        knowledge = build_knowledge(self.data, fetch_web=False)
        person = next(iter(knowledge.entities.people.values()))
        self.assertEqual(person["name"], "Анна Смирнова")
        self.assertIn("продаж", person["role"].lower())

    def test_person_contacts_extracted(self):
        company = self.data / "company"
        (company / "team" / "anna.md").write_text(
            "# Анна Смирнова\n\nДолжность: Директор по продажам\n\n"
            "Отвечает за крупных клиентов.\n\n- Почта: anna@test.example\n"
            "- Телефон: +7 383 111-22-33\n",
            encoding="utf-8",
        )
        knowledge = build_knowledge(self.data, fetch_web=False)
        person = next(iter(knowledge.entities.people.values()))
        contacts = person.get("contacts") or ""
        self.assertIn("anna@test.example", contacts)
        self.assertIn("+7 383 111-22-33", contacts)

    def test_news_date_extracted(self):
        knowledge = build_knowledge(self.data, fetch_web=False)
        self.assertEqual(knowledge.entities.news[0]["date"], "2026-04-01")

    def test_overview_is_first(self):
        knowledge = build_knowledge(self.data, fetch_web=False)
        self.assertEqual(knowledge.documents[0].kind, "overview")
        self.assertIn("Тест Софт", knowledge.documents[0].text)

    def test_missing_folder_raises(self):
        with self.assertRaises(FileNotFoundError):
            build_knowledge(self.tmp / "nope", fetch_web=False)


class TestRetriever(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="partner-ret-"))
        data = make_fixture(cls.tmp)
        storage = cls.tmp / "storage"
        build_index(data, storage)
        cls.retriever = Retriever.load(storage / "index", embedder=None, chroma_dir=None)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_search_finds_product(self):
        hits = self.retriever.search("сколько стоит Тест WMS", k=3)
        self.assertTrue(hits)
        titles = " ".join(str(hit.chunk.get("title")) for hit in hits)
        self.assertIn("Тест WMS", titles)

    def test_find_product(self):
        records = self.retriever.find_product("тест wms")
        self.assertTrue(records)
        self.assertEqual(records[0]["name"], "Тест WMS")

    def test_find_person(self):
        records = self.retriever.find_person("Анна")
        self.assertTrue(records)
        self.assertEqual(records[0]["name"], "Анна Смирнова")

    def test_find_faq(self):
        records = self.retriever.find_faq("интеграция с 1С")
        self.assertTrue(records)
        self.assertIn("1С", records[0]["question"] + records[0]["answer"])

    def test_stats(self):
        stats = self.retriever.stats()
        self.assertEqual(stats["company"], "Тест Софт")
        self.assertGreater(stats["chunks"], 0)
        self.assertEqual(stats["products"], 1)


class FakeClient:
    """Один вызов модели: проверяем, что промпт содержит контекст компании."""

    thinking_supported = True

    def __init__(self) -> None:
        self.calls = 0
        self.last_messages: list = []
        self.last_kwargs: dict = {}

    def stream_chat(self, messages, tools=None, **kwargs):
        from partner.engine.llm import StreamEvent

        self.calls += 1
        self.last_messages = messages
        self.last_kwargs = kwargs
        yield StreamEvent(type="delta", text="Тариф «Старт» — 10 000 ₽ (faq/faq.md).")
        yield StreamEvent(
            type="done",
            finish_reason="stop",
            usage={"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120},
        )


class TestAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="partner-agent-"))
        data = make_fixture(cls.tmp)
        storage = cls.tmp / "storage"
        build_index(data, storage)
        cls.retriever = Retriever.load(storage / "index", embedder=None, chroma_dir=None)

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def _agent(self, client=None, auto_context=True):
        settings = Settings(
            api_key="test",
            auto_context=auto_context,
            answer_cache=False,
            use_dense=False,
            company_name="Тест Софт",
        )
        return PartnerAgent(self.retriever, settings, client=client)

    def test_offline_mode_returns_sources(self):
        agent = self._agent(client=None)
        events = list(agent.run("Сколько стоит Тест WMS?"))
        done = events[-1]
        self.assertEqual(done["type"], "done")
        self.assertTrue(done["text"])
        self.assertTrue(done["sources"])

    def test_fast_mode_single_call_with_context(self):
        client = FakeClient()
        agent = self._agent(client=client)
        events = list(agent.run("Сколько стоит Тест WMS?", mode="fast"))
        done = events[-1]
        self.assertEqual(client.calls, 1)
        self.assertFalse(client.last_kwargs.get("allow_thinking", True))
        prompt = client.last_messages[0]["content"]
        self.assertIn("Тест Софт", prompt)
        self.assertIn("Тест WMS", prompt)
        self.assertIn("10 000", prompt)
        self.assertEqual(done["text"], "Тариф «Старт» — 10 000 ₽ (faq/faq.md).")

    def test_auto_context_can_be_disabled(self):
        client = FakeClient()
        agent = self._agent(client=client, auto_context=False)
        list(agent.run("Сколько стоит Тест WMS?", mode="fast"))
        self.assertNotIn("уже загружено из базы", client.last_messages[0]["content"])

    def test_modes_are_reported(self):
        agent = self._agent(client=FakeClient())
        events = list(agent.run("Вопрос", mode="fast"))
        start = next(event for event in events if event["type"] == "start")
        self.assertEqual(start["answer_mode"], "fast")


class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="partner-api-"))
        data = make_fixture(cls.tmp)
        storage = cls.tmp / "storage"
        build_index(data, storage)
        cls.settings = Settings(
            api_key="",
            data_dir=data,
            storage_dir=storage,
            use_dense=False,
            answer_cache=False,
            company_name="Тест Софт",
        )
        from fastapi.testclient import TestClient

        from partner.api import create_app

        cls.client = TestClient(create_app(cls.settings))
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.client.__exit__(None, None, None)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["company"], "Тест Софт")
        self.assertGreater(payload["chunks"], 0)

    def test_agent_profile_endpoint(self):
        response = self.client.get("/api/agent/profile")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["company"], "Тест Софт")
        self.assertIn("branding", payload)

    def test_retrieve(self):
        response = self.client.post("/api/retrieve", json={"query": "Тест WMS", "top_k": 3})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["hits"])
        self.assertTrue(payload["products"])

    def test_chat_offline_stream(self):
        response = self.client.post(
            "/api/chat",
            json={"message": "Сколько стоит Тест WMS?", "show_notes": False},
        )
        self.assertEqual(response.status_code, 200)
        body = response.text
        self.assertIn('"type": "done"', body)
        self.assertIn("session", body)

    def test_session_history(self):
        response = self.client.post(
            "/api/chat", json={"message": "Кто отвечает за продажи?", "show_notes": False}
        )
        session_id = response.headers.get("X-Session-Id")
        self.assertTrue(session_id)
        detail = self.client.get(f"/api/sessions/{session_id}")
        self.assertEqual(detail.status_code, 200)
        messages = detail.json()["messages"]
        self.assertEqual(len(messages), 2)

    def test_empty_message_rejected(self):
        self.assertEqual(self.client.post("/api/chat", json={"message": ""}).status_code, 422)


if __name__ == "__main__":
    unittest.main(verbosity=2)
