"""/config.js отдаёт токен из настроек, а не пустой файл-заглушку."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("partner/api.py")

OLD = '''    @app.get("/config.js", include_in_schema=False)
    def web_config():
        """Настройка связки с удалённым API: на хостинге правится только этот файл."""
        path = WEB_DIR / "config.js"
        if not path.is_file():
            raise HTTPException(status_code=404, detail="config.js не найден")
        return FileResponse(
            path,
            media_type="application/javascript; charset=utf-8",
            headers={"Cache-Control": "no-store, max-age=0"},
        )'''

NEW = '''    @app.get("/config.js", include_in_schema=False)
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
        body = "window.__AGENT_API__ = " + json.dumps(payload, ensure_ascii=False) + ";\\n"
        return Response(
            body,
            media_type="application/javascript; charset=utf-8",
            headers={"Cache-Control": "no-store, max-age=0"},
        )'''

HEADERS_OLD = "from fastapi.responses import FileResponse, JSONResponse, StreamingResponse"
HEADERS_NEW = "from fastapi.responses import FileResponse, JSONResponse, Response, StreamingResponse"


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    if "payload = {\"base\": \"\", \"token\": settings.api_token or \"\"}" in text:
        print("уже отдаёт токен из настроек")
        return 0
    if OLD not in text:
        print("исходный обработчик не найден")
        return 1
    text = text.replace(OLD, NEW, 1)
    text = text.replace(HEADERS_OLD, HEADERS_NEW, 1)
    if "import json" not in text.split("from fastapi")[0]:
        text = text.replace("import logging", "import json\nimport logging", 1)
    PATH.write_text(text, encoding="utf-8")
    print("/config.js теперь отдаёт токен из настроек")
    return 0


if __name__ == "__main__":
    sys.exit(main())
