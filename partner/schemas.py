"""Pydantic-схемы Partner-Agent."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Вопрос пользователя")
    session_id: Optional[str] = Field(None, description="ID чата; если нет — создаётся новый")
    show_notes: bool = Field(True, description="Разрешить короткие оговорки о базе")
    use_cache: bool = Field(True, description="Отдавать готовый ответ из кэша")
    mode: str = Field("thinking", description="thinking (с инструментами) или fast (сразу)")
    hidden: bool = Field(False, description="Служебное сообщение: не показывать в чате")


class SessionCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=120)


class SessionRename(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    reasoning: str = ""
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    hidden: bool = False
    steps: int = 0
    tokens: int = 0
    cached: bool = False
    created_at: str = ""


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str
    model: Optional[str] = None
    message_count: int = 0


class SessionDetail(SessionOut):
    messages: List[MessageOut] = Field(default_factory=list)


class HealthOut(BaseModel):
    ok: bool
    mode: str
    provider: str = ""
    model: str = ""
    thinking: bool = False
    chunks: int = 0
    vectors: int = 0
    products: int = 0
    people: int = 0
    faq: int = 0
    news: int = 0
    company: str = ""
    embedding: str = ""
    built_at: str = ""
    sessions: int = 0
    messages: int = 0


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(6, ge=1, le=20)
