"""Запуск веб-чата Partner-Agent.

    python app.py                 # http://127.0.0.1:8001
    python app.py --port 8020     # другой порт
    python app.py --reload        # автоперезапуск при правках (dev)
    python app.py --ingest        # сначала пересобрать базу знаний

База знаний должна быть собрана хотя бы раз: `python ingest.py`.
"""

from __future__ import annotations

import argparse
import sys
import threading
import time
import webbrowser

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from partner import compat

compat.ensure_workable_tempdir()

from partner.config import Settings  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Веб-чат Partner-Agent")
    parser.add_argument("--host", default=None, help="адрес (по умолчанию 127.0.0.1)")
    parser.add_argument("--port", type=int, default=None, help="порт (по умолчанию 8001)")
    parser.add_argument("--reload", action="store_true", help="автоперезапуск (uvicorn --reload)")
    parser.add_argument("--ingest", action="store_true", help="пересобрать базу знаний перед запуском")
    parser.add_argument("--no-browser", action="store_true", help="не открывать браузер")
    return parser.parse_args(argv)


def _open_browser(url: str) -> None:
    def _open() -> None:
        time.sleep(1.2)
        try:
            webbrowser.open(url)
        except Exception:  # noqa: BLE001
            pass

    threading.Thread(target=_open, daemon=True).start()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    settings = Settings.load()
    if args.host:
        settings.host = args.host
    if args.port:
        settings.port = args.port

    if args.ingest or not (settings.index_dir / "chunks.json").exists():
        print("→ Собираю базу знаний …", flush=True)
        from ingest import main as ingest_main

        code = ingest_main([])
        if code != 0:
            return code

    url = f"http://{settings.host}:{settings.port}"
    print("=" * 66)
    print("  Partner-Agent — ИИ-ассистент по компании-партнёру")
    print("=" * 66)
    print(f"  Адрес     : {url}")
    print(f"  Компания  : {settings.company_name}")
    print(f"  Модель    : {settings.effective_model} ({settings.provider})")
    print(f"  Индекс    : {settings.index_dir}")
    print(f"  История   : {settings.db_path}")
    print("=" * 66, flush=True)

    if not args.no_browser:
        _open_browser(url)

    import uvicorn

    uvicorn.run(
        "partner.api:app",
        host=settings.host,
        port=settings.port,
        reload=args.reload,
        log_level="info",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
