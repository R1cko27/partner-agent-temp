"""Ядро RAG-прототипа: загрузка документов, чанкинг, эмбеддинги, ChromaDB.

Главный принцип — запись в базу только добавляет данные.
Коллекция никогда не пересоздаётся: чанки пишутся через upsert с
детерминированными id, поэтому повторная индексация того же документа
не создаёт дублей и не стирает ранее загруженные материалы.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION = "rag_docs"

SUPPORTED_TEXT = {".txt", ".md"}
SUPPORTED_PDF = {".pdf"}
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


# --- документы ----------------------------------------------------------
@dataclass
class Document:
    doc_id: str
    title: str
    text: str
    source: str  # путь к файлу или URL
    source_type: str  # "file" | "url"
    added_at: str = ""
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def digest(self) -> str:
        return hashlib.sha1(self.text.encode("utf-8")).hexdigest()


def _clean(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t\u00a0]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _doc_id(source: str) -> str:
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:16]


def load_text_file(path: Path) -> Document:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("utf-8", errors="replace")
    return Document(
        doc_id=_doc_id(str(path.resolve())),
        title=path.name,
        text=_clean(text),
        source=str(path.resolve()),
        source_type="file",
        added_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    )


def load_pdf(path: Path) -> Document:
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages: List[str] = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # noqa: BLE001
            continue
    return Document(
        doc_id=_doc_id(str(path.resolve())),
        title=path.name,
        text=_clean("\n".join(pages)),
        source=str(path.resolve()),
        source_type="file",
        added_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    )


def load_url(url: str) -> Document:
    """Скачивает страницу, вычищает script/style/nav/footer и сохраняет текст."""
    import httpx
    from bs4 import BeautifulSoup

    response = httpx.get(
        url,
        follow_redirects=True,
        timeout=40,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "ru,en;q=0.9"},
    )
    response.raise_for_status()
    response.encoding = response.encoding or "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = " ".join(str(soup.title.string).split())
    for heading in soup.find_all(["h1", "h2", "h3"]):
        heading.insert_before("\n\n")

    text = _clean(soup.get_text("\n"))
    return Document(
        doc_id=_doc_id(url),
        title=title or url,
        text=text,
        source=url,
        source_type="url",
        added_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        meta={"status_code": response.status_code},
    )


def load_folder(folder: Path) -> Tuple[List[Document], List[str]]:
    """Читает все PDF и TXT в папке (рекурсивно). Возвращает документы и ошибки."""
    documents: List[Document] = []
    errors: List[str] = []
    if not folder.exists():
        return documents, [f"папка не найдена: {folder}"]

    for path in sorted(folder.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        try:
            if suffix in SUPPORTED_PDF:
                documents.append(load_pdf(path))
            elif suffix in SUPPORTED_TEXT:
                documents.append(load_text_file(path))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path.name}: {exc}")
    return documents, errors


# --- чанкинг ------------------------------------------------------------
def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Режет текст на фрагменты по size символов с перекрытием overlap.

    Границы стараемся ставить по абзацу или предложению рядом с лимитом,
    чтобы не рвать мысль посередине.
    """
    text = _clean(text)
    if not text:
        return []
    if len(text) <= size:
        return [text]

    step = max(1, size - overlap)
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            window = text[start:end]
            for pattern in ("\n\n", ". ", "! ", "? ", "\n"):
                cut = window.rfind(pattern)
                if cut > size * 0.6:
                    end = start + cut + len(pattern)
                    break
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        if end >= len(text):
            break
        start += step
        if start >= len(text):
            break
    return chunks


def chunk_ids(document: Document, chunks: List[str]) -> List[str]:
    """Стабильные id: один и тот же чанк не задвоится при повторной индексации."""
    return [
        hashlib.sha1(f"{document.doc_id}:{index}:{piece}".encode("utf-8")).hexdigest()[:24]
        for index, piece in enumerate(chunks)
    ]


