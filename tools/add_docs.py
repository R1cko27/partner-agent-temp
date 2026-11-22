"""Инкрементальное пополнение общей базы: PDF, TXT и страницы по ссылке.

    py tools/add_docs.py --file "C:\\docs\\manual.pdf"
    py tools/add_docs.py --url https://usergate.com/products/
    py tools/add_docs.py --folder "C:\\docs"

Чанки и векторы кладутся в ту же Chroma (`storage/chroma`, коллекция s2ze_kb),
тексты — в `storage/index/delta/chunks.jsonl`. Пересборка индекса не нужна.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import pathlib
import sys
from typing import Any, Dict, List

# Только для запуска из консоли: при импорте из сервера нельзя подменять
# sys.stdout (сборщик мусора закрывает буфер, и сервер теряет вывод).
if __name__ == "__main__" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from partner.config import Settings
from partner.domain import delta
from partner.engine.chunking import Chunker
from partner.engine.embeddings import Embedder
from partner.engine.vectorstore import COLLECTION, open_vector_store


def load_rag_core():
    """Подключаем парсеры PDF/URL из rag_streamlit как библиотеку."""
    path = pathlib.Path(__file__).resolve().parent.parent / "rag_streamlit" / "core.py"
    spec = importlib.util.spec_from_file_location("rag_core", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def collect(args, core) -> List[Any]:
    documents = []
    for item in args.file or []:
        path = pathlib.Path(item)
        if not path.is_file():
            print("нет файла:", path)
            continue
        documents.append(
            core.load_pdf(path) if path.suffix.lower() == ".pdf" else core.load_text_file(path)
        )
    for url in args.url or []:
        try:
            documents.append(core.load_url(url))
        except Exception as exc:  # noqa: BLE001
            print(f"не удалось скачать {url}: {exc}")
    for folder in args.folder or []:
        found, skipped = core.load_folder(pathlib.Path(folder))
        documents.extend(found)
        for item in skipped:
            print("  пропущено:", item)
    return documents


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Добавить документы в общую базу")
    parser.add_argument("--file", action="append", help="PDF или TXT")
    parser.add_argument("--url", action="append", help="страница по ссылке")
    parser.add_argument("--folder", action="append", help="папка с PDF/TXT")
    parser.add_argument("--as", dest="as_name", help="Имя источника в базе")
    parser.add_argument("--dry-run", action="store_true", help="только показать, что будет добавлено")
    args = parser.parse_args(argv)

    settings = Settings.load()
    core = load_rag_core()
    documents = collect(args, core)
    if not documents:
        print("нечего добавлять")
        return 1

    if args.as_name:
        for document in documents:
            document.source = args.as_name
            document.title = args.as_name

    chunker = Chunker(settings.chunk_size, settings.chunk_overlap)
    manifest = delta.load_manifest(settings.index_dir)

    prepared: List[Dict[str, Any]] = []
    for document in documents:
        source = str(getattr(document, "source", "") or getattr(document, "title", ""))
        text = str(getattr(document, "text", ""))
        if not text.strip():
            print("пустой текст:", source)
            continue
        key = delta.document_key(source, text)
        if manifest.get(source, {}).get("hash") == key:
            print("уже в базе, пропуск:", source)
            continue
        pieces = chunker.split_text(text)
        slug = delta.slug(source)
        for index, piece in enumerate(pieces):
            digest = hashlib.sha1(piece.encode("utf-8")).hexdigest()[:10]
            prepared.append(
                {
                    "id": f"{slug}:{index}:{digest}",
                    "text": piece,
                    "source": source,
                    "title": str(getattr(document, "title", "") or source),
                    "url": str(getattr(document, "url", "") or ""),
                    "kind": "doc",
                    "_hash": key,
                    "_chunks": len(pieces),
                }
            )
        print(f"{source}: {len(pieces)} фрагментов")

    if not prepared:
        print("новых фрагментов нет")
        return 0
    if args.dry_run:
        print("dry-run: записано не будет, фрагментов", len(prepared))
        return 0

    embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
    if not embedder.available:
        print("эмбеддинги недоступны:", embedder.error)
        return 1

    vectors = embedder.embed_documents([item["text"] for item in prepared])
    if len(vectors) != len(prepared):
        print("модель вернула неверное число векторов")
        return 1

    store = open_vector_store(settings.chroma_dir, prefer_chroma=True)
    if store is None:
        print("хранилище недоступно")
        return 1
    for item in prepared:
        item.pop("_hash", None)
        item.pop("_chunks", None)
    # Пишем в общую коллекцию: те же id, что уйдут в delta.
    try:
        store.collection.upsert(
            ids=[item["id"] for item in prepared],
            embeddings=[list(vector) for vector in vectors],
            documents=[item["text"] for item in prepared],
            metadatas=[
                {
                    "source": item["source"],
                    "title": item["title"],
                    "url": item["url"],
                    "kind": item["kind"],
                }
                for item in prepared
            ],
        )
    except Exception as exc:  # noqa: BLE001
        print("не удалось записать векторы:", exc)
        return 1

    added = delta.append_delta(settings.index_dir, prepared)
    for document in documents:
        source = str(getattr(document, "source", "") or "")
        text = str(getattr(document, "text", ""))
        if source:
            delta.remember_document(
                settings.index_dir, source, delta.document_key(source, text),
                sum(1 for item in prepared if item["source"] == source),
            )

    print(f"добавлено фрагментов: {added} · коллекция: {COLLECTION}")
    print("пересборка не требуется: документы лежат в delta и в общей Chroma")
    return 0


if __name__ == "__main__":
    sys.exit(main())
