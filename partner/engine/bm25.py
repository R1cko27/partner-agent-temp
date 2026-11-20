"""BM25 с сериализацией в JSON — лексический ретривер без внешних зависимостей.

DeepSeek API не предоставляет embeddings-эндпоинт, поэтому вместо векторного
поиска используется BM25 плюс (в retriever.py) точное и нечёткое сопоставление
ников. Для корпуса в сотни чанков этого более чем достаточно.
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence, Tuple


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self.doc_count = 0
        self.avg_len = 0.0
        self.doc_len: List[int] = []
        self.term_freq: List[Dict[str, int]] = []
        self.doc_freq: Dict[str, int] = {}

    def fit(self, docs: Sequence[Sequence[str]]) -> "BM25":
        self.doc_count = len(docs)
        self.term_freq = []
        self.doc_len = []
        self.doc_freq = {}

        for tokens in docs:
            tf: Dict[str, int] = {}
            for token in tokens:
                tf[token] = tf.get(token, 0) + 1
            self.term_freq.append(tf)
            self.doc_len.append(len(tokens))
            for token in tf:
                self.doc_freq[token] = self.doc_freq.get(token, 0) + 1

        self.avg_len = (sum(self.doc_len) / self.doc_count) if self.doc_count else 0.0
        return self

    def idf(self, term: str) -> float:
        if not self.doc_count:
            return 0.0
        df = self.doc_freq.get(term, 0)
        return math.log(1.0 + (self.doc_count - df + 0.5) / (df + 0.5))

    def scores(self, query_tokens: Sequence[str]) -> List[float]:
        """BM25 для каждого документа; редкие термины весят больше частых."""
        result = [0.0] * self.doc_count
        if not self.doc_count or not query_tokens:
            return result

        unique_terms = list(dict.fromkeys(query_tokens))
        for term in unique_terms:
            df = self.doc_freq.get(term)
            if not df:
                continue
            idf = self.idf(term)
            for index, tf in enumerate(self.term_freq):
                freq = tf.get(term)
                if not freq:
                    continue
                dl = self.doc_len[index]
                denom = freq + self.k1 * (1 - self.b + self.b * dl / (self.avg_len or 1.0))
                result[index] += idf * (freq * (self.k1 + 1)) / (denom or 1.0)
        return result

    def top_n(self, query_tokens: Sequence[str], limit: int = 5) -> List[Tuple[int, float]]:
        scored = [(index, score) for index, score in enumerate(self.scores(query_tokens)) if score > 0]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:limit]

    # --- сериализация ---------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "k1": self.k1,
            "b": self.b,
            "doc_count": self.doc_count,
            "avg_len": self.avg_len,
            "doc_len": self.doc_len,
            "term_freq": self.term_freq,
            "doc_freq": self.doc_freq,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "BM25":
        model = cls(k1=payload.get("k1", 1.5), b=payload.get("b", 0.75))
        model.doc_count = payload.get("doc_count", 0)
        model.avg_len = payload.get("avg_len", 0.0)
        model.doc_len = list(payload.get("doc_len", []))
        model.term_freq = list(payload.get("term_freq", []))
        model.doc_freq = dict(payload.get("doc_freq", {}))
        return model
