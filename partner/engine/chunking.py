"""Чанкование документов базы знаний.

Структурированные «карточки» (карта, маппер, обзор) уже имеют удобный размер и
не режутся. Длинные свободные тексты (описания карт, PDF, DOCX, HTML-страницы)
режутся `RecursiveCharacterTextSplitter` из langchain-text-splitters по
границам абзацев и предложений с перекрытием.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List

from .types import Document

_SPACE_RE = re.compile(r"\n{3,}")
_HEADING_RE = re.compile(r"(?m)^(#{1,6})\s+(.+)$")


@dataclass
class Chunk:
    id: str
    doc_id: str
    index: int
    text: str
    kind: str
    title: str
    source: str
    entities: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "doc_id": self.doc_id,
            "index": self.index,
            "text": self.text,
            "kind": self.kind,
            "title": self.title,
            "source": self.source,
            "entities": self.entities,
        }


def _short_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()[:8]


def _fallback_split(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Разбиение по абзацам, если langchain недоступен."""
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: List[str] = []
    buffer = ""
    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if buffer:
                chunks.append(buffer)
                buffer = ""
            start = 0
            while start < len(paragraph):
                chunks.append(paragraph[start:start + chunk_size])
                start += max(1, chunk_size - overlap)
            continue
        if len(buffer) + len(paragraph) + 2 <= chunk_size:
            buffer = f"{buffer}\n\n{paragraph}" if buffer else paragraph
        else:
            if buffer:
                chunks.append(buffer)
            buffer = paragraph
    if buffer:
        chunks.append(buffer)
    return chunks


class Chunker:
    def __init__(self, chunk_size: int = 900, chunk_overlap: int = 120) -> None:
        self.chunk_size = max(200, int(chunk_size))
        self.chunk_overlap = max(0, min(int(chunk_overlap), self.chunk_size // 2))
        self._splitter = None
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter

            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
                keep_separator=True,
            )
        except Exception:  # pragma: no cover - окружение без langchain
            self._splitter = None

    def _sections(self, text: str) -> List[tuple[str, str]]:
        """Делит текст по заголовкам markdown, сохраняя название раздела."""
        matches = list(_HEADING_RE.finditer(text))
        if not matches:
            return [("", text)]
        sections: List[tuple[str, str]] = []
        if matches[0].start() > 0:
            head = text[: matches[0].start()].strip()
            if head:
                sections.append(("", head))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            title = match.group(2).strip()
            body = text[match.end():end].strip()
            sections.append((title, body))
        return sections

    def split_text(self, text: str) -> List[str]:
        text = _SPACE_RE.sub("\n\n", text.strip())
        if not text:
            return []
        if len(text) <= int(self.chunk_size * 1.15):
            return [text]

        sections = self._sections(text)
        if len(sections) > 1:
            # Режем по разделам: заголовок остаётся в каждом фрагменте, поэтому
            # «Кластеры → VRRP» находится по словам заголовка, а списки и
            # таблицы не разрываются между частями.
            chunks: List[str] = []
            buffer = ""
            for title, body in sections:
                block = f"{title}\n{body}".strip() if title else body
                if not block:
                    continue
                if len(block) <= self.chunk_size:
                    if buffer and len(buffer) + len(block) + 2 <= self.chunk_size:
                        buffer = f"{buffer}\n\n{block}"
                    else:
                        if buffer:
                            chunks.append(buffer)
                        buffer = block
                    continue
                if buffer:
                    chunks.append(buffer)
                    buffer = ""
                if self._splitter is not None:
                    parts = [part.strip() for part in self._splitter.split_text(block)]
                else:
                    parts = _fallback_split(block, self.chunk_size, self.chunk_overlap)
                for part in parts:
                    if not part:
                        continue
                    # заголовок повторяем, если он оторвался при делении
                    if title and title not in part[:120]:
                        part = f"{title}\n{part}"
                    chunks.append(part)
            if buffer:
                chunks.append(buffer)
            return [chunk.strip() for chunk in chunks if chunk.strip()]

        if self._splitter is not None:
            parts = [part.strip() for part in self._splitter.split_text(text)]
            return [part for part in parts if part]
        return _fallback_split(text, self.chunk_size, self.chunk_overlap)

    def split_document(self, document: Document) -> List[Chunk]:
        text = _SPACE_RE.sub("\n\n", document.text.strip())
        if document.no_split or len(text) <= int(self.chunk_size * 1.15):
            pieces = [text] if text else []
        else:
            pieces = self.split_text(document.text)
        chunks: List[Chunk] = []
        for index, piece in enumerate(pieces):
            chunk_id = document.doc_id if len(pieces) == 1 else f"{document.doc_id}-{index + 1}"
            if len(pieces) > 1:
                chunk_id = f"{chunk_id}-{_short_hash(piece)}"
            chunks.append(
                Chunk(
                    id=chunk_id,
                    doc_id=document.doc_id,
                    index=index,
                    text=piece,
                    kind=document.kind,
                    title=document.title,
                    source=document.source,
                    entities=dict(document.entities),
                )
            )
        return chunks

    def split_documents(self, documents: Iterable[Document]) -> List[Chunk]:
        chunks: List[Chunk] = []
        for document in documents:
            chunks.extend(self.split_document(document))
        return chunks
