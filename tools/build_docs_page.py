"""Собирает третью страницу `partner/web/docs.html` из `template2.html`.

Стили страницы не переписываются: те же CSS-файлы подключаются с
docs.usergate.com по исходным именам. Меняются только ссылки на локальные
ассеты saved-страницы (их папки `_files` рядом нет), убираются скрипты и
добавляется виджет вопросов.

Запуск:
    python tools/build_docs_page.py
"""

from __future__ import annotations

import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCE = ROOT / "template2.html"
TARGET = ROOT / "partner" / "web" / "docs.html"
WIDGET_CSS = ROOT / "tools" / "page3_widget.css"
WIDGET_JS = ROOT / "tools" / "page3_widget.js"

DOCS_BASE = "https://docs.usergate.com"
SKIN = f"{DOCS_BASE}/client/skin"
ASSET_VERSION = "c8f98b33"
SELF_URL = (
    f"{DOCS_BASE}/politika-obnovleniya-programmnogo-obespecheniya-"
    "usergate-ngfw_3043.html"
)

# Имена из сохранённой страницы → реальные пути на портале документации.
CSS_MAP = {
    "common.css": "common.css",
    "common_table.css": "common_table.css",
    "common_view.css": "view_left/common_view.css",
    "default.css": "view_left/default/default.css",
    "box.css": "box.css",
    "form.css": "form.css",
    "tooltipster.bundle.min.css": "jquery/tooltipster/tooltipster.bundle.min.css",
    "tooltipster-sideTip-kbp.css": (
        "jquery/tooltipster/plugins/tooltipster/sideTip/themes/"
        "tooltipster-sideTip-kbp.css"
    ),
    "tooltipster-sideTip-kbp_error.css": (
        "jquery/tooltipster/plugins/tooltipster/sideTip/themes/"
        "tooltipster-sideTip-kbp_error.css"
    ),
    "tooltipster-sideTip-light.min.css": (
        "jquery/tooltipster/plugins/tooltipster/sideTip/themes/"
        "tooltipster-sideTip-light.min.css"
    ),
    "jquery.growl.css": "jquery/jquery.growl.css",
    "jquery-ui.css": "jquery-ui/smoothness/jquery-ui.css",
    "custom.css": "jquery-ui/smoothness/custom.css",
    "jquery.dropdown.css": "jquery/jquery.dropdown.css",
    "ezmodal.css": "jquery/ezmodal.css",
    "foundation.css": "foundation.css",
    "foundation_custom.css": "foundation_custom.css",
    "search2.css": "search2.css",
    "magnific-popup.css": "jquery/magnific-popup.css",
    "jquery.rating.css": "jquery/jquery.rating.css",
    "blue.css": "jquery/icheck/skins/square/blue.css",
    "ajax_tree.css": "ajax_tree.css",
}

IMAGE_MAP = {
    "x-mark.svg": "icons/x-mark.svg",
    "menu_category_expanded.svg": "icons/menu_category_expanded.svg",
    "menu_category_collapsed.svg": "icons/menu_category_collapsed.svg",
    "menu_entry.svg": "icons/menu_entry.svg",
    "help.svg": "icons/help.svg",
    "gear.gif": "icons/gear.gif",
    "indicator.svg": "ajax/indicator.svg",
}

WIDGET_HTML = """
<!-- Partner-Agent: предложение спросить об этой странице -->
<div id="paqRoot" class="paq">
  <button class="paq-q" id="paqQuestion" type="button" hidden
          aria-label="Задать вопрос об этой странице">
    <span class="paq-q__text" id="paqQuestionText"><span class="paq-q__run" id="paqQuestionRun"></span></span>
  </button>

  <button class="paq-bubble" id="paqBubble" type="button"
          aria-label="Открыть чат с ИИ-ассистентом" title="Спросить об этой странице">
    <span class="paq-bubble__icon" aria-hidden="true">
      <svg viewBox="0 0 24 24" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 11.5a8.4 8.4 0 0 1-8.5 8.3 9 9 0 0 1-3.8-.8L3 21l2-5.2a8.2 8.2 0 0 1-1-4A8.4 8.4 0 0 1 12.5 3 8.4 8.4 0 0 1 21 11.5Z"></path>
        <circle cx="8.5" cy="11.5" r=".9" fill="currentColor" stroke="none"></circle>
        <circle cx="12" cy="11.5" r=".9" fill="currentColor" stroke="none"></circle>
        <circle cx="15.5" cy="11.5" r=".9" fill="currentColor" stroke="none"></circle>
      </svg>
    </span>
  </button>
</div>

<div class="paq-chat" id="paqChat" role="dialog" aria-modal="true"
     aria-label="Чат с ИИ-ассистентом UserGate" aria-hidden="true">
  <div class="paq-chat__window">
    <div class="paq-chat__body">
      <div class="paq-chat__loader" id="paqLoader">
        <span class="paq-spinner" aria-hidden="true"></span>
        <span id="paqLoaderText">Открываю чат…</span>
      </div>
      <iframe class="paq-chat__frame" id="paqFrame"
              title="Чат с ИИ-ассистентом UserGate"></iframe>
    </div>
  </div>
</div>
"""


