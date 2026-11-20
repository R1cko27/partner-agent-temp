"""Агент Partner-Agent: поиск по базе знаний компании и ответ со ссылками."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, Iterator, List, Optional, Sequence

from .domain.retriever import Retriever, SearchHit
from .engine.answers import AnswerCache
from .engine.complexity import MODE_PROMPT, heuristic_mode, parse_mode
from .engine.lang import detect_lang, fallback_text, sanitize_text
from .engine.llm import DeepSeekClient, LLMError, ToolCall
from .engine.logbook import write_log
from .engine.tokenize import clean_text, tokenize
from .config import Settings
from .domain.agent_profile import AgentProfile, build_profile
from .prompts import build_fast_prompt, build_system_prompt, tools_for

MAX_HISTORY_MESSAGES = 12


def _clip(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rsplit(" ", 1)[0] + "…"
    

def _compact(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Убирает пустые поля — экономит токены в ответах инструментов."""
    return {
        key: value
        for key, value in payload.items()
        if value not in (None, "", [], {}, 0)
    }


def _clean_followups(values: Any, limit: int = 8) -> List[str]:
    """Аккуратные кнопки-продолжения: без пустых, дублей и простыней."""
    if isinstance(values, str):
        values = [values]
    items: List[str] = []
    seen = set()
    for value in values or []:
        text = " ".join(str(value).split()).strip(" -—•")
        if not text or len(text) > 90:
            continue
        if text[-1] not in "?？":
            text += "?"
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(text)
    return items[:limit]


def _clean_options(values: Any, limit: int = 3) -> List[str]:
    if isinstance(values, str):
        values = [values]
    items: List[str] = []
    seen = set()
    for value in values or []:
        text = " ".join(str(value).split()).strip(" -—•")
        if not text or len(text) > 80:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(text)
        if len(items) >= limit:
            break
    return items


