"""Модель-судья: проверяет ответ и контекст, который получает агент.

Два режима:

1. `judge_answer` — сравнивает ответ с эталоном: верно / частично / неверно /
   выдумка. Не наказывает за перефразирование, наказывает за неверный факт,
   выдуманные числа и потерю обязательных элементов.

2. `judge_context` — проверяет сам контекст: есть ли в нём ответ, нет ли мусора
   (новостные посты вместо документации), нет ли противоречий. Если контекста
   не хватает, агент получает указание не выдумывать.

Включается через `JUDGE_ENABLED=1`; по умолчанию выключен, чтобы не удваивать
стоимость и задержку обычных ответов.
"""

from __future__ import annotations

import io
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .llm import DeepSeekClient

ANSWER_SYSTEM = """Ты — строгий приёмщик ответов корпоративного ассистента.
Сравни ответ агента с эталоном и верни ТОЛЬКО JSON без пояснений:

{"verdict": "ok|partial|wrong|invented",
 "score": 0.0-1.0,
 "missing": ["чего не хватает из эталона"],
 "invented": ["факты, которых нет ни в эталоне, ни в материалах"],
 "comment": "одна короткая фраза"}

Правила:
- ok — все ключевые факты эталона переданы, лишнего не выдумано; формулировка может отличаться.
- partial — часть ключевых фактов отсутствует, но ошибок нет.
- wrong — факт передан неверно или подменён другим продуктом/версией.
- invented — есть число, сертификат, цена или адрес, которых нет ни в эталоне, ни в КОНТЕКСТЕ.
- Дополнительные подробности, которые есть в КОНТЕКСТЕ, — это ok, а не invented и не partial.
- Перефразирование, другой порядок и более подробное объяснение — это ok, не partial.
- Если в ответе честно сказано, что данных нет, а эталон тоже про отсутствие данных — это ok.
- Эталон короткий: ответ может быть подробнее, если подробности подтверждаются контекстом.""" 

CONTEXT_SYSTEM = """Ты — контролёр контекста, который подаётся модели.
Оцени, достаточно ли этого контекста, чтобы ответить на вопрос. Верни ТОЛЬКО JSON:

{"enough": true|false,
 "relevant": true|false,
 "noise": ["фрагменты не по теме"],
 "missing": ["каких сведений не хватает"],
 "comment": "одна короткая фраза"}

Правила:
- enough=true, если в контексте есть факты, позволяющие ответить по существу.
- relevant=false, если большинство фрагментов не относятся к вопросу (например, посты соцсетей вместо документации).
- Если вопрос о том, чего в базе нет (цена, SLA, сертификат версии) — enough=true и при пустом контексте, если ответ должен быть «данных нет».""" 


@dataclass
class Verdict:
    verdict: str = "unknown"
    score: float = 0.0
    missing: List[str] = field(default_factory=list)
    invented: List[str] = field(default_factory=list)
    comment: str = ""

    @property
    def ok(self) -> bool:
        return self.verdict == "ok"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict,
            "score": round(self.score, 2),
            "missing": self.missing,
            "invented": self.invented,
            "comment": self.comment,
        }


CANDIDATES_SYSTEM = """Ты — контролёр поиска. Тебе дают вопрос и список кандидатов,
которые нашла система (номер, тип источника, заголовок, начало текста, оценка).
Оцени, где в этом списке лежит ответ и что система сделала не так. Верни ТОЛЬКО JSON:

{"answer_in_candidates": true|false,
 "best_index": номер кандидата с ответом или -1,
 "noise": ["номера кандидатов не по теме"],
 "missed": ["номера кандидатов, в которых есть ответ, но которые могут не попасть в контекст"],
 "duplicates": ["номера почти одинаковых кандидатов"],
 "comment": "одна короткая фраза"}

Правила:
- best_index — самый точный кандидат: где факт сформулирован прямо, а не упомянут вскользь.
- Предпочитай документацию и карточки продуктов, а не новости и посты соцсетей.
- Если ответа нет ни в одном кандидате — answer_in_candidates=false, best_index=-1.
- Не считай шумом кандидата, который полезен частично: шум — это не по теме вообще."""


@dataclass
class CandidateVerdict:
    """Разбор кандидатов поиска: где лежит ответ и что отбросили зря."""

    answer_in_candidates: bool = False
    best_index: int = -1
    noise: List[str] = field(default_factory=list)
    missed: List[str] = field(default_factory=list)
    duplicates: List[str] = field(default_factory=list)
    comment: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "answer_in_candidates": self.answer_in_candidates,
            "best_index": self.best_index,
            "noise": self.noise,
            "missed": self.missed,
            "duplicates": self.duplicates,
            "comment": self.comment,
        }


