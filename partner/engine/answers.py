"""Кэш ответов: похожий вопрос получает уже готовый ответ без вызова модели.

Зачем: агент отвечает на многие вопросы повторно, а каждый ответ стоит
несколько секунд и тысяч токенов. Ответы сохраняются в SQLite вместе с
эмбеддингом вопроса; новый вопрос сначала ищется в кэше:

1. точное совпадение нормализованного текста — сразу ответ;
2. иначе косинусная близость эмбеддингов ≥ порога **и** пересечение слов
   (Jaccard) ≥ порога, иначе «похожий» вопрос про другую карту даст ложное
   попадание;
3. сущности (карты/мапперы) в вопросе должны совпадать: «расскажи про
   ze_changed» и «расскажи про ze_rush_a» — разные вопросы, хоть и похожи.

Кэш привязан к сборке индекса (`kb_stamp`): после пересборки старые ответы не
выдаются, потому что данные могли измениться.
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Sequence, Set

# Меняйте версию при изменении промптов/правил ответа: старые ответы
# перестанут попадать в кэш, даже если база знаний не пересобиралась.
CACHE_VERSION = "2026-11-22.3"

_PUNCT_RE = re.compile(r"[^\w\s]+", re.UNICODE)
STOP_WORDS = {
    "и", "в", "на", "по", "с", "со", "а", "но", "что", "как", "это", "для",
    "про", "из", "у", "к", "от", "до", "за", "же", "ли", "не", "мне", "мы",
    "ты", "вы", "он", "она", "они", "есть", "ли", "или", "the", "a", "of",
}


def normalize_question(text: str) -> str:
    lowered = (text or "").lower().replace("ё", "е")
    return " ".join(_PUNCT_RE.sub(" ", lowered).split())


def _tokens(text: str) -> Set[str]:
    return {word for word in normalize_question(text).split() if word not in STOP_WORDS}


def jaccard(first: Set[str], second: Set[str]) -> float:
    if not first or not second:
        return 0.0
    union = first | second
    return len(first & second) / len(union)


def cosine(first: Sequence[float], second: Sequence[float]) -> float:
    if not first or not second or len(first) != len(second):
        return 0.0
    dot = sum(a * b for a, b in zip(first, second))
    norm_a = math.sqrt(sum(a * a for a in first))
    norm_b = math.sqrt(sum(b * b for b in second))
    if not norm_a or not norm_b:
        return 0.0
    return dot / (norm_a * norm_b)


def entity_keys(entities: Optional[Sequence[Dict[str, Any]]]) -> List[str]:
    keys = []
    for entity in entities or []:
        if not isinstance(entity, dict):
            continue
        kind = entity.get("type")
        key = entity.get("key")
        if kind and key:
            keys.append(f"{kind}:{key}")
    return sorted(set(keys))


class AnswerCache:
    """Обёртка над таблицей answer_cache."""

    def __init__(
        self,
        db: Any,
        embedder: Any = None,
        threshold: float = 0.93,
        min_jaccard: float = 0.55,
        kb_stamp: str = "",
        ttl_days: int = 7,
        max_entries: int = 500,
    ) -> None:
        self.db = db
        self.embedder = embedder
        self.threshold = threshold
        self.min_jaccard = min_jaccard
        self.kb_stamp = kb_stamp or ""
        self.ttl_days = max(0, int(ttl_days))
        self.max_entries = max(10, int(max_entries))

    # --- срок жизни -----------------------------------------------------
    def _cutoff(self) -> str:
        """Граница «свежести»: ответы старше не отдаём и чистим."""
        if not self.ttl_days:
            return ""
        moment = datetime.now(timezone.utc) - timedelta(days=self.ttl_days)
        return moment.isoformat(timespec="seconds")

    def _stamp(self, mode: str = "", context_key: str = "") -> str:
        """Режим, версия промптов и контекст чата входят в ключ свежести."""
        return "|".join(
            part for part in (self.kb_stamp, mode, CACHE_VERSION, context_key) if part
        )

    def prune(self) -> int:
        """Удаляет просроченные и лишние ответы; возвращает число удалённых."""
        try:
            return self.db.cache_prune(self._cutoff(), self.max_entries)
        except Exception:  # noqa: BLE001
            return 0

    # --- поиск ----------------------------------------------------------
    def _embed(self, question: str) -> Optional[List[float]]:
        if self.embedder is None:
            return None
        try:
            if hasattr(self.embedder, "available") and not self.embedder.available():
                return None
            vector = self.embedder.embed_query(question)
            return list(vector) if vector else None
        except Exception:  # noqa: BLE001
            return None

    def lookup(
        self,
        question: str,
        show_notes: bool = True,
        entities: Optional[Sequence[Dict[str, Any]]] = None,
        mode: str = "",
        lang: str = "",
        context_key: str = "",
    ) -> Optional[Dict[str, Any]]:
        normalized = normalize_question(question)
        if not normalized:
            return None
        candidates = self.db.cache_candidates(
            show_notes, self._stamp(mode, context_key), self._cutoff(), lang
        )
        if not candidates:
            return None

        current_entities = entity_keys(entities)
        for entry in candidates:
            if entry.get("normalized") != normalized:
                continue
            if sorted(set(entry.get("entities") or [])) != current_entities:
                continue
            self.db.cache_touch(entry["id"])
            return {**entry, "similarity": 1.0, "exact": True}

        vector = self._embed(question)
        if not vector:
            return None

        tokens = _tokens(question)
        best: Optional[Dict[str, Any]] = None
        best_score = 0.0
        for entry in candidates:
            if sorted(set(entry.get("entities") or [])) != current_entities:
                continue
            entry_vector = entry.get("embedding") or []
            if not entry_vector:
                continue
            similarity = cosine(vector, entry_vector)
            if similarity < self.threshold:
                continue
            overlap = jaccard(tokens, _tokens(entry.get("question") or ""))
            if overlap < self.min_jaccard:
                continue
            if similarity > best_score:
                best_score = similarity
                best = {**entry, "similarity": round(similarity, 3), "exact": False}
        if best:
            self.db.cache_touch(best["id"])
        return best

    # --- сохранение -----------------------------------------------------
    def store(
        self,
        question: str,
        answer: str,
        *,
        reasoning: str = "",
        sources: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        show_notes: bool = True,
        entities: Optional[Sequence[Dict[str, Any]]] = None,
        model: str = "",
        tokens: int = 0,
        min_answer_chars: int = 80,
        mode: str = "",
        lang: str = "",
        context_key: str = "",
    ) -> int:
        normalized = normalize_question(question)
        if not normalized or len(answer or "") < min_answer_chars:
            return 0
        vector = self._embed(question)
        # Каждое сохранение — повод вычистить просроченное и лишнее.
        self.prune()
        return self.db.cache_store(
            question=question,
            normalized=normalized,
            answer=answer,
            reasoning=reasoning,
            sources=sources,
            attachments=attachments,
            tool_calls=tool_calls,
            embedding=vector,
            entities=entity_keys(entities),
            show_notes=show_notes,
            kb_stamp=self._stamp(mode, context_key),
            lang=lang,
            model=model,
            tokens=tokens,
        )

    def stats(self) -> Dict[str, int]:
        stats = dict(self.db.cache_stats())
        stats["ttl_days"] = self.ttl_days
        stats["max_entries"] = self.max_entries
        return stats

    def clear(self) -> int:
        return self.db.cache_clear()