def _clean_clarification_item(item: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(item, dict):
        return None
    question = " ".join(str(item.get("question") or "").split()).strip()
    options = _clean_options(item.get("options"))
    if not question or len(question) > 220 or len(options) < 2:
        return None
    placeholder = " ".join(str(item.get("placeholder") or "").split()).strip()
    return {
        "question": question,
        "options": options[:3],
        "placeholder": placeholder[:80] or "Свой вариант",
    }


def _clean_clarification(args: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(args, dict):
        return None
    questions: List[Dict[str, Any]] = []
    raw = args.get("questions")
    if isinstance(raw, list):
        for item in raw[:10]:
            cleaned = _clean_clarification_item(item)
            if cleaned:
                questions.append(cleaned)
    # Обратная совместимость со старым форматом одного вопроса.
    if not questions:
        legacy = _clean_clarification_item(args)
        if legacy:
            questions.append(legacy)
    if not questions:
        return None
    intro = " ".join(str(args.get("intro") or "").split()).strip()[:240]
    summary = intro or "Уточнение: " + " · ".join(
        item["question"] for item in questions
    )
    first = questions[0]
    return {
        "questions": questions,
        "intro": intro,
        "summary": summary,
        "allow_custom": True,
        "question": first["question"],
        "options": first["options"],
        "placeholder": first["placeholder"],
    }


def _followups_from_calls(calls: Any) -> List[str]:
    for call in calls or []:
        if not isinstance(call, dict) or call.get("name") != "offer_followups":
            continue
        args = call.get("arguments") or {}
        if isinstance(args, dict):
            return _clean_followups(args.get("items"))
    return []


_SOURCE_FILE_RE = re.compile(r"`[^`\n]+\.(?:md|txt|pdf|docx|html?|json)`", re.I)
_SOURCE_CODE_RE = re.compile(r"\s*`[^`\n]+`")
_SOURCE_PAREN_WORDS_RE = re.compile(
    r"\s*\([^()\n]*(?:FAQ|faq|источник|материал|баз[аеы]|документ|файл|раздел|карточк)"
    r"[^()\n]*\)",
    re.I,
)
_SOURCE_PAREN_CODE_RE = re.compile(r"\s*\([^()\n]*`[^`\n]+`[^()\n]*\)")
_SOURCE_PAREN_RE = re.compile(
    r"\s*\((?:[^()\n]*?\.(?:md|txt|pdf|docx|html?|json))\)", re.I
)
_SOURCE_LINE_RE = re.compile(r"(?im)^\s*Источник(?:и)?\s*:.*(?:\n|$)")


_CLIENT_PHRASES = [
    (re.compile(r"(?i)\bпо материалам компании\b"), "по нашим данным"),
    (re.compile(r"(?i)\bпо материалам\b"), "по нашим данным"),
    (re.compile(r"(?i)\bв материалах\b"), ""),
    (re.compile(r"(?i)\bв документах\b"), ""),
    (re.compile(r"(?i)\bв источниках\b"), ""),
    (re.compile(r"(?i)\bиз материалов\b"), "из наших данных"),
    (re.compile(r"(?i)\bматериалами\b"), ""),
    (re.compile(r"(?i)\bматериалы\b"), ""),
    (re.compile(r"(?i)\bматериалов\b"), ""),
    (re.compile(r"(?i)\bматериале\b"), ""),
    (re.compile(r"(?i)\bматериал\b"), ""),
    (re.compile(r"(?i)\bв материалах компании\b"), "у нас"),
    (re.compile(r"(?i)\bв базе(?: знаний)?\b"), ""),
    (re.compile(r"(?i)\bпо данным базы\b"), "по нашим данным"),
    (re.compile(r"(?i)\bв выгрузке\b"), "в данных"),
    (re.compile(r"(?i)\bиз материалов компании\b"), "из наших данных"),
]


def _strip_source_keys(value: Any) -> Any:
    """Убирает из данных инструмента поля source/sources в клиентском режиме."""
    if isinstance(value, dict):
        drop = {"source", "sources", "source_path", "file"}
        if "text" in value:  # фрагмент поиска: убираем и его заголовок
            drop |= {"title", "kind", "id"}
        return {
            key: _strip_source_keys(item)
            for key, item in value.items()
            if key not in drop
        }
    if isinstance(value, list):
        return [_strip_source_keys(item) for item in value]
    return value


def _client_text(text: str) -> str:
    """Убирает из ответа служебные ссылки на файлы, когда включён клиентский режим."""
    cleaned = text or ""
    for pattern, replacement in _CLIENT_PHRASES:
        cleaned = pattern.sub(replacement, cleaned)
    cleaned = _SOURCE_PAREN_WORDS_RE.sub("", cleaned)
    cleaned = _SOURCE_PAREN_CODE_RE.sub("", cleaned)
    cleaned = _SOURCE_FILE_RE.sub("", cleaned)
    cleaned = _SOURCE_PAREN_RE.sub("", cleaned)
    cleaned = _SOURCE_CODE_RE.sub("", cleaned)
    cleaned = _SOURCE_LINE_RE.sub("", cleaned)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([.,;:!?])", r"\1", cleaned)
    # «… и.» после удаления цитаты
    cleaned = re.sub(r"\s+(?:и|или|а|но)\s*([.,;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"\[\s*\]", "", cleaned)
    cleaned = re.sub(r"\(\s*\)", "", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(
        r"(?m)(^|\n\n)(по нашим данным)",
        lambda match: match.group(1) + "По нашим данным",
        cleaned,
    )
    return cleaned.strip()


def _empty_usage() -> Dict[str, int]:
    return {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}


def _merge_usage(total: Dict[str, int], usage: Optional[Dict[str, Any]]) -> None:
    if not usage:
        return
    total["calls"] += 1
    for key in ("prompt_tokens", "completion_tokens", "total_tokens"):
        try:
            total[key] += int(usage.get(key) or 0)
        except (TypeError, ValueError):
            continue


class PartnerAgent:
    def __init__(
        self,
        retriever: Retriever,
        settings: Settings,
        client: Optional[DeepSeekClient] = None,
        cache: Optional[AnswerCache] = None,
        profile: Optional[AgentProfile] = None,
    ) -> None:
        self.retriever = retriever
        self.settings = settings
        self.client = client
        self.cache = cache
        self.stats = retriever.stats()
        self._mode_cache: dict[str, tuple[str, str, str]] = {}
        self.profile = profile or build_profile(
            settings.data_dir,
            company_name=self.stats.get("company") or settings.company_name,
            limits={
                "max_tokens": settings.max_tokens,
                "fast_max_tokens": settings.fast_max_tokens,
                "local_max_tokens": settings.local_max_tokens,
                "max_steps": settings.max_steps,
            },
        )
        self.company = self.profile.company_name or self.stats.get("company") or "компания"
        self.tools = tools_for(self.profile)

    # --- инструменты ----------------------------------------------------
    def _tool_plan(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        steps = [str(step).strip() for step in (args.get("steps") or []) if str(step).strip()]
        return {
            "result": {"ok": True, "steps": steps},
            "summary": f"план из {len(steps)} шагов" if steps else "план",
            "sources": [],
            "plan": {"steps": steps[:6], "reasoning": str(args.get("reasoning") or "")[:600]},
        }

    def _tool_search_knowledge(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        query = str(args.get("query") or "").strip()
        top_k = max(1, min(int(args.get("top_k") or self.settings.top_k), 10))
        hits = self.retriever.search(query, k=top_k)
        payload = {
            "query": query,
            "chunks": [
                _compact(
                    {
                        "title": hit.chunk.get("title"),
                        "kind": hit.chunk.get("kind"),
                        "source": hit.chunk.get("source"),
                        "text": _clip(str(hit.chunk.get("text") or ""), 700),
                    }
                )
                for hit in hits
            ],
        }
        sources = [hit.to_source() for hit in hits]
        summary = f"фрагментов: {len(hits)}" if hits else "ничего не найдено"
        return {"result": payload, "summary": summary, "sources": sources}

    def _tool_company_profile(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        company = self.retriever.company()
        if not company:
            return {"result": {"found": False}, "summary": "карточка компании не заполнена", "sources": []}
        payload = _compact(
            {
                "name": company.get("name"),
                "site": company.get("site"),
                "industry": company.get("industry"),
                "description": _clip(str(company.get("description") or ""), 800),
                "products": company.get("products"),
                "contacts": company.get("contacts"),
                "source": company.get("source"),
            }
        )
        sources = []
        if company.get("source"):
            sources = [
                {
                    "id": "company",
                    "title": f"Компания {company.get('name')}",
                    "kind": "company",
                    "score": 1.0,
                    "why": ["profile"],
                    "excerpt": _clip(str(company.get("description") or ""), 200),
                    "source": company["source"],
                }
            ]
        return {"result": payload, "summary": f"карточка {company.get('name')}", "sources": sources}

    def _tool_find_product(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        query = str(args.get("query") or "").strip()
        records = self.retriever.find_product(query, limit=5)
        payload = {
            "products": [
                _compact(
                    {
                        "name": record.get("name"),
                        "description": _clip(str(record.get("description") or ""), 400),
                        "source": record.get("source"),
                    }
                )
                for record in records
            ]
        }
        return {
            "result": payload,
            "summary": f"продуктов: {len(records)}" if records else "продукт не найден",
            "sources": [],
        }

    def _tool_find_person(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        query = str(args.get("query") or "").strip()
        records = self.retriever.find_person(query, limit=5)
        payload = {
            "people": [
                _compact(
                    {
                        "name": record.get("name"),
                        "role": record.get("role"),
                        "source": record.get("source"),
                    }
                )
                for record in records
            ]
        }
        return {
            "result": payload,
            "summary": f"сотрудников: {len(records)}" if records else "сотрудник не найден",
            "sources": [],
        }

    def _tool_find_faq(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        query = str(args.get("query") or "").strip()
        records = self.retriever.find_faq(query, limit=5)
        payload = {
            "faq": [
                _compact(
                    {
                        "question": record.get("question"),
                        "answer": _clip(str(record.get("answer") or ""), 500),
                        "source": record.get("source"),
                    }
                )
                for record in records
            ]
        }
        return {
            "result": payload,
            "summary": f"вопросов: {len(records)}" if records else "в FAQ не найдено",
            "sources": [],
        }

    def _tool_ask_clarification(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        clarification = _clean_clarification(args)
        if not clarification:
            return {
                "result": {"error": "нужно 2–10 вопросов с вариантами"},
                "summary": "уточнение не сформировано",
                "sources": [],
            }
        return {
            "result": clarification,
            "clarification": clarification,
            "summary": "уточняющий вопрос клиенту",
            "sources": [],
        }

    def _tool_offer_followups(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        items = _clean_followups(args.get("items"))
        summary = (
            f"предложил продолжить: {len(items)}"
            if items
            else "продолжение не предложено"
        )
        return {
            "result": {"items": items, "count": len(items)},
            "summary": summary,
            "sources": [],
        }

    def _tool_kb_stats(self, args: Dict[str, Any], question: str = "") -> Dict[str, Any]:
        stats = dict(self.stats)
        stats.pop("kinds", None)
        return {"result": stats, "summary": f"фрагментов: {stats.get('chunks')}", "sources": []}

    def _execute(self, call: ToolCall, question: str = "") -> Dict[str, Any]:
        try:
            args = json.loads(call.arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        if not isinstance(args, dict):
            args = {}
        handlers = {
            "plan": self._tool_plan,
            "search_knowledge": self._tool_search_knowledge,
            "company_profile": self._tool_company_profile,
            "find_product": self._tool_find_product,
            "find_person": self._tool_find_person,
            "find_faq": self._tool_find_faq,
            "kb_stats": self._tool_kb_stats,
            "offer_followups": self._tool_offer_followups,
            "ask_clarification": self._tool_ask_clarification,
        }
        handler = handlers.get(call.name)
        if handler is None:
            return {"result": {"error": f"неизвестный инструмент {call.name}"}, "summary": "ошибка", "sources": []}
        try:
            return handler(args, question)
        except Exception as exc:  # noqa: BLE001
            return {"result": {"error": str(exc)}, "summary": f"ошибка инструмента: {exc}", "sources": []}

    # --- контекст -------------------------------------------------------
    def _auto_context(
        self,
        question: str,
        show_notes: bool = True,
        hits: Optional[int] = None,
        catalog: bool = False,
    ) -> tuple[str, List[Dict[str, Any]]]:
        if not self.settings.auto_context:
            return "", []
        lines: List[str] = [
            "",
            "КОНТЕКСТ (уже загружено — инструменты не нужны):"
            if show_notes
            else "СПРАВКА (факты для ответа):",
        ]
        company = self.retriever.company()
        if company:
            lines.append(
                "Компания: "
                + ", ".join(
                    part
                    for part in (
                        str(company.get("name") or ""),
                        str(company.get("industry") or ""),
                        str(company.get("site") or ""),
                    )
                    if part
                )
            )
            if company.get("description"):
                lines.append("Описание: " + _clip(str(company["description"]), 500))

        if catalog:
            lines.append("Каталог программ:")
            for record in self.retriever.products():
                name = str(record.get("name") or "").strip()
                description = _clip(str(record.get("description") or ""), 240)
                if name:
                    lines.append(f"- {name}: {description}")
        for record in self.retriever.find_product(question, limit=2):
            lines.append(f"Продукт: {record.get('name')} — {_clip(str(record.get('description') or ''), 300)}")
        for record in self.retriever.find_person(question, limit=2):
            role = f" ({record.get('role')})" if record.get("role") else ""
            lines.append(f"Сотрудник: {record.get('name')}{role}")

        hits = self.retriever.search(
            question, k=hits or self.profile.retrieval.context_hits
        )
        sources: List[Dict[str, Any]] = []
        for hit in hits:
            text = str(hit.chunk.get("text") or "")
            if not text:
                continue
            if show_notes:
                header = f"[{hit.chunk.get('title')} · {hit.chunk.get('source')}]"
            else:
                header = "Факт:"
            lines.append(
                f"{header}\n                {_clip(text, self.profile.retrieval.excerpt_chars)}"
            )
            sources.append(hit.to_source())
        return "\n".join(lines), sources

    @staticmethod
    def _context_key(history: Optional[Sequence[Dict[str, Any]]]) -> str:
        if not history:
            return ""
        parts = []
        for item in list(history)[-8:]:
            if not isinstance(item, dict):
                continue
            role = item.get("role")
            content = str(item.get("content") or "").strip()
            if role in ("user", "assistant") and content:
                parts.append(f"{role}:{content}")
        if not parts:
            return ""
        return hashlib.sha1("\n".join(parts).encode("utf-8")).hexdigest()[:16]

    def _should_offer_followups(self, question: str, answer: str) -> bool:
        text = (answer or "").strip()
        if len(text) < 140:
            return False
        return True

    def _suggest_followups(self, question: str, answer: str) -> List[str]:
        """Запасные варианты, когда модель не вернула кнопки."""
        text = f"{question} {answer}".lower()
        options: List[str] = []

        try:
            products = self.retriever.find_product(f"{question} {answer[:400]}", limit=2)
        except Exception:  # noqa: BLE001
            products = []
        for product in products[:2]:
            name = str(product.get("name") or "").strip()
            if not name:
                continue
            options.append(f"Подробнее о программе: {name}")
            if "сколько стоит" not in question.lower():
                options.append(f"Стоимость: {name}")

        if any(word in text for word in ("корпоратив", "компани", "сотрудник")):
            options.extend(
                [
                    "Какие форматы корпоративного обучения?",
                    "Как запросить смету?",
                ]
            )
        elif any(word in text for word in ("школьн", "ребен", "ребён", "подрост")):
            options.extend(
                [
                    "Что входит в программу для школьников?",
                    "Как проходит пробное занятие?",
                ]
            )
        else:
            options.extend(
                [
                    "Какие форматы обучения есть?",
                    "Как проходит поступление?",
                    "Как с вами связаться?",
                ]
            )

        normalized_question = " ".join(question.lower().split()).strip(" ?")
        unique: List[str] = []
        for option in options:
            value = " ".join(option.split()).strip()
            if not value:
                continue
            if value.lower().strip(" ?") == normalized_question:
                continue
            if value.lower() in {item.lower() for item in unique}:
                continue
            unique.append(value)
            if len(unique) >= 4:
                break
        return _clean_followups(unique)

    # --- выбор режима ---------------------------------------------------
    def _resolve_mode(
        self,
        question: str,
        lang: str,
        usage_out: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, str, str]:
        """Режим по сложности вопроса: (fast|thinking, объяснение, кто решил)."""
        fallback, reason = heuristic_mode(question)
        # Очевидные случаи решаем без отдельного запроса к модели — это быстрее.
        if reason in ("короткое приветствие", "пустой вопрос"):
            return fallback, reason, "эвристика"
        if not self.client or self.settings.is_local:
            return fallback, reason, "эвристика"
        cache_key = f"{lang}|{question.strip().lower()}"
        cached = self._mode_cache.get(cache_key)
        if cached is not None:
            return cached[0], cached[1], "кэш режима"
        try:
            messages = [
                {"role": "system", "content": MODE_PROMPT},
                {"role": "user", "content": question},
            ]
            parts: List[str] = []
            mode_usage: Dict[str, Any] = {}
            for event in self.client.stream_chat(
                messages, None, allow_thinking=False, max_tokens=96
            ):
                if event.type == "delta":
                    parts.append(event.text)
                elif event.type == "done" and event.usage:
                    mode_usage = event.usage
            parsed = parse_mode("".join(parts))
            if parsed:
                if usage_out is not None:
                    usage_out.update(mode_usage)
                result = (parsed, "модель оценила сложность", "модель")
                if len(self._mode_cache) > 256:
                    self._mode_cache.clear()
                self._mode_cache[cache_key] = result
                return result
        except Exception:  # noqa: BLE001
            pass
        return fallback, reason, "эвристика"

    # --- ответ ----------------------------------------------------------
    def run(
        self,
        question: str,
        history: Optional[Sequence[Dict[str, Any]]] = None,
        show_notes: bool = True,
        use_cache: bool = True,
        mode: str = "thinking",
    ) -> Iterator[Dict[str, Any]]:
        question = (question or "").strip()
        if not question:
            yield {"type": "error", "message": "Пустой запрос"}
            return

        requested = str(mode).lower()
        if requested not in ("auto", "fast", "thinking", "direct"):
            requested = "auto"
        lang = detect_lang(question)
        auto = requested == "auto"
        direct = requested == "direct"
        mode_usage: Dict[str, Any] = {}
        if auto:
            mode, decision, decided_by = self._resolve_mode(
                question, lang, usage_out=mode_usage
            )
        elif direct:
            mode, decision, decided_by = "thinking", "ответ после уточнения", "система"
        else:
            mode = "fast" if requested == "fast" else "thinking"
            decision = "режим выбран вручную"
            decided_by = "пользователь"
        yield {
            "type": "start",
            "mode": "api" if self.client else "demo",
            "answer_mode": mode,
            "requested_mode": requested,
            "auto": auto,
            "complexity": decision,
            "decided_by": decided_by,
            "lang": lang,
            "model": self.settings.effective_model if self.client else "retrieval-only",
            "thinking": bool(self.client and self.client.thinking_supported and mode == "thinking"),
            "notes": bool(show_notes),
            "company": self.company,
        }

        context_key = self._context_key(history)
        if self.cache is not None and use_cache and self.settings.answer_cache:
            try:
                hit = self.cache.lookup(
                    question,
                    show_notes=show_notes,
                    mode=mode,
                    lang=lang,
                    context_key=context_key,
                )
            except Exception:  # noqa: BLE001
                hit = None
            if hit:
                yield from self._cached_answer(hit, show_notes=show_notes)
                return

        if not self.client:
            yield from self._run_offline(question, lang)
            return

        if mode == "clarify":
            yield from self._run_clarification(
                question, lang, history, show_notes, base_usage=mode_usage
            )
            return

        if direct:
            yield from self._run_single(
                question, lang, history, show_notes, mode, direct=True,
                context_key=context_key, base_usage=mode_usage,
            )
            return

        single_call = mode == "fast" or self.settings.is_local
        if single_call:
            yield from self._run_single(
                question, lang, history, show_notes, mode, direct=direct,
                context_key=context_key, base_usage=mode_usage,
            )
            return

        yield from self._run_agent(
            question, lang, history, show_notes, mode, context_key=context_key,
            base_usage=mode_usage,
        )

    def _run_clarification(
        self,
        question: str,
        lang: str,
        history: Optional[Sequence[Dict[str, Any]]],
        show_notes: bool,
        base_usage: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        """Один короткий вызов: получить у клиента недостающий параметр."""
        ask_tool = next(
            (
                tool
                for tool in (self.tools or [])
                if tool["function"]["name"] == "ask_clarification"
            ),
            None,
        )
        if ask_tool is None or self.client is None:
            yield from self._run_agent(
                question, lang, history, show_notes, "thinking",
                base_usage=base_usage,
            )
            return

        context, _ = self._auto_context(
            question, show_notes=False, catalog=True
        )
        context = _clip(context, 2400)
        system = (
            f"Ты — {self.profile.persona.role} компании «{self.company}». "
            "Представь, что ты сотрудник компании, который консультирует клиента. "
            "Клиент задал вопрос или попросил действие, но для точной рекомендации "
            "не хватает информации. Твоя задача — полностью собрать вводные, а не уложиться "
            "в определённое число вопросов. Задай столько вопросов, сколько реально нужно: "
            "обычно 4, для широкого запроса — 5–8, максимум 10. Четыре — ориентир, а не потолок: "
            "не сокращай опрос ради четырёх и не добавляй вопросы, которые не влияют на рекомендацию. "
            "Не спрашивай то, что уже известно. "
            "Вызови ask_clarification; у каждого вопроса 2–3 конкретных варианта, свой вариант клиент введёт сам. "
            "Опирайся на материалы компании: не добавляй направления, услуги и технологии, "
            "которых нет в справке. Не отвечай на исходный вопрос сейчас."
        )
        if context:
            system += "\n\n" + context
        messages: List[Dict[str, Any]] = [{"role": "system", "content": system}]
        messages.extend(self._prepare_history(history))
        messages.append({"role": "user", "content": question})

        yield {"type": "step", "n": 1, "max": 1}
        calls: List[ToolCall] = []
        usage: Dict[str, Any] = {}
        for event in self.client.stream_chat(
            messages, [ask_tool], allow_thinking=False, max_tokens=1400
        ):
            if event.type == "tool_calls":
                calls = event.tool_calls
            elif event.type == "done":
                usage = event.usage or usage

        for call in calls:
            if call.name != "ask_clarification":
                continue
            try:
                args = json.loads(call.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            if not isinstance(args, dict):
                args = {}
            clarification = _clean_clarification(args)
            if not clarification:
                continue
            tool_entry = {
                "name": call.name,
                "arguments": args,
                "reason": str(args.get("reason") or ""),
                "summary": "уточняющий вопрос клиенту",
            }
            total_usage = _empty_usage()
            _merge_usage(total_usage, base_usage)
            _merge_usage(total_usage, usage)
            yield {"type": "clarification", **clarification}
            yield {
                "type": "done",
                "text": clarification.get("summary") or clarification["question"],
                "reasoning": "",
                "plan": None,
                "steps": 1,
                "usage": usage,
                "usage_total": total_usage,
                "sources": [],
                "attachments": [],
                "tool_calls": [tool_entry],
                "followups": [],
                "clarification": clarification,
                "cached": False,
                "mode": "clarify",
            }
            return

        # Модель не вернула уточнение — отвечаем обычным путём.
        yield from self._run_agent(
            question, lang, history, show_notes, "thinking",
            base_usage=base_usage,
        )

    def _run_single(
        self,
        question: str,
        lang: str,
        history: Optional[Sequence[Dict[str, Any]]],
        show_notes: bool,
        mode: str,
        direct: bool = False,
        context_key: str = "",
        base_usage: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        query = question
        if direct and history:
            previous = next(
                (
                    str(item.get("content") or "").strip()
                    for item in reversed(history)
                    if item.get("role") == "user" and item.get("content")
                ),
                "",
            )
            if previous and previous not in query:
                query = f"{previous}\n{question}"
        context, context_sources = self._auto_context(
            query, show_notes, hits=5 if direct else None, catalog=direct
        )
        if direct:
            prompt = build_system_prompt(
                self.stats, self.profile, lang=lang, include_tools=False
            )
            prompt += (
                "\n\nКлиент уже ответил на уточняющие вопросы. Не задавай новых вопросов. "
                "Дай полноценную рекомендацию связным текстом, как консультант: короткий заголовок `##`, "
                "2–3 коротких абзаца через пустую строку и **жирные акценты** на ценах, сроках и форматах. "
                "Список или таблицу используй только при сравнении нескольких вариантов или для шагов. "
                "Назови конкретные сроки, форматы, стоимость и источники. Опирайся на каталог программ из контекста: "
                "если подходящие программы там есть, назови их и не утверждай, что данных нет. "
                "Не добавляй технологии и направления, которых нет в контексте. "
                "Не сокращай ответ ради экономии."
            )
        else:
            prompt = build_fast_prompt(
                context, self.profile, lang=lang, show_notes=show_notes
            )
        messages: List[Dict[str, Any]] = [{"role": "system", "content": prompt}]
        messages.extend(self._prepare_history(history))
        messages.append(
            {
                "role": "user",
                "content": f"{question}\n{context}" if context else question,
            }
        )

        max_tokens = (
            1200
            if direct
            else self.profile.limits.local_max_tokens
            if self.settings.is_local
            else self.profile.limits.fast_max_tokens
        )
        yield {"type": "step", "n": 1, "max": 1}

        answer_parts: List[str] = []
        usage: Dict[str, Any] = {}
        for event in self.client.stream_chat(  # type: ignore[union-attr]
            messages, None, allow_thinking=direct, max_tokens=max_tokens
        ):
            if event.type == "delta":
                chunk = sanitize_text(event.text, lang)
                answer_parts.append(chunk)
                yield {"type": "delta", "text": chunk}
            elif event.type == "done":
                usage = event.usage or usage

        answer = sanitize_text("".join(answer_parts).strip(), lang) or fallback_text(lang)
        if not show_notes:
            answer = _client_text(answer)
        followups = (
            self._suggest_followups(question, answer)
            if self._should_offer_followups(question, answer)
            else []
        )
        usage_total = _empty_usage()
        _merge_usage(usage_total, base_usage)
        _merge_usage(usage_total, usage)
        if context_sources and show_notes:
            yield {"type": "sources", "items": context_sources}

        if self.cache is not None and self.settings.answer_cache:
            try:
                self.cache.store(
                    question,
                    answer,
                    sources=context_sources,
                    show_notes=show_notes,
                    model=self.settings.effective_model,
                    tokens=int(usage_total.get("total_tokens") or 0),
                    mode=mode,
                    lang=lang,
                    context_key=context_key,
                )
            except Exception:  # noqa: BLE001
                pass

        yield {
            "type": "done",
            "text": answer,
            "reasoning": "",
            "plan": None,
            "steps": 1,
            "usage": usage,
            "usage_total": usage_total,
            "sources": context_sources,
            "attachments": [],
            "tool_calls": [],
            "followups": followups,
            "cached": False,
            "mode": mode,
        }

    def _run_agent(
        self,
        question: str,
        lang: str,
        history: Optional[Sequence[Dict[str, Any]]],
        show_notes: bool,
        mode: str,
        context_key: str = "",
        base_usage: Optional[Dict[str, Any]] = None,
    ) -> Iterator[Dict[str, Any]]:
        context, context_sources = self._auto_context(question, show_notes)
        messages: List[Dict[str, Any]] = [
            {
                "role": "system",
                "content": build_system_prompt(self.stats, self.profile, lang=lang),
            }
        ]
        messages.extend(self._prepare_history(history))
        messages.append(
            {"role": "user", "content": f"{question}\n{context}" if context else question}
        )

        answer_parts: List[str] = []
        early_parts: List[str] = []
        reasoning_parts: List[str] = []
        sources: Dict[str, Dict[str, Any]] = {
            item["id"]: item for item in context_sources if item.get("id")
        }
        tool_log: List[Dict[str, Any]] = []
        plan: Optional[Dict[str, Any]] = None
        followups: List[str] = []
        clarification: Optional[Dict[str, Any]] = None
        usage_total = _empty_usage()
        _merge_usage(usage_total, base_usage)
        usage: Dict[str, Any] = {}
        step = 0

        try:
            max_steps = self.profile.limits.max_steps
            for step in range(1, max_steps + 1):
                yield {"type": "step", "n": step, "max": max_steps}
                text_parts: List[str] = []
                calls: List[ToolCall] = []
                step_usage: Dict[str, Any] = {}
                finish_reason = ""

                for event in self.client.stream_chat(messages, self.tools or None):  # type: ignore[union-attr]
                    if event.type == "delta":
                        chunk = sanitize_text(event.text, lang)
                        text_parts.append(chunk)
                        yield {"type": "delta", "text": chunk}
                    elif event.type == "reasoning":
                        reasoning_parts.append(event.text)
                        if show_notes:
                            yield {"type": "reasoning_delta", "text": event.text}
                    elif event.type == "tool_calls":
                        calls = event.tool_calls
                    elif event.type == "done":
                        step_usage = event.usage or step_usage
                        usage = step_usage or usage
                        finish_reason = event.finish_reason or finish_reason

                _merge_usage(usage_total, step_usage)

                step_text = "".join(text_parts).strip()
                if not calls:
                    answer_parts.append(step_text)
                    break
                if step_text:
                    early_parts.append(step_text)

                messages.append(
                    {
                        "role": "assistant",
                        "content": "".join(text_parts),
                        "tool_calls": [
                            {
                                "id": call.id,
                                "type": "function",
                                "function": {"name": call.name, "arguments": call.arguments},
                            }
                            for call in calls
                        ],
                    }
                )

                for call in calls:
                    args = {}
                    try:
                        args = json.loads(call.arguments or "{}")
                    except json.JSONDecodeError:
                        pass
                    reason = str((args or {}).get("reason") or "") if isinstance(args, dict) else ""
                    if call.name == "ask_clarification":
                        outcome = self._execute(call, question)
                        clar = outcome.get("clarification")
                        if clar:
                            clarification = clar
                            tool_log.append(
                                {
                                    "name": call.name,
                                    "arguments": args if isinstance(args, dict) else {},
                                    "reason": reason,
                                    "summary": outcome.get("summary", ""),
                                }
                            )
                            break
                    if show_notes:
                        yield {
                            "type": "tool_call",
                            "id": call.id,
                            "name": call.name,
                            "arguments": args if isinstance(args, dict) else {},
                            "reason": reason,
                        }
                    outcome = self._execute(call, question)
                    if call.name == "offer_followups":
                        followups = _clean_followups(
                            (outcome.get("result") or {}).get("items")
                        )
                    summary = outcome.get("summary", "")
                    for source in outcome.get("sources", []):
                        key = source.get("id") or source.get("source") or summary
                        sources[str(key)] = source
                    tool_log.append(
                        {
                            "name": call.name,
                            "arguments": args if isinstance(args, dict) else {},
                            "reason": reason,
                            "summary": summary,
                        }
                    )
                    if call.name == "plan" and outcome.get("plan"):
                        plan = outcome["plan"]
                        if show_notes:
                            yield {"type": "plan", **plan}
                    if show_notes:
                        yield {
                            "type": "tool_result",
                            "id": call.id,
                            "name": call.name,
                            "summary": summary,
                            "sources": outcome.get("sources", [])[:6],
                            "attachments": [],
                        }
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.id,
                            "content": json.dumps(
                                _strip_source_keys(outcome.get("result", {}))
                                if not show_notes
                                else outcome.get("result", {}),
                                ensure_ascii=False,
                            )[:6000],
                        }
                    )
                if clarification:
                    break
                if sources and show_notes:
                    yield {"type": "sources", "items": list(sources.values())}
            else:
                yield {"type": "step", "n": max_steps, "max": max_steps}
                messages.append(
                    {
                        "role": "user",
                        "content": "Ответь по уже собранным данным, без новых инструментов.",
                    }
                )
                final_usage: Dict[str, Any] = {}
                for event in self.client.stream_chat(messages, None):
                    if event.type == "delta":
                        chunk = sanitize_text(event.text, lang)
                        answer_parts.append(chunk)
                        yield {"type": "delta", "text": chunk}
                    elif event.type == "done":
                        final_usage = event.usage or final_usage
                _merge_usage(usage_total, final_usage)

            final_answer = "".join(answer_parts).strip()
            early_answer = "\n\n".join(early_parts).strip()
            if early_answer and (not final_answer or len(final_answer) < 220):
                answer = early_answer
                if final_answer and final_answer not in early_answer:
                    answer = f"{early_answer}\n\n{final_answer}"
            else:
                answer = final_answer or early_answer
            answer = sanitize_text(answer.strip(), lang) or fallback_text(lang)
            if not show_notes:
                answer = _client_text(answer)
            if not followups and self._should_offer_followups(question, answer):
                followups = self._suggest_followups(question, answer)
            reasoning = "".join(reasoning_parts).strip()
            if plan:
                plan_text = "\n".join(
                    f"{index}. {item}" for index, item in enumerate(plan.get("steps", []), start=1)
                )
                reasoning = (f"План:\n{plan_text}" + (f"\n\n{reasoning}" if reasoning else "")).strip()

            if clarification:
                yield {"type": "clarification", **clarification}
                yield {
                    "type": "done",
                    "text": clarification.get("summary") or clarification["question"],
                    "reasoning": reasoning,
                    "plan": plan,
                    "steps": step,
                    "usage": usage,
                    "usage_total": usage_total,
                    "sources": list(sources.values()),
                    "attachments": [],
                    "tool_calls": tool_log,
                    "followups": [],
                    "clarification": clarification,
                    "cached": False,
                    "mode": mode,
                }
                return

            if self.cache is not None and self.settings.answer_cache and answer:
                try:
                    self.cache.store(
                        question,
                        answer,
                        reasoning=reasoning,
                        sources=list(sources.values()),
                        tool_calls=tool_log,
                        show_notes=show_notes,
                        model=self.settings.effective_model,
                        tokens=int(usage_total.get("total_tokens") or 0),
                        mode=mode,
                        lang=lang,
                        context_key=context_key,
                    )
                except Exception:  # noqa: BLE001
                    pass

            yield {
                "type": "done",
                "text": answer,
                "reasoning": reasoning,
                "plan": plan,
                "steps": step,
                "usage": usage,
                "usage_total": usage_total,
                "sources": list(sources.values()),
                "attachments": [],
                "tool_calls": tool_log,
                "followups": followups,
                "cached": False,
                "mode": mode,
            }
        except LLMError as exc:
            yield {"type": "error", "message": str(exc), "status": exc.status}
        except Exception as exc:  # noqa: BLE001
            yield {"type": "error", "message": f"{type(exc).__name__}: {exc}"}

    def _cached_answer(
        self, hit: Dict[str, Any], show_notes: bool = True
    ) -> Iterator[Dict[str, Any]]:
        answer = sanitize_text(
            hit.get("answer") or "", str(hit.get("lang") or "")
        )
        if not show_notes:
            answer = _client_text(answer)
        followups = _followups_from_calls(hit.get("tool_calls"))
        if not followups and self._should_offer_followups(
            str(hit.get("question") or ""), answer
        ):
            followups = self._suggest_followups(str(hit.get("question") or ""), answer)
        sources = hit.get("sources") or []
        yield {
            "type": "cache",
            "hit": True,
            "question": hit.get("question"),
            "similarity": hit.get("similarity"),
            "exact": bool(hit.get("exact")),
        }
        if sources:
            yield {"type": "sources", "items": sources}
        for start in range(0, len(answer), max(1, len(answer) // 20)):
            yield {
                "type": "delta",
                "text": sanitize_text(
                    answer[start:start + max(1, len(answer) // 20)],
                    str(hit.get("lang") or ""),
                ),
            }
        yield {
            "type": "done",
            "text": answer,
            "reasoning": hit.get("reasoning") or "",
            "plan": None,
            "steps": 0,
            "usage": {},
            "usage_total": {},
            "sources": sources,
            "attachments": [],
            "tool_calls": hit.get("tool_calls") or [],
            "followups": followups,
            "cached": True,
            "mode": hit.get("kb_stamp", "").split("|")[-1] or "thinking",
        }

    def _run_offline(self, question: str, lang: str) -> Iterator[Dict[str, Any]]:
        hits = self.retriever.search(question, k=3)
        sources = [hit.to_source() for hit in hits]
        if sources:
            lines = [
                f"**{item['title']}** ({item['source']})\n{item['excerpt']}" for item in sources
            ]
            text = "Нашёл в базе знаний:\n\n" + "\n\n".join(lines)
        else:
            text = fallback_text(lang)
        yield {"type": "tool_call", "id": "offline-search", "name": "search_knowledge", "arguments": {"query": question}, "reason": ""}
        yield {"type": "tool_result", "id": "offline-search", "name": "search_knowledge", "summary": f"фрагментов: {len(hits)}", "sources": sources, "attachments": []}
        if sources:
            yield {"type": "sources", "items": sources}
        yield {"type": "delta", "text": text}
        yield {
            "type": "done",
            "text": text,
            "reasoning": "",
            "plan": None,
            "steps": 1,
            "usage": {},
            "usage_total": _empty_usage(),
            "sources": sources,
            "attachments": [],
            "tool_calls": [{"name": "search_knowledge", "arguments": {"query": question}, "summary": f"фрагментов: {len(hits)}"}],
            "followups": [],
            "cached": False,
            "mode": "demo",
        }

    @staticmethod
    def _prepare_history(history: Optional[Sequence[Dict[str, Any]]]) -> List[Dict[str, str]]:
        if not history:
            return []
        cleaned: List[Dict[str, str]] = []
        for item in history[-MAX_HISTORY_MESSAGES:]:
            role = item.get("role")
            content = str(item.get("content") or "").strip()
            if role not in ("user", "assistant") or not content:
                continue
            cleaned.append({"role": role, "content": _clip(content, 2000)})
        return cleaned