@dataclass
class ContextVerdict:
    enough: bool = True
    relevant: bool = True
    noise: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    comment: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "enough": self.enough,
            "relevant": self.relevant,
            "noise": self.noise,
            "missing": self.missing,
            "comment": self.comment,
        }


def _numbers_in(text: str) -> List[str]:
    return [re.sub(r"\s+", "", item) for item in re.findall(r"\d[\d\s.,]{2,}", text or "")]


def _normalize_numbers(text: str) -> set:
    return {re.sub(r"\s+", "", item) for item in re.findall(r"\d[\d\s.,]{2,}", text or "")}


def _json_block(text: str) -> Dict[str, Any]:
    """Достаёт JSON из ответа модели: чинит обрезанный ответ и повторяет попытку."""
    value = (text or "").strip()
    if value.startswith("```"):
        value = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", value)
    start = value.find("{")
    if start < 0:
        return {}
    body = value[start:]
    for attempt in range(3):
        candidate = body if attempt == 0 else body + ("}" * attempt)
        end = candidate.rfind("}")
        if end < 0:
            continue
        try:
            return json.loads(candidate[: end + 1])
        except json.JSONDecodeError:
            continue
    # Последняя попытка: вытащить поля регулярками.
    fields: Dict[str, Any] = {}
    found = re.search(r'"verdict"\s*:\s*"(ok|partial|wrong|invented)"', body)
    if found:
        fields["verdict"] = found.group(1)
    score = re.search(r'"score"\s*:\s*([0-9.]+)', body)
    if score:
        fields["score"] = float(score.group(1))
    for key in ("enough", "relevant"):
        flag = re.search(rf'"{key}"\s*:\s*(true|false)', body)
        if flag:
            fields[key] = flag.group(1) == "true"
    comment = re.search(r'"comment"\s*:\s*"([^"]{0,200})"', body)
    if comment:
        fields["comment"] = comment.group(1)
    return fields


