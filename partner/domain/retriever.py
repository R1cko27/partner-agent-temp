"""Гибридный поиск: плотные эмбеддинги + BM25 + буст по сущностям (RRF)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..engine.bm25 import BM25
from ..engine.embeddings import Embedder
from ..engine.tokenize import clean_text, query_terms, tokenize
from ..engine.vectorstore import VectorStore, open_vector_store

RRF_K = 60
FUZZY = 0.72
# Справочные материалы (глоссарий, термины) не уводим во второй уровень:
# они отвечают на вопрос «что такое X» точнее любой карточки.
_REFERENCE_RE = re.compile(r"глоссар|glossary|termin|термин", re.I)


@dataclass
class SearchHit:
    chunk: Dict[str, Any]
    score: float
    why: List[str]

    def to_source(self, excerpt: int = 320) -> Dict[str, Any]:
        text = str(self.chunk.get("text") or "")
        return {
            "id": self.chunk.get("id"),
            "title": self.chunk.get("title", ""),
            "kind": self.chunk.get("kind", ""),
            "score": round(self.score, 4),
            "why": list(self.why),
            "excerpt": text[:excerpt] + ("…" if len(text) > excerpt else ""),
            "source": self.chunk.get("source", ""),
        }


def _ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


_WORD_RE = re.compile(r"\w{4,}", re.UNICODE)


def _content_words(text: str) -> set:
    """Слова для сравнения фрагментов: короткие и служебные не считаем."""
    return set(_WORD_RE.findall((text or "").lower()))


def _jaccard(first: set, second: set) -> float:
    if not first or not second:
        return 0.0
    return len(first & second) / len(first | second)


class Retriever:
    def __init__(
        self,
        chunks: List[Dict[str, Any]],
        bm25: BM25,
        entities: Dict[str, Any],
        meta: Dict[str, Any],
        embedder: Optional[Embedder] = None,
        vectors: Optional[VectorStore] = None,
    ) -> None:
        self.chunks = chunks
        self.bm25 = bm25
        self.entities = entities or {}
        self.meta = meta or {}
        self.embedder = embedder
        self.vectors = vectors
        self._exclude_kinds: set[str] = set()
        self._dedupe_enabled = True
        self._max_per_doc = 2
        self._dedupe_threshold = 0.75
        self._kind_weights: Dict[str, float] = {}
        self._channel_weights: Dict[str, float] = {}
        self._faq_index = None      # BM25 по вопросам FAQ, строится по требованию
        self._secondary_kinds: set[str] = set()   # документация — во вторую очередь
        self._by_id = {chunk["id"]: chunk for chunk in chunks}
        self._name_index: List[Tuple[str, str, Dict[str, Any]]] = []
        self._build_name_index()

    def set_view(self, exclude_kinds: Optional[Iterable[str]] = None) -> None:
        """Режим просмотра: какие типы фрагментов не участвуют в поиске.

        «Кратко» исключает тяжёлую документацию (kind=doc/web), «полно» — ищет
        по всей базе. Фильтр применяется и к плотному поиску (через where в
        Chroma), и к BM25, и к бусту по сущностям, поэтому выдача не размывается.
        """
        self._exclude_kinds = {str(kind) for kind in (exclude_kinds or []) if kind}

    def _kind_allowed(self, chunk: Dict[str, Any]) -> bool:
        return not self._exclude_kinds or chunk.get("kind") not in self._exclude_kinds

    def _where(self) -> Optional[Dict[str, Any]]:
        if not self._exclude_kinds:
            return None
        return {"kind": {"$nin": sorted(self._exclude_kinds)}}

    def _build_name_index(self) -> None:
        products = (self.entities.get("products") or {}).values()
        people = (self.entities.get("people") or {}).values()
        for record in products:
            if record.get("name"):
                self._name_index.append(("product", str(record["name"]), record))
        for record in people:
            if record.get("name"):
                self._name_index.append(("person", str(record["name"]), record))

    # --- загрузка -------------------------------------------------------
    @classmethod
    def load(
        cls,
        index_dir: Path,
        embedder: Optional[Embedder] = None,
        chroma_dir: Optional[Path] = None,
    ) -> "Retriever":
        chunks = json.loads((index_dir / "chunks.json").read_text(encoding="utf-8"))
        bm25_payload = json.loads((index_dir / "bm25.json").read_text(encoding="utf-8"))
        entities_path = index_dir / "entities.json"
        entities = (
            json.loads(entities_path.read_text(encoding="utf-8"))
            if entities_path.is_file()
            else {}
        )
        meta_path = index_dir / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}

        vectors = None
        if chroma_dir is not None and (chroma_dir / "chroma.sqlite3").exists():
            try:
                vectors = open_vector_store(chroma_dir)
            except Exception:  # noqa: BLE001
                vectors = None

        # Инкрементальные документы: чанки из delta + отдельный BM25 по ним.
        try:
            from .delta import load_delta

            extra = load_delta(index_dir)
        except Exception:  # noqa: BLE001
            extra = []
        if extra:
            chunks = chunks + [
                {
                    "id": item.get("id"),
                    "doc_id": item.get("source") or item.get("id"),
                    "index": 0,
                    "text": item.get("text") or "",
                    "kind": item.get("kind") or "doc",
                    "title": item.get("title") or "",
                    "source": item.get("source") or "",
                }
                for item in extra
                if item.get("text")
            ]

        if extra:
            # Лексический поиск тоже должен видеть новые документы:
            # BM25 собирается по базе и дельте один раз при загрузке.
            from ..engine.tokenize import tokenize

            bm25_index = BM25().fit(
                [tokenize(str(item.get("text") or ""), unique=False) for item in chunks]
            )
        else:
            bm25_index = BM25.from_dict(bm25_payload)

        return cls(
            chunks=chunks,
            bm25=bm25_index,
            entities=entities,
            meta=meta,
            embedder=embedder,
            vectors=vectors,
        )

    # --- ранжирование ---------------------------------------------------
    def _dense_ranking(self, query: str, limit: int = 40) -> List[Tuple[str, float]]:
        if not self.embedder or not self.vectors:
            return []
        try:
            vector = self.embedder.embed_query(query)
        except Exception:  # noqa: BLE001
            return []
        if not vector:
            return []
        raw = self.vectors.query(vector, k=limit, where=self._where())
        excluded = set(self._exclude_kinds)
        if excluded:
            raw = [
                (chunk_id, score)
                for chunk_id, score in raw
                if str((self._by_id.get(chunk_id) or {}).get("kind") or "") not in excluded
            ]
        return raw[:limit]

    def _sparse_ranking(self, query: str, limit: int = 40) -> List[Tuple[str, float]]:
        terms = query_terms(query)
        if not terms:
            return []
        scores = self.bm25.scores(terms)
        ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
        hits: List[Tuple[str, float]] = []
        for index, score in ranked:
            if score <= 0 or index >= len(self.chunks):
                continue
            chunk = self.chunks[index]
            if not self._kind_allowed(chunk):
                continue
            hits.append((chunk["id"], score))
            if len(hits) >= limit:
                break
        return hits

    def _entity_ranking(self, query: str, limit: int = 20) -> List[Tuple[str, float]]:
        text = clean_text(query)
        if not text:
            return []
        boosted: Dict[str, float] = {}
        for kind, name, _record in self._name_index:
            name_clean = clean_text(name)
            score = 1.0 if name_clean and name_clean in text else _ratio(text, name_clean)
            if score < FUZZY and name_clean not in text:
                continue
            for chunk in self.chunks:
                if not self._kind_allowed(chunk):
                    continue
                entities = chunk.get("entities") or {}
                if kind in entities and clean_text(str(entities[kind])) == name_clean:
                    boosted[chunk["id"]] = max(boosted.get(chunk["id"], 0.0), score)
        ranked = sorted(boosted.items(), key=lambda pair: pair[1], reverse=True)
        return ranked[:limit]

    # --- веса источников ------------------------------------------------
    def set_kind_weights(self, weights: Optional[Dict[str, float]] = None) -> None:
        """Приоритет типов фрагментов при слиянии.

        Курируемые карточки (faq, product, about, company) должны обгонять
        сырые страницы документации: они короче, свежее и уже проверены.
        Вес умножает вклад канала в RRF, а не отбрасывает документы.
        """
        clean: Dict[str, float] = {}
        for kind, value in (weights or {}).items():
            try:
                weight = float(value)
            except (TypeError, ValueError):
                continue
            if 0.1 <= weight <= 3.0:
                clean[str(kind)] = weight
        self._kind_weights = clean

    def _weight_for(self, chunk: Dict[str, Any]) -> float:
        return self._kind_weights.get(str(chunk.get("kind") or ""), 1.0)

    def set_channel_weights(self, weights: Optional[Dict[str, float]] = None) -> None:
        """Приоритет каналов поиска при слиянии: bm25, dense, entity.

        Точный термин («политика сети», «7.7») лексический поиск ловит надёжнее
        плотного, поэтому вес BM25 по умолчанию выше.
        """
        clean: Dict[str, float] = {}
        for channel, value in (weights or {}).items():
            try:
                weight = float(value)
            except (TypeError, ValueError):
                continue
            if 0.1 <= weight <= 3.0:
                clean[str(channel)] = weight
        self._channel_weights = clean

    def search(self, query: str, k: int = 6) -> List[SearchHit]:
        query = (query or "").strip()
        if not query:
            return []
        fused: Dict[str, float] = {}
        reasons: Dict[str, List[str]] = {}

        def add(ranking: Sequence[Tuple[str, float]], label: str) -> None:
            channel = self._channel_weights.get(label, 1.0)
            for rank, (chunk_id, _score) in enumerate(ranking):
                chunk = self._by_id.get(chunk_id)
                if chunk is None:
                    continue
                weight = self._weight_for(chunk) * channel
                fused[chunk_id] = fused.get(chunk_id, 0.0) + weight / (RRF_K + rank + 1)
                reasons.setdefault(chunk_id, []).append(f"{label}#{rank + 1}")

        add(self._dense_ranking(query), "dense")
        add(self._sparse_ranking(query), "bm25")
        add(self._entity_ranking(query), "entity")

        if not fused:
            fallback = [chunk for chunk in self.chunks if chunk.get("kind") == "overview"][:1]
            return [
                SearchHit(chunk=chunk, score=0.0, why=["fallback:overview"])
                for chunk in fallback
            ]

        ordered = sorted(fused.items(), key=lambda pair: pair[1], reverse=True)
        ordered = self._order_by_tier(ordered)
        selected = self._dedupe(ordered, k)
        return [
            SearchHit(chunk=self._by_id[chunk_id], score=score, why=reasons.get(chunk_id, []))
            for chunk_id, score in selected
        ]

    # --- уровни источников ----------------------------------------------
    def set_secondary_kinds(self, kinds: Optional[Iterable[str]] = None) -> None:
        """Типы фрагментов, которые идут во вторую очередь.

        Курируемые карточки (FAQ, продукт, контакты) отвечают на вопрос клиента
        точнее, чем глава руководства администратора. Документация подключается
        только на свободные места — когда карточек не хватило.
        """
        self._secondary_kinds = {str(kind) for kind in (kinds or []) if kind}

    def _order_by_tier(
        self, ordered: Sequence[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        if not self._secondary_kinds:
            return list(ordered)
        primary: List[Tuple[str, float]] = []
        secondary: List[Tuple[str, float]] = []
        for chunk_id, score in ordered:
            chunk = self._by_id.get(chunk_id) or {}
            kind = chunk.get("kind")
            # Справочник терминов — не глава руководства: он отвечает на вопрос
            # «что такое X» точнее любой карточки, поэтому остаётся в первом уровне.
            reference = _REFERENCE_RE.search(
                f"{chunk.get('title') or ''} {chunk.get('source') or ''}"
            )
            if kind in self._secondary_kinds and not reference:
                secondary.append((chunk_id, score))
            else:
                primary.append((chunk_id, score))
        return primary + secondary

    # --- дедупликация выдачи ---------------------------------------------
    def set_dedupe(
        self,
        max_per_doc: int = 2,
        threshold: float = 0.75,
        enabled: bool = True,
    ) -> None:
        """Насколько строго вычищать повторы в выдаче.

        Одни и те же статьи документации лежат в деревьях разных продуктов,
        поэтому без этого в контекст попадали почти одинаковые фрагменты и
        вытесняли полезные.
        """
        self._dedupe_enabled = bool(enabled)
        self._max_per_doc = max(1, int(max_per_doc))
        self._dedupe_threshold = min(0.99, max(0.3, float(threshold)))

    def _dedupe(self, ordered: Sequence[Tuple[str, float]], k: int) -> List[Tuple[str, float]]:
        if not self._dedupe_enabled or k <= 0:
            return list(ordered[:k])
        selected: List[Tuple[str, float]] = []
        per_doc: Dict[str, int] = {}
        word_sets: List[set] = []
        for chunk_id, score in ordered:
            chunk = self._by_id.get(chunk_id)
            if chunk is None:
                continue
            doc_id = str(chunk.get("doc_id") or "")
            if doc_id and per_doc.get(doc_id, 0) >= self._max_per_doc:
                continue
            words = _content_words(str(chunk.get("text") or ""))
            duplicate = False
            for other in word_sets:
                if _jaccard(words, other) >= self._dedupe_threshold:
                    duplicate = True
                    break
            if duplicate:
                continue
            per_doc[doc_id] = per_doc.get(doc_id, 0) + 1
            word_sets.append(words)
            selected.append((chunk_id, score))
            if len(selected) >= k:
                break
        return selected

    # --- справочники ----------------------------------------------------
    def company(self) -> Dict[str, Any]:
        return dict(self.entities.get("company") or {})

    def products(self) -> List[Dict[str, Any]]:
        return list((self.entities.get("products") or {}).values())

    def find_product(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self._find_named(query, "products", limit)

    def find_person(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        return self._find_named(query, "people", limit)

    def _find_named(self, query: str, collection: str, limit: int) -> List[Dict[str, Any]]:
        records = list((self.entities.get(collection) or {}).values())
        text = clean_text(query or "")
        if not text:
            return []
        exact: List[Dict[str, Any]] = []
        partial: List[Dict[str, Any]] = []
        for record in records:
            name = clean_text(str(record.get("name") or ""))
            if not name:
                continue
            if name in text or text in name:
                exact.append(record)
            elif _ratio(name, text) >= FUZZY:
                partial.append(record)
        return (exact or partial)[:limit]

    def find_term(self, query: str, limit: int = 2) -> List[Dict[str, Any]]:
        """Точный поиск термина в глоссарии: «что такое X» → определение.

        Термин считается найденным, если он входит в запрос целыми словами.
        Длинные термины приоритетнее: «BFD profile» точнее, чем «BFD».
        """
        entries = self.entities.get("glossary") or []
        if not entries:
            return []
        haystack = " " + clean_text(query or "").lower() + " "
        matches: List[Tuple[int, Dict[str, Any]]] = []
        for entry in entries:
            term = clean_text(str(entry.get("term") or "")).lower()
            if not term or len(term) < 2:
                continue
            # «BFD (Bidirectional…)» проверяем и по части до скобки.
            variants = {term, term.split("(")[0].strip()}
            for variant in variants:
                if len(variant) >= 2 and f" {variant} " in haystack:
                    matches.append((len(variant), entry))
                    break
        matches.sort(key=lambda pair: pair[0], reverse=True)
        seen: set[str] = set()
        result: List[Dict[str, Any]] = []
        for _length, entry in matches:
            key = str(entry.get("term") or "").lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(entry)
            if len(result) >= limit:
                break
        return result

    def chunks_by_source(self, pattern: str, limit: int = 3) -> List[SearchHit]:
        """Фрагменты из конкретного документа: нужно, когда ответ живёт в одной карточке."""
        needle = (pattern or "").lower()
        if not needle:
            return []
        hits: List[SearchHit] = []
        for chunk in self._by_id.values():
            source = str(chunk.get("source") or "").lower()
            if needle in source:
                hits.append(SearchHit(chunk=chunk, score=0.05, why=["source-match"]))
                if len(hits) >= limit:
                    break
        return hits

    def faq_items(self) -> List[Dict[str, Any]]:
        """Все карточки FAQ.

        Нужны продолжениям: канал, названный в ответе, ищется по ответам FAQ,
        а не по одному вопросу пользователя.
        """
        return list(self.entities.get("faq") or [])

    def glossary_items(self) -> List[Dict[str, Any]]:
        """Все термины глоссария: продолжение «что такое X» берёт соседние."""
        return list(self.entities.get("glossary") or [])

    def find_faq(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Поиск по вопросам FAQ: BM25 по самим вопросам, а не по длинному тексту.

        Раньше сравнивались целые строки, и короткий вопрос вроде «где ваш офис»
        не находил карточку «Есть ли офис в Новосибирске?».
        """
        faq = list(self.entities.get("faq") or [])
        if not faq:
            return []
        terms = query_terms(query or "")
        if not terms:
            return []
        if self._faq_index is None:
            self._faq_index = BM25().fit(
                [tokenize(str(item.get("question") or ""), unique=False) for item in faq]
            )
        scores = self._faq_index.scores(terms)
        ranked = sorted(
            ((index, score) for index, score in enumerate(scores) if score > 0),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [faq[index] for index, _score in ranked[:limit]]

    # --- служебное ------------------------------------------------------
    def stats(self) -> Dict[str, Any]:
        kinds: Dict[str, int] = {}
        for chunk in self.chunks:
            kind = chunk.get("kind", "other")
            kinds[kind] = kinds.get(kind, 0) + 1
        return {
            "chunks": len(self.chunks),
            "kinds": kinds,
            "products": len(self.entities.get("products") or {}),
            "people": len(self.entities.get("people") or {}),
            "faq": len(self.entities.get("faq") or []),
            "news": len(self.entities.get("news") or []),
            "company": (self.entities.get("company") or {}).get("name", ""),
            "built_at": self.meta.get("built_at", ""),
            "embedding": self.meta.get("embedding", ""),
            "vectors": self.meta.get("vectors", len(self.chunks)),
        }
