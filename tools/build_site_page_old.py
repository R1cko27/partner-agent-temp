"""Вставляет чат в сохранённую страницу usergate.com и кладёт её в веб-папку."""

from __future__ import annotations

import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SOURCE = pathlib.Path("UserGate _ Безопасность корпоративных сетей и дата-центров.html")
TARGET = pathlib.Path("partner/web/site.html")

CHAT_CSS = """
<style id="ug-chat-style">
.ug-chat-launcher{position:fixed;right:24px;bottom:24px;z-index:9998;display:flex;align-items:center;gap:10px;
padding:14px 20px;border:0;border-radius:999px;background:linear-gradient(135deg,#0c89db,#3eb6e2);color:#fff;
font:600 15px/1 "Granate","Inter","Segoe UI",Arial,sans-serif;cursor:pointer;box-shadow:0 16px 40px rgba(12,137,219,.35)}
.ug-chat-launcher:hover{transform:translateY(-1px)}
.ug-chat-launcher__dot{width:9px;height:9px;border-radius:50%;background:#8ef0b0;box-shadow:0 0 0 4px rgba(142,240,176,.25)}
.ug-chat{position:fixed;inset:0;z-index:9999;display:none;align-items:center;justify-content:center;padding:24px;
background:rgba(20,32,44,.55);backdrop-filter:blur(6px)}
.ug-chat.is-open{display:flex}
.ug-chat__window{width:min(1180px,100%);height:min(880px,100%);background:#fff;border-radius:22px;overflow:hidden;
display:flex;flex-direction:column;box-shadow:0 40px 90px rgba(15,27,40,.4);transform:scale(.94) translateY(12px);
opacity:0;transition:transform .22s ease,opacity .22s ease}
.ug-chat.is-open .ug-chat__window{transform:scale(1) translateY(0);opacity:1}
.ug-chat__bar{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid rgba(37,56,74,.1)}
.ug-chat__title{font:700 15px "Granate","Inter",Arial,sans-serif;color:#25384a}
.ug-chat__hint{font:400 13px "Granate","Inter",Arial,sans-serif;color:rgba(37,56,74,.55)}
.ug-chat__close{margin-left:auto;border:0;background:rgba(37,56,74,.06);width:34px;height:34px;border-radius:50%;
font-size:18px;line-height:1;cursor:pointer;color:#25384a}
.ug-chat__close:hover{background:rgba(37,56,74,.12)}
.ug-chat__frame{flex:1;border:0;width:100%;background:#fff}
/* Пропавшие из сохранённой страницы картинки: прячем, логотип рисуем знаком сайта. */
img[src*="_files/"]{display:none!important}
.header-menu__logo{display:inline-block;min-width:120px;height:26px;
background:url("https://usergate.com/f/dist/media/favicons/favicon.svg") no-repeat left center/contain}

@media(max-width:600px){.ug-chat{padding:10px}.ug-chat__window{border-radius:16px}}
</style>
"""

CHAT_HTML = """
<button class="ug-chat-launcher" type="button" data-ug-chat aria-label="Открыть чат с ассистентом">
  <span class="ug-chat-launcher__dot"></span> Спросить ИИ
</button>

<div class="ug-chat" id="ugChat" role="dialog" aria-modal="true" aria-label="Чат с ассистентом">
  <div class="ug-chat__window">
    <div class="ug-chat__bar">
      <span class="ug-chat__title">Ассистент UserGate</span>
      <span class="ug-chat__hint">ответы по материалам компании, со ссылками на источники</span>
      <button class="ug-chat__close" type="button" data-ug-close aria-label="Закрыть чат">&times;</button>
    </div>
    <iframe class="ug-chat__frame" id="ugChatFrame" title="Чат с ассистентом UserGate" loading="lazy"></iframe>
  </div>
</div>

<script>
(function () {
  var overlay = document.getElementById('ugChat');
  var frame = document.getElementById('ugChatFrame');
  var loaded = false;
  function openChat() {
    if (!loaded) { frame.src = 'index.html'; loaded = true; }
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }
  function closeChat() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }
  Array.prototype.forEach.call(document.querySelectorAll('[data-ug-chat]'), function (node) {
    node.addEventListener('click', function (event) { event.preventDefault(); openChat(); });
  });
  overlay.addEventListener('click', function (event) { if (event.target === overlay) closeChat(); });
  overlay.querySelector('[data-ug-close]').addEventListener('click', closeChat);
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && overlay.classList.contains('is-open')) closeChat();
  });
})();
</script>
"""

MENU_ITEM = (
    '<li class="header-menu__menu-item">'
    '<a class="header-menu__menu-item-link" href="#" data-ug-chat>Чат с ИИ</a>'
    "</li>"
)


def main() -> int:
    if not SOURCE.is_file():
        print("нет исходной страницы:", SOURCE)
        return 1
    html = SOURCE.read_text(encoding="utf-8", errors="replace")

    # 1. Убираем ссылки на пропавшую папку _files: скрипты-трекеры и битые картинки.
    html = re.sub(r'<script[^>]*src="\./[^"]*_files/[^"]*"[^>]*>\s*</script>', "", html)
    # 1a. Стили сайта берём из уже скачанного бандла, а не из пропавшей папки.
    html = re.sub(
        r'<link[^>]+href="\./[^"]*_files/app\.[^"]*\.bundle\.css"[^>]*>',
        '<link rel="stylesheet" href="usergate/app.css">',
        html,
    )
    # 1b. Сторонний виджет-чат со страницы не нужен: у нас свой.
    html = re.sub(r'<link[^>]*widget\.css[^>]*>', "", html)
    # 1c. Картинки на сайте лежат по адресу /f/dist/asset/<hash>.<ext>.
    html = re.sub(
        r'\./UserGate _ Безопасность[^"]*_files/([0-9a-f]{8,}\.(?:svg|png|jpg|jpeg|webp|woff2?|ttf))',
        r'https://usergate.com/f/dist/asset/\1',
        html,
    )
    # 1d. Служебные iframe (капча) убираем.
    html = re.sub(r'<iframe[^>]*_files/[^"]*\.html[^>]*>\s*</iframe>', "", html)

    broken = len(re.findall(r'\./UserGate _ Безопасность[^"]*_files/', html))

    # 2. Пункт меню «Чат с ИИ» — первым в списке.
    marker = '<ul class="header-menu__menu">'
    if marker in html and "data-ug-chat" not in html:
        html = html.replace(marker, marker + MENU_ITEM, 1)

    # 3. Стили и виджет чата перед </body>.
    if 'id="ug-chat-style"' not in html:
        html = html.replace("</body>", CHAT_CSS + CHAT_HTML + "</body>", 1)

    TARGET.write_text(html, encoding="utf-8")
    print(f"страница записана: {TARGET} · {round(TARGET.stat().st_size/1024)} КБ")
    print(f"пункт меню добавлен: {'data-ug-chat' in html}")
    print(f"осталось ссылок на отсутствующую папку _files: {broken}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