class Judge:
    def __init__(
        self,
        client: DeepSeekClient,
        enabled: bool = True,
        max_tokens: int = 700,
        facts_path: Optional[Path] = None,
    ) -> None:
        self.client = client
        self.enabled = enabled
        self.max_tokens = max_tokens
        self._facts_path = facts_path or Path("storage/index/facts.json")
        self._facts: Dict[str, Any] = {}

    def _load_facts(self) -> Dict[str, Any]:
        """Реестр фактов базы: числа, версии, адреса, события."""
        if self._facts:
            return self._facts
        try:
            self._facts = json.loads(self._facts_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._facts = {}
        return self._facts

    def known_number(self, number: str) -> bool:
        facts = self._load_facts()
        return str(number) in (facts.get("numbers") or {})

    def known_url(self, url: str) -> bool:
        facts = self._load_facts()
        clean = str(url or "").rstrip(".,;")
        for key in (facts.get("urls") or {}):
            if clean == key or clean.rstrip("/") == key.rstrip("/"):
                return True
            if clean in key or key in clean:
                return True
        return False

    def _ask(self, system: str, user: str) -> Dict[str, Any]:
        if not self.enabled:
            return {}
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        parts = []
        try:
            for event in self.client.stream_chat(
                messages, None, allow_thinking=False, max_tokens=self.max_tokens
            ):
                if getattr(event, "type", "") == "delta":
                    parts.append(getattr(event, "text", "") or "")
        except Exception:  # noqa: BLE001 — судья не должен ронять ответ
            return {}
        return _json_block("".join(parts))

    def judge_answer(self, question: str, reference: str, answer: str, context: str = "") -> Verdict:
        user = (
            f"ВОПРОС:\n{question}\n\n"
            f"ЭТАЛОН:\n{reference}\n\n"
            f"КОНТЕКСТ, КОТОРЫЙ БЫЛ У МОДЕЛИ:\n{context[:3500] or 'не передан'}\n\n"
            f"ОТВЕТ АГЕНТА:\n{answer[:4000]}"
        )
        payload = (
            self._ask(ANSWER_SYSTEM, user)
            or self._ask(ANSWER_SYSTEM, user)
            or self._ask(ANSWER_SYSTEM, user)
        )
        if not payload:
            return Verdict(verdict="unknown", comment="судья недоступен")
        verdict = str(payload.get("verdict") or "unknown").lower()
        if verdict not in ("ok", "partial", "wrong", "invented"):
            verdict = "unknown"
        try:
            score = float(payload.get("score") or 0.0)
        except (TypeError, ValueError):
            score = 0.0
        invented = [str(item) for item in (payload.get("invented") or [])][:5]
        missing = [str(item) for item in (payload.get("missing") or [])][:5]
        # Если судья говорит «выдумка», проверяем по числам и номерам: настоящая
        # выдумка — это цифра, которой нет ни в эталоне, ни в контексте.
        if verdict == "invented":
            known = _normalize_numbers(reference + " " + context)
            # Реестр фактов базы: число может быть верным, но не попасть в контекст.
            unknown = [
                n for n in _numbers_in(answer)
                if n not in known and not self.known_number(n)
            ]
            if not unknown:
                invented = []
                verdict = "partial" if missing else "ok"
        # Детерминированная поправка: если «выдумка» подтверждается контекстом,
        # это не выдумка. Судья видит короткий эталон и перестраховывается.
        if invented and context:
            haystack = context.lower()
            ungrounded = []
            for item in invented:
                words = [w for w in re.findall(r"[\w\-]{4,}", item.lower())]
                if words and all(word[:5] in haystack for word in words):
                    continue        # подтверждено контекстом
                ungrounded.append(item)
            invented = ungrounded
            if not invented and verdict == "invented":
                verdict = "partial" if missing else "ok"
                score = 0.75 if missing else score
        return Verdict(
            verdict=verdict,
            score=max(0.0, min(1.0, score)),
            missing=missing,
            invented=invented,
            comment=str(payload.get("comment") or "")[:200],
        )

    def judge_context(self, question: str, context: str, expect_absent: bool = False) -> ContextVerdict:
        user = (
            f"ВОПРОС:\n{question}\n\n"
            f"{'В базе заведомо НЕТ ответа (цена, SLA, сертификат версии).' if expect_absent else ''}\n"
            f"КОНТЕКСТ, КОТОРЫЙ ПОЛУЧИТ МОДЕЛЬ:\n{context[:6000]}"
        )
        payload = self._ask(CONTEXT_SYSTEM, user)
        if not payload:
            return ContextVerdict(comment="судья недоступен")
        return ContextVerdict(
            enough=bool(payload.get("enough", True)),
            relevant=bool(payload.get("relevant", True)),
            noise=[str(item) for item in (payload.get("noise") or [])][:5],
            missing=[str(item) for item in (payload.get("missing") or [])][:5],
            comment=str(payload.get("comment") or "")[:200],
        )

    def judge_candidates(
        self, question: str, candidates: List[Dict[str, Any]]
    ) -> CandidateVerdict:
        """Оценивает кандидатов поиска: где ответ и что отброшено зря.

        Нужен, чтобы отличать провал поиска (факта нет среди кандидатов) от
        провала отбора (факт найден, но не попал в контекст) и от провала
        генерации (факт в контексте, а модель его не использовала).
        """
        if not candidates:
            return CandidateVerdict(comment="кандидатов нет")
        rows = []
        for index, item in enumerate(candidates, 1):
            rows.append(
                f"{index}. [{item.get('kind', '')}] {str(item.get('title') or '')[:90]}"
                f" · score {item.get('score', 0)}"
                f" · {str(item.get('excerpt') or '')[:260]}"
            )
        user = f"ВОПРОС:\n{question}\n\nКАНДИДАТЫ:\n" + "\n".join(rows)
        payload = self._ask(CANDIDATES_SYSTEM, user)
        if not payload:
            return CandidateVerdict(comment="судья недоступен")
        try:
            best = int(payload.get("best_index", -1))
        except (TypeError, ValueError):
            best = -1
        if best < 1 or best > len(candidates):
            best = -1
        return CandidateVerdict(
            answer_in_candidates=bool(payload.get("answer_in_candidates", best > 0)),
            best_index=best,
            noise=[str(item) for item in (payload.get("noise") or [])][:5],
            missed=[str(item) for item in (payload.get("missed") or [])][:5],
            duplicates=[str(item) for item in (payload.get("duplicates") or [])][:5],
            comment=str(payload.get("comment") or "")[:200],
        )


def context_warning(verdict: ContextVerdict) -> str:
    """Строка-предупреждение для контекста, если судья признал его слабым."""
    if verdict.enough:
        return ""
    missing = ", ".join(verdict.missing[:3]) or "ключевые сведения"
    return (
        "ВНИМАНИЕ: в контексте нет прямого ответа "
        f"({missing}). Не выдумывай факты, числа и адреса: скажи, чего нет в материалах, "
        "и предложи официальный канал."
    )
