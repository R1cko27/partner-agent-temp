"""Хранилище истории чата на SQLite.

Схема:

    sessions(id, title, created_at, updated_at, model, message_count)
    messages(id, session_id, role, content, reasoning, sources, tool_calls,
             steps, tokens, created_at)

`reasoning` хранит видимую цепочку рассуждений агента (план + размышления
модели), `sources` — JSON со ссылками на чанки, `tool_calls` — JSON с вызовами
инструментов. Так историю можно восстановить в UI полностью, а не только
текстом ответа.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id            TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    model         TEXT,
    message_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    reasoning   TEXT NOT NULL DEFAULT '',
    sources     TEXT NOT NULL DEFAULT '[]',
    attachments TEXT NOT NULL DEFAULT '[]',
    tool_calls  TEXT NOT NULL DEFAULT '[]',
    hidden      INTEGER NOT NULL DEFAULT 0,
    steps       INTEGER NOT NULL DEFAULT 0,
    tokens      INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, id);
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC);

CREATE TABLE IF NOT EXISTS answer_cache (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    question    TEXT NOT NULL,
    normalized  TEXT NOT NULL,
    answer      TEXT NOT NULL,
    reasoning   TEXT NOT NULL DEFAULT '',
    sources     TEXT NOT NULL DEFAULT '[]',
    attachments TEXT NOT NULL DEFAULT '[]',
    tool_calls  TEXT NOT NULL DEFAULT '[]',
    embedding   TEXT NOT NULL DEFAULT '[]',
    entities    TEXT NOT NULL DEFAULT '[]',
    show_notes  INTEGER NOT NULL DEFAULT 1,
    kb_stamp    TEXT NOT NULL DEFAULT '',
    lang        TEXT NOT NULL DEFAULT '',
    model       TEXT NOT NULL DEFAULT '',
    tokens      INTEGER NOT NULL DEFAULT 0,
    hits        INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL,
    last_hit_at TEXT,
    UNIQUE(normalized, show_notes, kb_stamp)
);

CREATE INDEX IF NOT EXISTS idx_answer_cache_key
    ON answer_cache(show_notes, kb_stamp);

CREATE TABLE IF NOT EXISTS aliases (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    alias        TEXT NOT NULL,
    normalized   TEXT NOT NULL UNIQUE,
    target_type  TEXT NOT NULL,
    target_key   TEXT NOT NULL,
    target_title TEXT NOT NULL DEFAULT '',
    source       TEXT NOT NULL DEFAULT 'user',
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
"""


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_title(text: str, limit: int = 64) -> str:
    """Заголовок чата из первого сообщения — как в ChatGPT/DeepSeek."""
    clean = " ".join((text or "").split())
    if not clean:
        return "Новый чат"
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


