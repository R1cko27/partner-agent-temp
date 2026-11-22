"""Собирает автономный набор файлов для загрузки на сайт.

    python tools/build_host_bundle.py

Результат в `deploy/host/` — обычная статика без сервера:
    index.html  app.js  app.css  config.js  favicon.svg
    site.html   docs.html

Все пути относительные, поэтому папку можно положить как в корень сайта,
так и в любой подкаталог (`example.com/ai/`). Запросы к агенту идут на адрес
из `config.js` — то есть на туннель до вашего ПК.
"""

from __future__ import annotations

import io
import pathlib
import re
import shutil
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB = ROOT / "partner" / "web"
OUT = ROOT / "deploy" / "host"

CONFIG_TEMPLATE = """// Адрес агента (туннель до вашего ПК) и токен доступа.
// Этот файл единственный, который нужно править после загрузки на сайт.
//
// Пример: base: "https://agent-vashe-imya.trycloudflare.com"
// Слэш на конце не нужен. Если оставить пустым — запросы пойдут на этот же сайт
// (годится, только если статика и агент на одном сервере).
window.__AGENT_API__ = {
  base: "https://REPLACE-ME.trycloudflare.com",
  token: "REPLACE-ME-TOKEN",
};
"""


def main() -> int:
    if not WEB.is_dir():
        print("нет папки", WEB)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)

    # 1. Вторая страница с импортированными стилями сайта
    try:
        shutil.copy2(WEB / "usergate.html", OUT / "usergate.html")
    except FileNotFoundError:
        pass
    shutil.copy2(WEB / "site.html", OUT / "site.html")
    if (WEB / "docs.html").is_file():
        shutil.copy2(WEB / "docs.html", OUT / "docs.html")
        print("скопирована: docs.html (третья страница с виджетом)")
    target_dir = OUT / "usergate"
    target_dir.mkdir(parents=True, exist_ok=True)
    if (WEB / "usergate").is_dir():
        for item in (WEB / "usergate").iterdir():
            if item.is_file() and not item.name.startswith("_"):
                shutil.copy2(item, target_dir / item.name)
    print("скопирована: usergate.html + usergate/")

    # 2. Статика как есть
    for name in ("app.js", "app.css", "favicon.svg", "favicon-96x96.png", "studio.html"):
        source = WEB / name
        if not source.is_file():
            print("пропущен (нет файла):", name)
            continue
        shutil.copy2(source, OUT / name)
        print("скопирован:", name)

    # 2. index.html с относительными путями
    index = (WEB / "index.html").read_text(encoding="utf-8")
    index = re.sub(r'href="/static/([^"?]+)(\?[^"]*)?"', r'href="\1"', index)
    index = re.sub(r'src="/static/([^"?]+)(\?[^"]*)?"', r'src="\1"', index)
    index = index.replace('src="/config.js"', 'src="config.js"')
    # на всякий случай: любые оставшиеся абсолютные /static/
    index = index.replace('"/static/', '"./')
    (OUT / "index.html").write_text(index, encoding="utf-8")
    print("собран: index.html (относительные пути)")

    # 3. config.js — шаблон для правки на хостинге
    config = OUT / "config.js"
    if config.is_file():
        print("config.js оставлен без изменений")
    else:
        config.write_text(CONFIG_TEMPLATE, encoding="utf-8")
        print("создан: config.js (шаблон)")

    # 4. Короткая инструкция рядом
    (OUT / "КАК-ЗАГРУЗИТЬ.txt").write_text(
        "1. Загрузите всю папку на сайт: например в /ai/\n"
        "2. Откройте config.js и укажите base (адрес туннеля) и token\n"
        "3. Откройте страницу https://ваш-сайт/ai/\n"
        "4. На ПК должны быть запущены: py app.py и туннель\n",
        encoding="utf-8",
    )

    total = sum(item.stat().st_size for item in OUT.iterdir() if item.is_file())
    print(f"\nпапка: {OUT.relative_to(ROOT)} · файлов: {len([i for i in OUT.iterdir() if i.is_file()])}"
          f" · всего {total / 1024:.0f} КБ")
    for item in sorted(OUT.iterdir()):
        if item.is_file():
            print(f"  {item.name:20} {item.stat().st_size / 1024:7.1f} КБ")
    return 0


if __name__ == "__main__":
    sys.exit(main())
