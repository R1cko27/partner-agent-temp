"""Пополнение базы через сайт: загрузка файлов и ссылок без пересборки."""

from __future__ import annotations

import base64
import importlib.util
import pathlib
import sys
import tempfile
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from .config import Settings
from .domain import delta

router = APIRouter(prefix="/api/studio", tags=["studio"])
ROOT = pathlib.Path(__file__).resolve().parent.parent


_ADD_DOCS = None


def _add_docs():
    global _ADD_DOCS
    if _ADD_DOCS is not None:
        return _ADD_DOCS
    path = ROOT / "tools" / "add_docs.py"
    spec = importlib.util.spec_from_file_location("add_docs", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    _ADD_DOCS = module
    return module






def _chunk_previews(source: str, limit: int = 8) -> dict:
    """Первые строки добавленных фрагментов: что именно попало в базу."""
    settings = Settings.load()
    items = []
    total = 0
    for chunk in delta.load_delta(settings.index_dir):
        if str(chunk.get("source")) != source:
            continue
        total += 1
        if len(items) >= limit:
            continue
        text = " ".join(str(chunk.get("text") or "").split())
        items.append({"n": total, "text": text[:140]})
    return {"total": total, "items": items}


def _chunks_of(source: str) -> int:
    settings = Settings.load()
    info = delta.load_manifest(settings.index_dir).get(source) or {}
    return int(info.get("chunks") or 0)


def _fail(detail: str) -> None:
    raise HTTPException(status_code=400, detail=detail)


class UploadIn(BaseModel):
    name: str
    content_base64: str


class UrlIn(BaseModel):
    url: str


@router.post("/reload")
def reload_index(request: Request) -> Dict[str, Any]:
    """Перечитывает дельту без перезапуска сервера."""
    runtime = getattr(request.app.state, "runtime", None)
    if runtime is None:
        raise HTTPException(status_code=503, detail="Приложение не загружено")
    runtime.load()
    delta_count = len(delta.load_delta(runtime.settings.index_dir))
    return {"ok": True, "chunks": len(runtime.retriever.chunks), "delta": delta_count}


@router.get("/documents")
def documents() -> Dict[str, Any]:
    settings = Settings.load()
    manifest = delta.load_manifest(settings.index_dir)
    items = [
        {"source": source, "chunks": info.get("chunks", 0), "added_at": info.get("added_at", "")}
        for source, info in sorted(manifest.items())
    ]
    return {"items": items, "total_chunks": sum(item["chunks"] for item in items)}


@router.post("/upload")
def upload(payload: UploadIn) -> Dict[str, Any]:
    name = pathlib.Path(payload.name).name
    suffix = pathlib.Path(name).suffix.lower()
    if suffix not in {".pdf", ".txt", ".md"}:
        raise HTTPException(status_code=400, detail="Поддерживаются PDF, TXT и MD")
    try:
        raw = base64.b64decode(payload.content_base64)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Файл повреждён")
    if len(raw) > 40 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Файл больше 40 МБ")
    target = pathlib.Path(tempfile.gettempdir()) / f"studio-{name}"
    target.write_bytes(raw)
    module = _add_docs()
    before = _chunks_of(name)
    try:
        code = module.main(["--file", str(target), "--as", name])
    except Exception as exc:  # noqa: BLE001
        _fail(f"Ошибка разбора файла: {exc}")
    finally:
        target.unlink(missing_ok=True)
    if code != 0:
        _fail("Не удалось добавить документ")
    after = _chunks_of(name)
    return {"ok": True, "source": name, "chunks": after, "updated": before > 0, "added": max(0, after - before), "previews": _chunk_previews(name)}


@router.post("/url")
def add_url(payload: UrlIn) -> Dict[str, Any]:
    url = payload.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Нужна ссылка http(s)")
    module = _add_docs()
    before = _chunks_of(url)
    try:
        code = module.main(["--url", url])
    except Exception as exc:  # noqa: BLE001
        _fail(f"Ошибка чтения страницы: {exc}")
    if code != 0:
        _fail("Не удалось прочитать страницу")
    after = _chunks_of(url)
    return {"ok": True, "url": url, "source": url, "chunks": after, "updated": before > 0, "added": max(0, after - before), "previews": _chunk_previews(url)}


@router.delete("/documents")
def delete(source: str) -> Dict[str, Any]:
    settings = Settings.load()
    path = delta.delta_dir(settings.index_dir) / delta.CHUNKS_FILE
    if not path.is_file():
        return {"ok": True, "removed": 0}
    kept: List[str] = []
    removed_items: List[Dict[str, Any]] = []
    removed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = __import__("json").loads(line)
        except Exception:  # noqa: BLE001
            continue
        if str(item.get("source")) == source:
            removed += 1
            removed_items.append(item)
            continue
        kept.append(line)
    path.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    # Векторы тоже удаляем: иначе удалённый документ продолжит находиться поиском.
    removed_ids = [
        str(item.get("id"))
        for item in removed_items
        if item.get("id")
    ]
    if removed_ids:
        try:
            from .engine.vectorstore import COLLECTION, open_vector_store

            store = open_vector_store(settings.chroma_dir, COLLECTION, prefer_chroma=True)
            if store is not None and hasattr(store, "delete_ids"):
                store.delete_ids(removed_ids)
        except Exception:  # noqa: BLE001 - Chroma может быть недоступна
            pass
    manifest = delta.load_manifest(settings.index_dir)
    manifest.pop(source, None)
    delta.save_manifest(settings.index_dir, manifest)
    return {"ok": True, "removed": removed}

class TextIn(BaseModel):
    name: str
    text: str


@router.post("/text")
def add_text(payload: TextIn) -> Dict[str, Any]:
    """Добавить текст вручную: сохраняем как .md и встраиваем."""
    text = (payload.text or "").strip()
    if len(text) < 40:
        raise HTTPException(status_code=400, detail="Текст слишком короткий")
    name = pathlib.Path(payload.name or "studio-text.md").name
    if not name.lower().endswith(".md"):
        name = name + ".md"
    target = pathlib.Path(tempfile.gettempdir()) / f"studio-{name}"
    target.write_text("# " + name[:-3] + "\n\n" + text + "\n", encoding="utf-8")
    module = _add_docs()
    before = _chunks_of(name)
    try:
        code = module.main(["--file", str(target), "--as", name])
    except Exception as exc:  # noqa: BLE001
        _fail(f"Ошибка разбора текста: {exc}")
    finally:
        target.unlink(missing_ok=True)
    if code != 0:
        _fail("Не удалось добавить текст")
    after = _chunks_of(name)
    return {"ok": True, "source": name, "chunks": after, "updated": before > 0, "added": max(0, after - before), "previews": _chunk_previews(name)}