class ChatDB:
    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.executescript(SCHEMA)
            self._migrate()
            self._conn.commit()

    def _migrate(self) -> None:
        """Досоздаёт колонки, появившиеся в новых версиях (старые БД не теряются)."""
        columns = {
            row["name"]
            for row in self._conn.execute("PRAGMA table_info(messages)").fetchall()
        }
        if "attachments" not in columns:
            self._conn.execute(
                "ALTER TABLE messages ADD COLUMN attachments TEXT NOT NULL DEFAULT '[]'"
            )
        if "cached" not in columns:
            self._conn.execute(
                "ALTER TABLE messages ADD COLUMN cached INTEGER NOT NULL DEFAULT 0"
            )
        if "hidden" not in columns:
            self._conn.execute(
                "ALTER TABLE messages ADD COLUMN hidden INTEGER NOT NULL DEFAULT 0"
            )

        cache_columns = {
            row["name"]
            for row in self._conn.execute("PRAGMA table_info(answer_cache)").fetchall()
        }
        if cache_columns and "lang" not in cache_columns:
            self._conn.execute(
                "ALTER TABLE answer_cache ADD COLUMN lang TEXT NOT NULL DEFAULT ''"
            )

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # --- сессии ---------------------------------------------------------
    def create_session(self, title: Optional[str] = None, model: Optional[str] = None) -> Dict[str, Any]:
        session_id = uuid.uuid4().hex[:12]
        now = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO sessions (id, title, created_at, updated_at, model, message_count) "
                "VALUES (?, ?, ?, ?, ?, 0)",
                (session_id, title or "Новый чат", now, now, model),
            )
            self._conn.commit()
        return self.get_session(session_id)  # type: ignore[return-value]

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
        return dict(row) if row else None

    def list_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM sessions ORDER BY updated_at DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]

    def rename_session(self, session_id: str, title: str) -> bool:
        title = " ".join((title or "").split())[:120] or "Новый чат"
        with self._lock:
            cursor = self._conn.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title, utcnow(), session_id),
            )
            self._conn.commit()
        return cursor.rowcount > 0

    def delete_session(self, session_id: str) -> bool:
        with self._lock:
            self._conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cursor = self._conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            self._conn.commit()
        return cursor.rowcount > 0

    # --- сообщения ------------------------------------------------------
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        *,
        reasoning: str = "",
        sources: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        steps: int = 0,
        tokens: int = 0,
        cached: bool = False,
        hidden: bool = False,
    ) -> Dict[str, Any]:
        now = utcnow()
        with self._lock:
            cursor = self._conn.execute(
                "INSERT INTO messages "
                "(session_id, role, content, reasoning, sources, attachments, tool_calls, hidden, steps, tokens, cached, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    session_id,
                    role,
                    content,
                    reasoning,
                    json.dumps(sources or [], ensure_ascii=False),
                    json.dumps(attachments or [], ensure_ascii=False),
                    json.dumps(tool_calls or [], ensure_ascii=False),
                    1 if hidden else 0,
                    steps,
                    tokens,
                    1 if cached else 0,
                    now,
                ),
            )
            self._conn.execute(
                "UPDATE sessions SET updated_at = ?, message_count = message_count + 1 WHERE id = ?",
                (now, session_id),
            )
            self._conn.commit()
            message_id = cursor.lastrowid

        return {
            "id": message_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "reasoning": reasoning,
            "sources": sources or [],
            "attachments": attachments or [],
            "tool_calls": tool_calls or [],
            "hidden": bool(hidden),
            "steps": steps,
            "tokens": tokens,
            "cached": bool(cached),
            "created_at": now,
        }

    def get_messages(self, session_id: str, limit: int = 200) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [self._row_to_message(row) for row in rows]

    def history_for_llm(self, session_id: str, limit: int = 8) -> List[Dict[str, str]]:
        """Последние реплики в формате сообщений LLM (без reasoning)."""
        messages = self.get_messages(session_id)
        tail = messages[-limit:] if limit else messages
        return [
            {"role": item["role"], "content": item["content"]}
            for item in tail
            if item["role"] in ("user", "assistant") and item["content"]
        ]

    @staticmethod
    def _row_to_message(row: sqlite3.Row) -> Dict[str, Any]:
        data = dict(row)
        for key in ("sources", "tool_calls", "attachments"):
            try:
                data[key] = json.loads(data.get(key) or "[]")
            except json.JSONDecodeError:
                data[key] = []
        return data

    # --- кэш ответов ----------------------------------------------------
    def cache_candidates(
        self, show_notes: bool, kb_stamp: str, min_created: str = "", lang: str = ""
    ) -> List[Dict[str, Any]]:
        query = (
            "SELECT id, question, normalized, answer, reasoning, sources, attachments, "
            "tool_calls, embedding, entities, show_notes, kb_stamp, lang, model, tokens, hits, created_at "
            "FROM answer_cache WHERE show_notes = ? AND kb_stamp = ?"
        )
        params: List[Any] = [1 if show_notes else 0, kb_stamp]
        if min_created:
            query += " AND created_at >= ?"
            params.append(min_created)
        if lang:
            query += " AND lang = ?"
            params.append(lang)
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        result: List[Dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            for key in ("sources", "attachments", "tool_calls", "embedding", "entities"):
                try:
                    item[key] = json.loads(item.get(key) or "[]")
                except json.JSONDecodeError:
                    item[key] = []
            result.append(item)
        return result

    def cache_store(
        self,
        *,
        question: str,
        normalized: str,
        answer: str,
        reasoning: str = "",
        sources: Optional[List[Dict[str, Any]]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        embedding: Optional[List[float]] = None,
        entities: Optional[List[str]] = None,
        show_notes: bool = True,
        kb_stamp: str = "",
        lang: str = "",
        model: str = "",
        tokens: int = 0,
    ) -> int:
        now = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO answer_cache "
                "(question, normalized, answer, reasoning, sources, attachments, tool_calls, "
                "embedding, entities, show_notes, kb_stamp, lang, model, tokens, hits, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?) "
                "ON CONFLICT(normalized, show_notes, kb_stamp) DO UPDATE SET "
                "question = excluded.question, answer = excluded.answer, "
                "reasoning = excluded.reasoning, sources = excluded.sources, "
                "attachments = excluded.attachments, tool_calls = excluded.tool_calls, "
                "embedding = excluded.embedding, entities = excluded.entities, "
                "lang = excluded.lang, "
                "model = excluded.model, tokens = excluded.tokens, created_at = excluded.created_at",
                (
                    question,
                    normalized,
                    answer,
                    reasoning,
                    json.dumps(sources or [], ensure_ascii=False),
                    json.dumps(attachments or [], ensure_ascii=False),
                    json.dumps(tool_calls or [], ensure_ascii=False),
                    json.dumps(embedding or []),
                    json.dumps(entities or [], ensure_ascii=False),
                    1 if show_notes else 0,
                    kb_stamp,
                    lang,
                    model,
                    tokens,
                    now,
                ),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT id FROM answer_cache WHERE normalized = ? AND show_notes = ? AND kb_stamp = ?",
                (normalized, 1 if show_notes else 0, kb_stamp),
            ).fetchone()
        return int(row["id"]) if row else 0

    def cache_prune(self, min_created: str = "", max_entries: int = 0) -> int:
        """Удаляет просроченные ответы и лишние сверх лимита (сначала старые)."""
        removed = 0
        with self._lock:
            if min_created:
                removed += int(
                    self._conn.execute(
                        "DELETE FROM answer_cache WHERE created_at < ?", (min_created,)
                    ).rowcount or 0
                )
            if max_entries:
                total = int(self._conn.execute("SELECT COUNT(*) FROM answer_cache").fetchone()[0])
                excess = total - max_entries
                if excess > 0:
                    removed += int(
                        self._conn.execute(
                            "DELETE FROM answer_cache WHERE id IN ("
                            "SELECT id FROM answer_cache ORDER BY created_at ASC, hits ASC LIMIT ?"
                            ")",
                            (excess,),
                        ).rowcount or 0
                    )
            self._conn.commit()
        return removed

    def cache_touch(self, entry_id: int) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE answer_cache SET hits = hits + 1, last_hit_at = ? WHERE id = ?",
                (utcnow(), entry_id),
            )
            self._conn.commit()

    def cache_stats(self) -> Dict[str, int]:
        with self._lock:
            row = self._conn.execute(
                "SELECT COUNT(*) AS entries, COALESCE(SUM(hits), 0) AS hits FROM answer_cache"
            ).fetchone()
        return {"entries": int(row["entries"]), "hits": int(row["hits"])}

    def cache_clear(self) -> int:
        with self._lock:
            cursor = self._conn.execute("DELETE FROM answer_cache")
            self._conn.commit()
        return int(cursor.rowcount or 0)

    # --- алиасы (сленг) --------------------------------------------------
    def alias_all(self) -> List[Dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT alias, normalized, target_type, target_key, target_title, source "
                "FROM aliases ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    def alias_upsert(
        self,
        alias: str,
        normalized: str,
        target_type: str,
        target_key: str,
        target_title: str = "",
        source: str = "user",
    ) -> None:
        now = utcnow()
        with self._lock:
            self._conn.execute(
                "INSERT INTO aliases "
                "(alias, normalized, target_type, target_key, target_title, source, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(normalized) DO UPDATE SET "
                "alias = excluded.alias, target_type = excluded.target_type, "
                "target_key = excluded.target_key, target_title = excluded.target_title, "
                "source = excluded.source, updated_at = excluded.updated_at",
                (alias, normalized, target_type, target_key, target_title, source, now, now),
            )
            self._conn.commit()

    def alias_delete(self, normalized: str) -> bool:
        with self._lock:
            cursor = self._conn.execute("DELETE FROM aliases WHERE normalized = ?", (normalized,))
            self._conn.commit()
        return cursor.rowcount > 0

    def alias_prune(self, min_updated: str) -> int:
        """Забывает выученный сленг, который давно не подтверждали."""
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM aliases WHERE source != 'seed' AND updated_at < ?",
                (min_updated,),
            )
            self._conn.commit()
        return int(cursor.rowcount or 0)

    def alias_stats(self) -> Dict[str, int]:
        with self._lock:
            total = self._conn.execute("SELECT COUNT(*) FROM aliases").fetchone()[0]
            learned = self._conn.execute(
                "SELECT COUNT(*) FROM aliases WHERE source != 'seed'"
            ).fetchone()[0]
        return {"total": int(total), "learned": int(learned)}

    # --- статистика -----------------------------------------------------
    def stats(self) -> Dict[str, int]:
        with self._lock:
            sessions = self._conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            messages = self._conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
        return {"sessions": int(sessions), "messages": int(messages)}
