"""Гибридный поиск: плотные эмбеддинги + BM25 + буст по сущностям (RRF)."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from ..engine.bm25 import BM25
from ..engine.embeddings import Embedder
from ..engine.tokenize import clean_text, query_terms, tokenize
from ..engine.vectorstore import VectorStore

RRF_K = 60
FUZZY = 0.72


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
        self._by_id = {chunk["id"]: chunk for chunk in chunks}
        self._name_index: List[Tuple[str, str, Dict[str, Any]]] = []
        self._build_name_index()

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
                vectors = VectorStore(chroma_dir)
            except Exception:  # noqa: BLE001
                vectors = None

        return cls(
            chunks=chunks,
            bm25=BM25.from_dict(bm25_payload),
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
        return self.vectors.query(vector, k=limit)

    def _sparse_ranking(self, query: str, limit: int = 40) -> List[Tuple[str, float]]:
        terms = query_terms(query)
        if not terms:
            return []
        scores = self.bm25.scores(terms)
        ranked = sorted(enumerate(scores), key=lambda pair: pair[1], reverse=True)
        return [
            (self.chunks[index]["id"], score)
            for index, score in ranked[:limit]
            if score > 0 and index < len(self.chunks)
        ]

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
                entities = chunk.get("entities") or {}
                if kind in entities and clean_text(str(entities[kind])) == name_clean:
                    boosted[chunk["id"]] = max(boosted.get(chunk["id"], 0.0), score)
        ranked = sorted(boosted.items(), key=lambda pair: pair[1], reverse=True)
        return ranked[:limit]

    def search(self, query: str, k: int = 6) -> List[SearchHit]:
        query = (query or "").strip()
        if not query:
            return []
        fused: Dict[str, float] = {}
        reasons: Dict[str, List[str]] = {}

        def add(ranking: Sequence[Tuple[str, float]], label: str) -> None:
            for rank, (chunk_id, _score) in enumerate(ranking):
                if chunk_id not in self._by_id:
                    continue
                fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank + 1)
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

        ordered = sorted(fused.items(), key=lambda pair: pair[1], reverse=True)[:k]
        return [
            SearchHit(chunk=self._by_id[chunk_id], score=score, why=reasons.get(chunk_id, []))
            for chunk_id, score in ordered
        ]

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

    def find_faq(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        text = clean_text(query or "")
        tokens = set(tokenize(query or "", drop_stopwords=True, unique=False))
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for item in self.entities.get("faq") or []:
            question = clean_text(str(item.get("question") or ""))
            if not question:
                continue
            overlap = len(tokens & set(question.split()))
            ratio = _ratio(text, question)
            score = max(ratio, min(1.0, overlap / max(1, len(tokens))))
            if score >= 0.45:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [item for _score, item in scored[:limit]]

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
