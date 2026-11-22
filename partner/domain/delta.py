"""Инкрементальные документы поверх собранного индекса.

Идея: не пересобирать базу, а дописывать новые чанки в отдельный файл
`storage/index/delta/chunks.jsonl`. Векторы при этом кладутся в общую Chroma,
поэтому плотный поиск видит документ сразу, а BM25 по базе не пересчитывается —
для дельты строится маленький отдельный индекс.
"""

from __future__ import annotations

import json
import pathlib
import re
import time
from typing import Any, Dict, List

DELTA_DIR = "delta"
CHUNKS_FILE = "chunks.jsonl"
MANIFEST = "manifest.json"


def delta_dir(index_dir: pathlib.Path) -> pathlib.Path:
    path = pathlib.Path(index_dir) / DELTA_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_delta(index_dir: pathlib.Path) -> List[Dict[str, Any]]:
    """Читает добавленные чанки; битые строки пропускает."""
    path = delta_dir(index_dir) / CHUNKS_FILE
    if not path.is_file():
        return []
    items: List[Dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return items


def append_delta(index_dir: pathlib.Path, chunks: List[Dict[str, Any]]) -> int:
    """Дописывает чанки, не трогая существующие."""
    if not chunks:
        return 0
    path = delta_dir(index_dir) / CHUNKS_FILE
    existing = {str(item.get("id")) for item in load_delta(index_dir)}
    added = 0
    with path.open("a", encoding="utf-8") as handle:
        for chunk in chunks:
            chunk_id = str(chunk.get("id") or "")
            if not chunk_id or chunk_id in existing:
                continue
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            existing.add(chunk_id)
            added += 1
    return added


def _manifest_path(index_dir: pathlib.Path) -> pathlib.Path:
    return delta_dir(index_dir) / MANIFEST


def load_manifest(index_dir: pathlib.Path) -> Dict[str, Any]:
    path = _manifest_path(index_dir)
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_manifest(index_dir: pathlib.Path, manifest: Dict[str, Any]) -> None:
    _manifest_path(index_dir).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def document_key(source: str, text: str) -> str:
    """Отпечаток документа: одинаковый файл не индексируется дважды."""
    import hashlib

    digest = hashlib.sha1()
    digest.update(str(source).encode("utf-8"))
    digest.update(b"\0")
    digest.update(text.encode("utf-8"))
    return digest.hexdigest()


def remember_document(index_dir: pathlib.Path, source: str, key: str, chunks: int) -> None:
    manifest = load_manifest(index_dir)
    manifest[str(source)] = {
        "hash": key,
        "chunks": int(chunks),
        "added_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    save_manifest(index_dir, manifest)


def slug(value: str) -> str:
    text = re.sub(r"[^\w\-.]+", "-", str(value)).strip("-").lower()
    return text[:80] or "document"