def _replace_css_link(match: re.Match[str]) -> str:
    name = match.group(1)
    path = CSS_MAP.get(name, name)
    return f'href="{SKIN}/{path}?v={ASSET_VERSION}"'


def _replace_image(match: re.Match[str]) -> str:
    name = match.group(1)
    if name == "captcha.php":
        return f'src="{DOCS_BASE}/captcha.php"'
    path = IMAGE_MAP.get(name, f"icons/{name}")
    return f'src="{DOCS_BASE}/client/images/{path}"'


def build() -> int:
    if not SOURCE.is_file():
        print("нет исходной страницы:", SOURCE)
        return 1
    for path in (WIDGET_CSS, WIDGET_JS):
        if not path.is_file():
            print("нет файла виджета:", path)
            return 1

    html = SOURCE.read_text(encoding="utf-8", errors="replace")

    # 1. Убираем сохранённые скрипты и аналитику: страница должна быть
    #    статичной, чтобы не тянуть несуществующую папку `_files`.
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.S | re.I)
    html = re.sub(
        r"<!--\s*Yandex\.Metrika counter\s*-->.*?<!--\s*/Yandex\.Metrika counter\s*-->",
        "",
        html,
        flags=re.S | re.I,
    )
    html = re.sub(
        r'<noscript><div><img src="https://mc\.yandex\.ru/watch/[^"]*"[^>]*></div></noscript>',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(r"\s+on(?:click|submit)=\"[^\"]*\"", "", html, flags=re.I)

    # 2. Возвращаем исходные стили портала вместо отсутствующих `_files`.
    html = re.sub(
        r'href="[^"]*?_files/([^"/]+\.css)"',
        _replace_css_link,
        html,
    )
    html = re.sub(
        r'src="[^"]*?_files/([^"/]+)"',
        _replace_image,
        html,
    )

    # Абсолютные пути внутри inline-стилей (шрифты FontAwesome и т. п.)
    # относятся к docs.usergate.com, а не к нашему серверу.
    html = html.replace('src="/client/', f'src="{DOCS_BASE}/client/')
    html = html.replace("url('/client/", f"url('{DOCS_BASE}/client/")
    html = html.replace('url("/client/', f'url("{DOCS_BASE}/client/')
    html = html.replace("url(/client/", f"url({DOCS_BASE}/client/")

    # Оглавление статьи в сохранённой странице ссылается на абсолютный URL
    # этой же статьи. Оставляем переходы внутри копии, а не на живой портал.
    html = html.replace(f'href="{SELF_URL}#', 'href="#')

    left_files = re.findall(r"_files/", html)
    if left_files:
        print("предупреждение: остались ссылки _files:", len(left_files))

    widget_css = WIDGET_CSS.read_text(encoding="utf-8")
    widget_js = WIDGET_JS.read_text(encoding="utf-8")
    if "</script" in widget_js.lower():
        print("ошибка: в JS виджета есть закрывающий тег script")
        return 1

    # 3. Стили виджета — отдельным блоком, не затрагивая стили статьи.
    if 'id="paq-style"' not in html:
        html = html.replace(
            "</head>",
            f'<style id="paq-style">\n{widget_css}\n</style>\n</head>',
            1,
        )

    # 4. Разметка и поведение виджета.
    if 'id="paqRoot"' not in html:
        injection = (
            WIDGET_HTML
            + '\n<script src="config.js"></script>\n<script>\n'
            + widget_js
            + "\n</script>\n"
        )
        html = html.replace("</body>", injection + "</body>", 1)

    TARGET.write_text(html, encoding="utf-8")
    size = TARGET.stat().st_size / 1024
    print(f"страница: {TARGET} · {size:.0f} КБ")
    print(
        "стили:",
        len(re.findall(r'https://docs\.usergate\.com/client/skin/', html)),
        "| осталось _files:",
        len(re.findall(r"_files/", html)),
        "| виджет:",
        'id="paqRoot"' in html,
    )
    return 0


if __name__ == "__main__":
    sys.exit(build())