# --- эмбеддинги ---------------------------------------------------------
class Embedder:
    """Локальные эмбеддинги через fastembed, с запасным ONNX-бэкендом Chroma."""

    def __init__(self, model_name: str = EMBED_MODEL, cache_dir: Optional[Path] = None) -> None:
        self.model_name = model_name
        self.cache_dir = cache_dir
        self._model = None
        self._fallback = None
        self.error = ""
        self._init_model()

    def _init_model(self) -> None:
        try:
            from fastembed import TextEmbedding

            kwargs: Dict[str, Any] = {"model_name": self.model_name}
            if self.cache_dir:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                kwargs["cache_dir"] = str(self.cache_dir / "fastembed")
            self._model = TextEmbedding(**kwargs)
            probe = list(self._model.embed(["проверка"]))
            if probe:
                return
        except Exception as exc:  # noqa: BLE001
            self.error = f"fastembed: {exc}"
            self._model = None

        try:
            from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

            self._fallback = ONNXMiniLM_L6_V2()
            self._fallback(["probe"])
        except Exception as exc:  # noqa: BLE001
            self.error += f"; ONNX: {exc}"
            self._fallback = None

    @property
    def available(self) -> bool:
        return self._model is not None or self._fallback is not None

    def embed(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        if not texts:
            return []
        if self._model is not None:
            return [list(map(float, vec)) for vec in self._model.embed(texts, batch_size=batch_size)]
        if self._fallback is not None:
            return [list(map(float, vec)) for vec in self._fallback(texts)]
        return []


# --- хранилище ----------------------------------------------------------
class Store:
    """Обёртка над ChromaDB: только добавление, без пересоздания коллекции."""

    def __init__(self, path: Path, embedder: Embedder) -> None:
        import chromadb
        from chromadb.config import Settings as ChromaSettings

        self.path = path
        self.embedder = embedder
        path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=str(path),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )
        try:
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION, metadata={"hnsw:space": "cosine"}
            )
        except Exception:  # noqa: BLE001
            self.collection = self.client.get_or_create_collection(name=COLLECTION)
        self.manifest_path = path / "manifest.json"
        self.manifest: Dict[str, Dict[str, Any]] = self._read_manifest()

    # --- манифест -------------------------------------------------------
    def _read_manifest(self) -> Dict[str, Dict[str, Any]]:
        if not self.manifest_path.exists():
            return {}
        try:
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def _write_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.manifest, ensure_ascii=False, indent=1), encoding="utf-8"
        )

    # --- статус ---------------------------------------------------------
    def count(self) -> int:
        try:
            return int(self.collection.count())
        except Exception:  # noqa: BLE001
            return 0

    def is_indexed(self, document: Document) -> bool:
        entry = self.manifest.get(document.doc_id)
        return bool(entry) and entry.get("digest") == document.digest

    def documents(self) -> List[Dict[str, Any]]:
        return [
            {
                "doc_id": doc_id,
                "source": entry.get("source", ""),
                "type": entry.get("type", ""),
                "chunks": entry.get("chunks", 0),
                "added_at": entry.get("added_at", ""),
            }
            for doc_id, entry in sorted(self.manifest.items(), key=lambda kv: kv[1].get("added_at", ""))
        ]

    # --- запись ---------------------------------------------------------
    def add_documents(self, documents: List[Document], progress=None) -> Dict[str, Any]:
        """Добавляет документы в базу. Уже проиндексированные пропускаются."""
        report = {"added_docs": 0, "skipped": 0, "chunks": 0, "errors": []}
        for document in documents:
            if not document.text.strip():
                report["errors"].append(f"{document.source}: пустой текст")
                continue
            if self.is_indexed(document):
                report["skipped"] += 1
                continue

            chunks = chunk_text(document.text)
            if not chunks:
                report["errors"].append(f"{document.source}: не удалось нарезать")
                continue

            vectors = self.embedder.embed(chunks)
            if not vectors:
                report["errors"].append(f"{document.source}: эмбеддинги недоступны")
                continue

            ids = chunk_ids(document, chunks)
            metadatas = [
                {
                    "doc_id": document.doc_id,
                    "source": document.source,
                    "source_type": document.source_type,
                    "title": document.title[:300],
                    "chunk_index": index,
                }
                for index, _ in enumerate(chunks)
            ]
            # upsert, а не add: повторный прогон не создаёт дублей.
            self.collection.upsert(
                ids=ids, embeddings=vectors, documents=chunks, metadatas=metadatas
            )

            self.manifest[document.doc_id] = {
                "source": document.source,
                "type": document.source_type,
                "title": document.title,
                "digest": document.digest,
                "chunks": len(chunks),
                "added_at": document.added_at or time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            self._write_manifest()

            report["added_docs"] += 1
            report["chunks"] += len(chunks)
            if progress:
                progress(f"{document.title}: +{len(chunks)} фрагментов")
        return report

    def drop_document(self, doc_id: str) -> int:
        """Удаляет чанки одного документа — только по явному действию пользователя."""
        try:
            self.collection.delete(where={"doc_id": doc_id})
        except Exception:  # noqa: BLE001
            return 0
        removed = self.manifest.pop(doc_id, None)
        self._write_manifest()
        return int(removed.get("chunks", 0)) if removed else 0

    # --- поиск ----------------------------------------------------------
    def search(self, question: str, k: int = 3) -> List[Dict[str, Any]]:
        vector = self.embedder.embed([question])
        if not vector:
            return []
        try:
            result = self.collection.query(
                query_embeddings=vector, n_results=max(1, k), include=["documents", "metadatas", "distances"]
            )
        except Exception:  # noqa: BLE001
            return []

        hits: List[Dict[str, Any]] = []
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]
        for text, meta, distance in zip(documents, metadatas, distances):
            meta = meta or {}
            hits.append(
                {
                    "text": text or "",
                    "source": meta.get("source", ""),
                    "title": meta.get("title", ""),
                    "source_type": meta.get("source_type", ""),
                    "score": round(1.0 - float(distance), 4),
                }
            )
        return hits
