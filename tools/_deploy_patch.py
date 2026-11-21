"""Хостинг: фронтенд на сайте, запросы — на локальный ПК.

Что делает патч:
1. API: необязательный токен доступа (API_TOKEN) и заголовок X-Api-Token.
2. Клиент: адрес API и токен читаются из window.__AGENT_API__ (config.js).
3. index.html подключает config.js — на хостинге правится только он.
"""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API = pathlib.Path("partner/api.py")
CONFIG = pathlib.Path("partner/config.py")
APPJS = pathlib.Path("partner/web/app.js")
INDEX = pathlib.Path("partner/web/index.html")
CONFIG_JS = pathlib.Path("partner/web/config.js")

CONFIG_JS_TEXT = """// Настройка связки «сайт на хостинге → агент на вашем ПК».
// На хостинге правится ТОЛЬКО этот файл.
//
// base  — публичный адрес туннеля до вашего ПК (без слэша в конце).
//         Пустая строка = тот же сервер (локальный запуск).
// token — значение API_TOKEN из .env на вашем ПК.
window.__AGENT_API__ = {
  base: "",
  token: "",
};
"""

CLIENT_HELPERS = """// --- связка с удалённым API -------------------------------------------
// Адрес и токен приходят из config.js: на хостинге лежит статика, а сам агент
// работает на вашем ПК и доступен через туннель.
const API_CFG = window.__AGENT_API__ || {};
const API_BASE = String(API_CFG.base || "").replace(/\\/+$/, "");
const API_TOKEN = String(API_CFG.token || "");

function apiUrl(path) {
  if (!path.startsWith("/api")) return path;
  return API_BASE ? `${API_BASE}${path}` : path;
}

function apiHeaders(extra) {
  const headers = { "Content-Type": "application/json", ...(extra || {}) };
  if (API_TOKEN) headers["X-Api-Token"] = API_TOKEN;
  return headers;
}
"""


def patch_api() -> None:
    text = API.read_text(encoding="utf-8")
    changed = []

    if "X-Api-Token" not in text:
        text = text.replace(
            "from fastapi import FastAPI, HTTPException, Query",
            "from fastapi import FastAPI, HTTPException, Query, Request",
        )
        anchor = "    def runtime() -> Runtime:"
        middleware = '''    # --- доступ по токену ------------------------------------------------
    @app.middleware("http")
    async def token_guard(request: Request, call_next):
        """Если задан API_TOKEN, /api/* закрыт заголовком X-Api-Token.

        Нужно, когда интерфейс лежит на хостинге, а агент доступен через
        публичный туннель: без токена любой мог бы жечь ваш ключ модели.
        """
        token = (settings.api_token or "").strip()
        path = request.url.path
        if token and path.startswith("/api/") and path != "/api/health":
            supplied = request.headers.get("x-api-token") or request.query_params.get("token", "")
            if supplied != token:
                return JSONResponse({"detail": "Неверный или отсутствующий токен"}, status_code=401)
        return await call_next(request)

'''
        text = text.replace(anchor, middleware + anchor, 1)
        if "JSONResponse" not in text.split("from fastapi.responses")[1].split("\n")[0]:
            text = text.replace(
                "from fastapi.responses import FileResponse, StreamingResponse",
                "from fastapi.responses import FileResponse, JSONResponse, StreamingResponse",
            )
        changed.append("middleware токена")

    API.write_text(text, encoding="utf-8")
    print("api:", ", ".join(changed) or "без изменений")


def patch_settings() -> None:
    text = CONFIG.read_text(encoding="utf-8")
    if "api_token" in text:
        print("config: api_token уже есть")
        return
    text = text.replace(
        '    chroma_subdir: str = "chroma"',
        '    chroma_subdir: str = "chroma"\n    api_token: str = ""',
    )
    text = text.replace(
        '            chroma_subdir=(os.environ.get("CHROMA_SUBDIR") or "chroma"),',
        '            chroma_subdir=(os.environ.get("CHROMA_SUBDIR") or "chroma"),\n'
        '            api_token=(os.environ.get("API_TOKEN") or ""),',
    )
    CONFIG.write_text(text, encoding="utf-8")
    print("config: добавлен api_token")


def patch_client() -> None:
    text = APPJS.read_text(encoding="utf-8")
    changed = []

    if "apiUrl(" not in text:
        text = text.replace("async function api(path, options = {}) {", CLIENT_HELPERS + "\nasync function api(path, options = {}) {", 1)
        text = text.replace(
            """  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });""",
            """  const res = await fetch(apiUrl(path), {
    ...options,
    headers: apiHeaders(options.headers),
  });""",
            1,
        )
        text = text.replace(
            """    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },""",
            """    const res = await fetch(apiUrl('/api/chat'), {
      method: 'POST',
      headers: apiHeaders(),""",
            1,
        )
        changed.append("клиент: apiUrl/apiHeaders")
    APPJS.write_text(text, encoding="utf-8")
    print("app.js:", ", ".join(changed) or "без изменений")


def patch_index() -> None:
    text = INDEX.read_text(encoding="utf-8")
    if "config.js" in text:
        print("index.html: config.js уже подключён")
        return
    text = text.replace(
        '<script src="/static/app.js',
        '<script src="/config.js"></script>\n<script src="/static/app.js',
        1,
    )
    INDEX.write_text(text, encoding="utf-8")
    print("index.html: подключён config.js")


def main() -> int:
    patch_settings()
    patch_api()
    patch_client()
    patch_index()
    if not CONFIG_JS.is_file():
        CONFIG_JS.write_text(CONFIG_JS_TEXT, encoding="utf-8")
        print("создан: partner/web/config.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
