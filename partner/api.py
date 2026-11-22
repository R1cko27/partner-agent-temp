"""FastAPI-приложение Partner-Agent: чат по компании со стримингом и историей."""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterator, List, Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles

from . import compat  # noqa: F401  (патчи временных каталогов под песочницу)
from .agent import PartnerAgent
from .config import WEB_DIR, Settings, data_stamp
from .engine.db import ChatDB, make_title
from .domain.agent_profile import build_profile
from .domain.retriever import Retriever
from .engine.answers import AnswerCache
from .engine.embeddings import Embedder
from .engine.llm import DeepSeekClient, LLMError
from .engine.logbook import log_path, write_log
from .schemas import (
    ChatRequest,
    HealthOut,
    MessageOut,
    RetrieveRequest,
    SessionCreate,
    SessionDetail,
    SessionOut,
    SessionRename,
)

logger = logging.getLogger("partner.api")
SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


def _sse(payload: Dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"


class Runtime:
    """Всё, что живёт всё время работы приложения."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = ChatDB(settings.db_path)
        self.embedder: Optional[Embedder] = None
        self.retriever: Optional[Retriever] = None
        self.agent: Optional[PartnerAgent] = None
        self.profile: Any = None
        self.cache: Optional[AnswerCache] = None
        self.client: Optional[DeepSeekClient] = None
        self.started = False
        self.load_error: Optional[str] = None

    def load(self) -> None:
        index_dir = self.settings.index_dir
        if not (index_dir / "chunks.json").exists():
            raise RuntimeError("Индекс не найден. Соберать индекс: python ingest.py")

        if self.settings.use_dense:
            try:
                self.embedder = Embedder(
                    self.settings.embed_model,
                    cache_dir=self.settings.storage_dir / "models",
                )
                logger.info("Эмбеддинги: %s", self.embedder.describe())
            except Exception as exc:  # noqa: BLE001
                logger.warning("Эмбеддинги недоступны: %s", exc)
                self.embedder = None

        self.retriever = Retriever.load(
            index_dir,
            embedder=self.embedder,
            chroma_dir=self.settings.chroma_dir,
        )
        stats = self.retriever.stats()
        self.profile = build_profile(
            self.settings.data_dir,
            company_name=stats.get("company") or self.settings.company_name,
            limits={
                "max_tokens": self.settings.max_tokens,
                "fast_max_tokens": self.settings.fast_max_tokens,
                "local_max_tokens": self.settings.local_max_tokens,
                "max_steps": self.settings.max_steps,
            },
        )
        if self.profile.company_name:
            self.settings.company_name = self.profile.company_name

        if self.settings.llm_ready:
            try:
                self.client = DeepSeekClient(self.settings)
            except LLMError as exc:
                logger.warning("Модель недоступна: %s", exc)
                self.client = None

        self.cache = (
            AnswerCache(
                self.db,
                embedder=self.embedder,
                threshold=self.settings.answer_cache_threshold,
                # Только сборка индекса: правки файлов без пересборки не
                # должны обнулять кеш — индекс всё равно остаётся прежним.
                kb_stamp=f"{stats.get('built_at') or ''}",
                ttl_days=self.settings.answer_cache_ttl_days,
                max_entries=self.settings.answer_cache_max_entries,
            )
            if self.settings.answer_cache
            else None
        )
        if self.cache is not None:
            self.cache.prune()

        self.agent = PartnerAgent(
            self.retriever,
            self.settings,
            client=self.client,
            cache=self.cache,
            profile=self.profile,
        )
        self.started = True
        logger.info(
            "База знаний готова: %s фрагментов, продуктов %s, людей %s, FAQ %s",
            stats["chunks"],
            stats["products"],
            stats["people"],
            stats["faq"],
        )
        write_log(
            f"запуск сервера http://{self.settings.host}:{self.settings.port} · "
            f"провайдер {self.settings.provider} · модель {self.settings.effective_model} · "
            f"компания {self.settings.company_name}"
        )

    @property
    def mode(self) -> str:
        return "api" if self.client else "demo"


def create_app(settings: Optional[Settings] = None) -> FastAPI:
    settings = settings or Settings.load()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        runtime = Runtime(settings)
        try:
            runtime.load()
        except Exception as exc:  # noqa: BLE001
            logger.error("Не удалось загрузить базу знаний: %s", exc)
            runtime.load_error = str(exc)
        app.state.runtime = runtime
        yield
        if runtime.client:
            runtime.client.close()
        runtime.db.close()

    app = FastAPI(
        title="Partner-Agent",
        description="ИИ-ассистент по компании-партнёру: RAG по открытым источникам и материалам",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- доступ по токену ------------------------------------------------
    @app.middleware("http")
    async def token_guard(request: Request, call_next):
        """Если задан API_TOKEN, /api/* закрыт заголовком X-Api-Token.

        Нужно, когда интерфейс лежит на хостинге, а агент доступен через
        публичный туннель: без токена любой мог бы жечь ваш ключ модели.
        """
        token = (settings.api_token or "").strip()
        path = request.url.path
        # Preflight браузера не несёт заголовков: его обрабатывает CORS.
        if request.method == "OPTIONS":
            return await call_next(request)
        if token and path.startswith("/api/") and path != "/api/health":
            supplied = request.headers.get("x-api-token") or request.query_params.get("token", "")
            if supplied != token:
                return JSONResponse({"detail": "Неверный или отсутствующий токен"}, status_code=401)
        return await call_next(request)

    def runtime() -> Runtime:
        rt: Optional[Runtime] = getattr(app.state, "runtime", None)
        if rt is None or not rt.started:
            detail = getattr(rt, "load_error", None) if rt else None
            raise HTTPException(
                status_code=503,
                detail=detail or "База знаний не загружена. Выполните: python ingest.py",
            )
        return rt

    # --- статика и интерфейс -------------------------------------------
    if WEB_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")
    if (WEB_DIR / "usergate").is_dir():
        app.mount(
            "/usergate",
            StaticFiles(directory=str(WEB_DIR / "usergate")),
            name="usergate",
        )

    @app.get("/index.html", include_in_schema=False)
    def index_alias():
        """Тот же интерфейс: вторая страница открывает чат в iframe по index.html."""
        return index()

    @app.get("/", include_in_schema=False)
    def index():
        path = WEB_DIR / "index.html"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="partner/web/index.html не найден")
        return FileResponse(path, headers={"Cache-Control": "no-store, max-age=0"})

    @app.get("/config.js", include_in_schema=False)
    def web_config():
        """Настройка клиента: адрес API и токен.

        Если страница открыта с этого же сервера (локально или через туннель),
        отдаём токен из настроек — иначе клиент не сможет авторизоваться.
        Если рядом лежит свой config.js с заполненным base, он имеет приоритет.
        """
        path = WEB_DIR / "config.js"
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            has_custom = "REPLACE-ME" not in text and "base:" in text and 'base: ""' not in text
            if has_custom:
                return Response(
                    text,
                    media_type="application/javascript; charset=utf-8",
                    headers={"Cache-Control": "no-store, max-age=0"},
                )
        payload = {"base": "", "token": settings.api_token or ""}
        body = "window.__AGENT_API__ = " + json.dumps(payload, ensure_ascii=False) + ";\n"
        return Response(
            body,
            media_type="application/javascript; charset=utf-8",
            headers={"Cache-Control": "no-store, max-age=0"},
        )

    @app.get("/site.html", include_in_schema=False)
    def site_page():
        """Сохранённая главная usergate.com с нашим чатом в меню."""
        path = WEB_DIR / "site.html"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="partner/web/site.html не найден")
        return FileResponse(path, headers={"Cache-Control": "no-store, max-age=0"})

    @app.get("/usergate.html", include_in_schema=False)
    def usergate_page():
        """Вторая страница: структура и палитра usergate.com + наш чат."""
        path = WEB_DIR / "usergate.html"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="partner/web/usergate.html не найден")
        return FileResponse(path, headers={"Cache-Control": "no-store, max-age=0"})

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        path = WEB_DIR / "favicon.svg"
        if path.is_file():
            return FileResponse(path, media_type="image/svg+xml")
        raise HTTPException(status_code=404)

    # --- состояние ------------------------------------------------------
    @app.get("/api/health", response_model=HealthOut)
    def health() -> HealthOut:
        rt = runtime()
        stats = rt.retriever.stats()  # type: ignore[union-attr]
        db_stats = rt.db.stats()
        return HealthOut(
            ok=True,
            mode=rt.mode,
            provider=settings.provider,
            model=settings.effective_model if rt.client else "retrieval-only",
            thinking=bool(rt.client and rt.client.thinking_supported),
            chunks=stats["chunks"],
            vectors=stats.get("vectors", 0),
            products=stats.get("products", 0),
            people=stats.get("people", 0),
            faq=stats.get("faq", 0),
            news=stats.get("news", 0),
            company=stats.get("company", ""),
            embedding=stats.get("embedding", ""),
            built_at=str(stats.get("built_at") or ""),
            sessions=db_stats["sessions"],
            messages=db_stats["messages"],
        )

    @app.get("/api/agent/profile")
    def agent_profile() -> Dict[str, Any]:
        rt = runtime()
        if rt.profile is None:
            return {"company": settings.company_name, "branding": {}}
        return rt.profile.to_public()

    @app.get("/api/kb/stats")
    def kb_stats() -> Dict[str, Any]:
        rt = runtime()
        stats = dict(rt.retriever.stats())  # type: ignore[union-attr]
        stats["cache"] = rt.cache.stats() if rt.cache else {"entries": 0, "hits": 0}
        return stats

    @app.get("/api/kb/chunks")
    def kb_chunks(limit: int = Query(30, ge=1, le=200), kind: Optional[str] = None) -> Dict[str, Any]:
        rt = runtime()
        chunks = rt.retriever.chunks  # type: ignore[union-attr]
        if kind:
            chunks = [chunk for chunk in chunks if chunk.get("kind") == kind]
        return {
            "total": len(chunks),
            "items": [
                {
                    "id": chunk["id"],
                    "kind": chunk.get("kind"),
                    "title": chunk.get("title"),
                    "source": chunk.get("source"),
                    "text": str(chunk.get("text") or "")[:400],
                }
                for chunk in chunks[:limit]
            ],
        }

    @app.post("/api/retrieve")
    def retrieve(payload: RetrieveRequest) -> Dict[str, Any]:
        rt = runtime()
        hits = rt.retriever.search(payload.query, k=payload.top_k)  # type: ignore[union-attr]
        return {
            "query": payload.query,
            "hits": [hit.to_source() for hit in hits],
            "company": rt.retriever.company(),  # type: ignore[union-attr]
            "products": rt.retriever.find_product(payload.query, limit=3),  # type: ignore[union-attr]
            "people": rt.retriever.find_person(payload.query, limit=3),  # type: ignore[union-attr]
            "faq": rt.retriever.find_faq(payload.query, limit=3),  # type: ignore[union-attr]
        }

    # --- сессии ---------------------------------------------------------
    @app.get("/api/sessions", response_model=List[SessionOut])
    def list_sessions(limit: int = Query(100, ge=1, le=500)) -> List[SessionOut]:
        rt = runtime()
        return [SessionOut(**row) for row in rt.db.list_sessions(limit)]

    @app.post("/api/sessions", response_model=SessionOut)
    def create_session(payload: SessionCreate) -> SessionOut:
        rt = runtime()
        row = rt.db.create_session(title=payload.title, model=settings.effective_model)
        return SessionOut(**row)

    @app.get("/api/sessions/{session_id}", response_model=SessionDetail)
    def get_session(session_id: str) -> SessionDetail:
        rt = runtime()
        session = rt.db.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Чат не найден")
        messages = [MessageOut(**row) for row in rt.db.get_messages(session_id)]
        return SessionDetail(**session, messages=messages)

    @app.patch("/api/sessions/{session_id}", response_model=SessionOut)
    def rename_session(session_id: str, payload: SessionRename) -> SessionOut:
        rt = runtime()
        if not rt.db.rename_session(session_id, payload.title):
            raise HTTPException(status_code=404, detail="Чат не найден")
        return SessionOut(**rt.db.get_session(session_id))  # type: ignore[arg-type]

    @app.delete("/api/sessions/{session_id}")
    def delete_session(session_id: str) -> Dict[str, Any]:
        rt = runtime()
        if not rt.db.delete_session(session_id):
            raise HTTPException(status_code=404, detail="Чат не найден")
        return {"ok": True, "deleted": session_id}

    @app.delete("/api/cache")
    def clear_cache() -> Dict[str, Any]:
        rt = runtime()
        removed = rt.cache.clear() if rt.cache else 0
        return {"ok": True, "removed": removed}

    # --- чат ------------------------------------------------------------
    @app.post("/api/chat")
    def chat(payload: ChatRequest) -> StreamingResponse:
        rt = runtime()
        message = payload.message.strip()
        if not message:
            raise HTTPException(status_code=400, detail="Пустое сообщение")

        session = rt.db.get_session(payload.session_id) if payload.session_id else None
        created = False
        if session is None:
            session = rt.db.create_session(
                title=make_title(message), model=settings.effective_model
            )
            created = True
        session_id = session["id"]

        history = rt.db.history_for_llm(session_id)[-8:]
        rt.db.add_message(session_id, "user", message, hidden=payload.hidden)

        def event_stream() -> Iterator[str]:
            saved = False
            answer = ""
            reasoning = ""
            sources: List[Dict[str, Any]] = []
            tool_log: List[Dict[str, Any]] = []

            yield _sse(
                {
                    "type": "session",
                    "id": session_id,
                    "title": session["title"],
                    "created": created,
                }
            )

            try:
                assert rt.agent is not None
                # Ответы опроса уже содержат все параметры — не запускаем
                # полный цикл инструментов, отвечаем одним коротким вызовом.
                effective_mode = "direct" if payload.hidden else payload.mode
                for event in rt.agent.run(
                    message,
                    history=history,
                    show_notes=payload.show_notes,
                    use_cache=payload.use_cache,
                    mode=effective_mode,
                ):
                    if event.get("type") == "done":
                        answer = event.get("text", "")
                        reasoning = event.get("reasoning", "")
                        sources = event.get("sources", [])
                        tool_log = list(event.get("tool_calls", []) or [])
                        followups = event.get("followups") or []
                        if followups and not any(
                            call.get("name") == "offer_followups" for call in tool_log
                        ):
                            tool_log.append(
                                {
                                    "name": "offer_followups",
                                    "arguments": {"items": followups},
                                    "reason": "",
                                    "summary": f"варианты продолжения: {len(followups)}",
                                }
                            )
                        usage = event.get("usage_total") or event.get("usage") or {}
                        tokens = int(usage.get("total_tokens") or 0)
                        rt.db.add_message(
                            session_id,
                            "assistant",
                            answer,
                            reasoning=reasoning,
                            sources=sources,
                            attachments=event.get("attachments", []),
                            tool_calls=tool_log,
                            steps=int(event.get("steps") or 0),
                            tokens=tokens,
                            cached=bool(event.get("cached")),
                        )
                        saved = True
                    yield _sse(event)
            except GeneratorExit:
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("Ошибка в потоке чата")
                yield _sse({"type": "error", "message": f"Внутренняя ошибка: {exc}"})
            finally:
                if not saved and answer:
                    rt.db.add_message(
                        session_id,
                        "assistant",
                        answer,
                        reasoning=reasoning,
                        sources=sources,
                        tool_calls=tool_log,
                    )

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={**SSE_HEADERS, "X-Session-Id": session_id},
        )

    return app


app = create_app()
