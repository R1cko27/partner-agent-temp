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
import hashlib
import json
import sys
import time
from pathlib import Path

# Русская консоль Windows отдаёт cp1251, а логи содержат «→» и «·».
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from partner import compat  # noqa: F401  (патчи временных каталогов)
from partner.config import Settings
from partner.domain.loaders import build_knowledge
from partner.engine.bm25 import BM25
from partner.engine.chunking import Chunker
from partner.engine.embeddings import Embedder
from partner.engine.logbook import write_log
from partner.engine.tokenize import tokenize
from partner.engine.vectorcache import VectorCache
from partner.engine.vectorstore import VectorStore, open_vector_store


def log(message: str) -> None:
    write_log(message)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Сборка базы знаний Partner-Agent")
    parser.add_argument("--data", help="Каталог с материалами компании (по умолчанию data/)")
    parser.add_argument("--storage", help="Каталог индекса и истории (по умолчанию storage/)")
    parser.add_argument("--no-web", action="store_true", help="Не скачивать URL из urls.txt")
    parser.add_argument("--skip-embeddings", action="store_true", help="Только BM25, без Chroma")
    parser.add_argument("--chunk-size", type=int, help="Размер чанка в символах")
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Считать эмбеддинги только для новых и изменённых фрагментов",
    )
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
    reused_vectors = 0
    embedded_vectors = 0
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
            hashes = [hashlib.md5(text.encode("utf-8")).hexdigest() for text in texts]
            # Кеш валиден только для той же модели и той же нарезки.
            stamp = f"{settings.embed_model}|{settings.chunk_size}|{settings.chunk_overlap}"
            cache = (
                VectorCache.load(index_dir, stamp)
                if args.incremental
                else VectorCache(index_dir, stamp)
            )
            vectors = open_vector_store(settings.chroma_dir, prefer_chroma=True)
        if vectors is not None:
            if getattr(vectors, "supports_where", True) is False:
                log("  ! Chroma недоступна — векторы читаются из vectors.npz")

            # Первый инкрементальный запуск: забираем векторы из уже собранной Chroma,
            # чтобы не считать их заново.
            if args.incremental and len(cache) == 0:
                existing = vectors.all_vectors()
                if existing:
                    known = {chunk.id: hashes[index] for index, chunk in enumerate(chunks)}
                    for chunk_id, vector in existing:
                        if chunk_id in known:
                            cache.put(chunk_id, known[chunk_id], vector)
                    log(f"  кеш заполнен из Chroma: {len(cache)} векторов")

            todo = [
                index
                for index, chunk in enumerate(chunks)
                if cache.get(chunk.id, hashes[index]) is None
            ]
            if args.incremental:
                log(
                    f"  из кеша: {len(chunks) - len(todo)}, "
                    f"считаю заново: {len(todo)}"
                )

            batch = 128
            embed_started = time.perf_counter()
            done = 0
            for start in range(0, len(todo), batch):
                part_indexes = todo[start:start + batch]
                part_vectors = embedder.embed_documents([texts[i] for i in part_indexes])
                if not part_vectors:
                    log("  ! модель не вернула векторы, останавливаю эмбеддинг")
                    break
                for index, vector in zip(part_indexes, part_vectors):
                    cache.put(chunks[index].id, hashes[index], vector)
                done += len(part_indexes)
                elapsed = time.perf_counter() - embed_started
                speed = done / elapsed if elapsed else 0
                log(f"  {done}/{len(todo)} векторов · {speed:.1f}/с")

            ready_chunks = []
            ready_vectors = []
            for index, chunk in enumerate(chunks):
                vector = cache.get(chunk.id, hashes[index])
                if vector is None:
                    continue
                ready_chunks.append(chunk)
                ready_vectors.append(vector)
            missing = len(chunks) - len(ready_chunks)
            if missing:
                log(f"  ! без вектора остались {missing} фрагментов — они не попадут в Chroma")

            if ready_chunks and getattr(vectors, "supports_where", True) is False:
                log("  векторы записаны в кеш: Chroma недоступна, плотный поиск читает npz")
            elif ready_chunks:
                try:
                    if args.incremental:
                        vectors.upsert(ready_chunks, ready_vectors)
                    else:
                        vectors.reset()
                        vectors.add(ready_chunks, ready_vectors)
                except Exception as exc:  # noqa: BLE001
                    # Сборка не должна падать из-за хранилища векторов: лексический
                    # индекс уже готов, а векторы можно пересобрать отдельно.
                    log(f"  ! не удалось записать векторы в Chroma: {type(exc).__name__}")
                    log(f"    {str(exc)[:200]}")
                    log("    повторите: py ingest.py            (полная пересборка)")
                    log("    векторы сохранены в кеше, повторный запуск не будет их считать")

            reused_vectors = len(chunks) - len(todo)
            embedded_vectors = len(todo)
            cache.keep_only(chunk.id for chunk in chunks)
            if not cache.save():
                log("  ! кеш векторов не сохранён (сборка продолжает работу)")
            # Счётчик берём после сохранения кеша: при фолбэке на vectors.npz
            # он обновляется именно там, и старое значение вводило в заблуждение.
            vector_total = vectors.count() if vectors else 0
            if cache_path_is_npz := (vectors is not None and not getattr(vectors, "supports_where", True)):
                vector_total = max(vector_total, len(cache))
            if vectors is not None and getattr(vectors, "supports_where", True) is False:
                vector_total = len(cache)
            log(f"  в хранилище: {vector_total} векторов")
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
        "vectors": vector_total if "vector_total" in dir() else (vectors.count() if vectors else 0),
        "vectors_reused": reused_vectors,
        "vectors_embedded": embedded_vectors,
        "incremental": bool(args.incremental),
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
    if embedded_vectors or reused_vectors:
        log(f"  Векторов: посчитано {embedded_vectors} · из кеша {reused_vectors}")
    log(f"  Компания: {entities.company.get('name') or '—'}")
    log(f"  Индекс: {index_dir}")
    log("=" * 62)
    return 0


if __name__ == "__main__":
    sys.exit(main())
