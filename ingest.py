"""CLI: собрать базу знаний Partner-Agent из материалов компании.

    python ingest.py                 # полная сборка (BM25 + эмбеддинги)
    python ingest.py --skip-embeddings  # только лексический индекс, быстро
    python ingest.py --no-web        # не скачивать URL из urls.txt

Что происходит:
1. `data/company/` читается конверторами: PDF, DOCX, HTML, Markdown, TXT, JSON, CSV;
2. URL из `data/company/urls.txt` скачиваются и очищаются от разметки;
3. источники превращаются в карточки: компания, продукты, люди, FAQ, новости;
4. карточки режутся на чанки (RecursiveCharacterTextSplitter);
5. строятся BM25 и Chroma, справочники сохраняются для инструментов агента.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from partner import compat  # noqa: F401  (патчи временных каталогов)
from partner.config import Settings
from partner.domain.loaders import build_knowledge
from partner.engine.bm25 import BM25
from partner.engine.chunking import Chunker
from partner.engine.embeddings import Embedder
from partner.engine.logbook import write_log
from partner.engine.tokenize import tokenize
from partner.engine.vectorstore import VectorStore


def log(message: str) -> None:
    write_log(message)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Сборка базы знаний Partner-Agent")
    parser.add_argument("--data", help="Каталог с материалами компании (по умолчанию data/)")
    parser.add_argument("--storage", help="Каталог индекса и истории (по умолчанию storage/)")
    parser.add_argument("--no-web", action="store_true", help="Не скачивать URL из urls.txt")
    parser.add_argument("--skip-embeddings", action="store_true", help="Только BM25, без Chroma")
    parser.add_argument("--chunk-size", type=int, help="Размер чанка в символах")
    args = parser.parse_args(argv)

    settings = Settings.load()
    if args.data:
        settings.data_dir = Path(args.data)
    if args.storage:
        settings.storage_dir = Path(args.storage)
    if args.chunk_size:
        settings.chunk_size = args.chunk_size

    started = time.perf_counter()
    index_dir = settings.index_dir
    index_dir.mkdir(parents=True, exist_ok=True)

    log(f"→ Читаю материалы: {settings.data_dir}")
    knowledge = build_knowledge(
        settings.data_dir,
        fetch_web=not args.no_web,
        progress=log,
    )
    report = knowledge.report
    entities = knowledge.entities
    log(
        f"  документов: {report.get('documents', len(knowledge.documents))}, "
        f"компания: {entities.company.get('name') or '—'}, "
        f"продуктов {len(entities.products)}, людей {len(entities.people)}, "
        f"FAQ {len(entities.faq)}, новостей {len(entities.news)}"
    )
    if report.get("errors"):
        log(f"  ! не удалось скачать: {len(report['errors'])} URL")

    log("→ Чанкую документы …")
    chunker = Chunker(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    chunks = chunker.split_documents(knowledge.documents)
    average = sum(len(chunk.text) for chunk in chunks) // max(1, len(chunks))
    log(f"  чанков: {len(chunks)} (в среднем {average} символов)")

    log("→ Строю BM25 …")
    bm25 = BM25().fit([tokenize(chunk.text, unique=False) for chunk in chunks])
    log(f"  терминов в словаре: {len(bm25.doc_freq)}")

    embedding_label = "lexical-only"
    vectors: VectorStore | None = None
    if args.skip_embeddings or not settings.use_dense:
        log("→ Эмбеддинги пропущены (лексический режим)")
    else:
        log(f"→ Загружаю модель эмбеддингов {settings.embed_model} …")
        embedder = Embedder(settings.embed_model, cache_dir=settings.storage_dir / "models")
        log(f"  {embedder.describe()}")
        if not embedder.available:
            log(f"  ! эмбеддинги недоступны: {embedder.error}")
        else:
            texts = [chunk.text for chunk in chunks]
            batch = 128
            vectors = VectorStore(settings.chroma_dir)
            vectors.reset()
            embed_started = time.perf_counter()
            all_vectors: list[list[float]] = []
            for start in range(0, len(texts), batch):
                part = texts[start:start + batch]
                part_vectors = embedder.embed_documents(part)
                if not part_vectors:
                    log("  ! модель не вернула векторы, останавливаю эмбеддинг")
                    break
                all_vectors.extend(part_vectors)
                done = min(start + batch, len(texts))
                elapsed = time.perf_counter() - embed_started
                speed = done / elapsed if elapsed else 0
                log(f"  {done}/{len(texts)} векторов · {speed:.1f}/с")
            if all_vectors:
                vectors.add(chunks[: len(all_vectors)], all_vectors)
            log(f"  в Chroma: {vectors.count()} векторов")
            embedding_label = embedder.describe()

    log("→ Сохраняю индекс …")
    (index_dir / "chunks.json").write_text(
        json.dumps([chunk.to_dict() for chunk in chunks], ensure_ascii=False),
        encoding="utf-8",
    )
    (index_dir / "bm25.json").write_text(
        json.dumps(bm25.to_dict(), ensure_ascii=False), encoding="utf-8"
    )
    (index_dir / "entities.json").write_text(
        json.dumps(
            {
                **entities.as_dict(),
                "report": report,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    meta = {
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "chunks": len(chunks),
        "vectors": vectors.count() if vectors else 0,
        "embedding": embedding_label,
        "company": entities.company.get("name", ""),
        "counts": {
            "documents": len(knowledge.documents),
            "products": len(entities.products),
            "people": len(entities.people),
            "faq": len(entities.faq),
            "news": len(entities.news),
        },
        "report": report,
    }
    (index_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    elapsed = time.perf_counter() - started
    log("")
    log("=" * 62)
    log(f"  Готово за {elapsed:.1f} с")
    log(f"  Фрагментов: {len(chunks)} · BM25-терминов: {len(bm25.doc_freq)}")
    log(f"  Эмбеддинги: {embedding_label}")
    log(f"  Компания: {entities.company.get('name') or '—'}")
    log(f"  Индекс: {index_dir}")
    log("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
