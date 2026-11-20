"""Движок RAG: переиспользован из проекта s2ze.com без привязки к предметной области."""

from .answers import AnswerCache
from .bm25 import BM25
from .chunking import Chunker
from .db import ChatDB
from .embeddings import Embedder
from .lang import detect_lang, fallback_text, language_rule
from .llm import DeepSeekClient, LLMError, StreamEvent, ToolCall
from .logbook import log_path, write_log
from .tokenize import clean_text, tokenize
from .types import Document
from .vectorstore import VectorStore

__all__ = [
    "AnswerCache",
    "BM25",
    "ChatDB",
    "Chunker",
    "DeepSeekClient",
    "Document",
    "Embedder",
    "LLMError",
    "StreamEvent",
    "ToolCall",
    "VectorStore",
    "clean_text",
    "detect_lang",
    "fallback_text",
    "language_rule",
    "log_path",
    "tokenize",
    "write_log",
]
