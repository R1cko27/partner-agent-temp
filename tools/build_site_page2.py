"""Собирает страницу usergate.com с чатом: панель запроса + полноэкранный чат."""

from __future__ import annotations

import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SOURCE = pathlib.Path("UserGate _ Безопасность корпоративных сетей и дата-центров.html")
TARGET = pathlib.Path("partner/web/site.html")
CSS_REMOTE = "https://usergate.com/f/dist/app.06e30aaf9470fae2ad91.bundle.css"

STYLE = """
<style id="ug-chat-style">
.ug-ask{padding:26px 0 8px;background:#fff}
.ug-ask__card{position:relative;overflow:hidden;border-radius:32px;padding:34px 38px 30px;color:#fff;
background:linear-gradient(120deg,#1f3bff 0%,#2f5bff 45%,#4a7bff 100%);
box-shadow:0 24px 60px rgba(31,59,255,.25)}
.ug-ask__card:after{content:"";position:absolute;right:-60px;top:-80px;width:420px;height:420px;border-radius:50%;
background:radial-gradient(circle at 30% 30%,rgba(255,255,255,.18),transparent 60%)}
.ug-ask__title{margin:0 0 8px;font:700 clamp(20px,2.2vw,28px)/1.2 "Granate","Inter",Arial,sans-serif}
.ug-ask__sub{margin:0 0 22px;font:400 16px/1.5 "Granate","Inter",Arial,sans-serif;opacity:.9;max-width:640px}
.ug-ask__chips{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:18px;position:relative;z-index:1}
.ug-ask__chip{border:0;border-radius:999px;padding:11px 18px;font:500 15px "Granate","Inter",Arial,sans-serif;
color:#fff;background:rgba(255,255,255,.16);cursor:pointer;transition:background .15s ease}
.ug-ask__chip:hover{background:rgba(255,255,255,.28)}
.ug-ask__form{display:flex;align-items:center;gap:10px;background:#fff;border-radius:18px;padding:10px 12px 10px 18px;
position:relative;z-index:1;box-shadow:0 12px 30px rgba(12,20,60,.18)}
.ug-ask__input{flex:1;border:0;outline:0;font:400 17px "Granate","Inter",Arial,sans-serif;color:#25384a;background:transparent}
.ug-ask__input::placeholder{color:#8a97a8}
.ug-ask__send{width:46px;height:46px;border:0;border-radius:14px;cursor:pointer;display:grid;place-items:center;
background:rgba(31,59,255,.08);color:#2f4bff;font-size:20px}
.ug-ask__send:hover{background:rgba(31,59,255,.16)}
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
.ug-chat__frame{flex:1;border:0;width:100%;background:#fff}
img[src*="_files/"]{display:none!important}
.header-menu__logo{display:inline-block;min-width:120px;height:26px;
background:url("https://usergate.com/f/dist/media/favicons/favicon.svg") no-repeat left center/contain}
@media(max-width:600px){.ug-ask__card{padding:24px 20px}.ug-chat{padding:10px}.ug-chat__window{border-radius:16px}}
</style>
"""

PANEL = """
<section class="ug-ask" id="ugAsk">
  <div class="ug-ask__card">
    <h2 class="ug-ask__title">Спросите ИИ-ассистента о продуктах UserGate</h2>
    <p class="ug-ask__sub">Ответы по документации, карточкам продуктов и FAQ — со ссылками на источники.</p>
    <div class="ug-ask__chips">
      <button class="ug-ask__chip" type="button" data-ug-ask="Чем NGFW отличается от WAF?">Чем NGFW отличается от WAF?</button>
      <button class="ug-ask__chip" type="button" data-ug-ask="Какие сертификаты ФСТЭК есть у продуктов?">Сертификаты ФСТЭК</button>
      <button class="ug-ask__chip" type="button" data-ug-ask="Какие аппаратные платформы поддерживаются?">Аппаратные платформы</button>
      <button class="ug-ask__chip" type="button" data-ug-ask="Что входит в каталог курсов и экзаменов Академии?">Курсы Академии</button>
    </div>
    <form class="ug-ask__form" id="ugAskForm">
      <input class="ug-ask__input" id="ugAskInput" type="text" placeholder="Введите запрос…" autocomplete="off" />
      <button class="ug-ask__send" type="submit" title="Отправить" aria-label="Отправить">&#10148;</button>
    </form>
  </div>
</section>
"""

OVERLAY = """
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
  var input = document.getElementById('ugAskInput');
  var loaded = false;
  var pending = '';

  function flush() {
    if (!pending) return;
    try {
      frame.contentWindow.postMessage({ type: 'partner-agent-ask', text: pending }, '*');
      pending = '';
    } catch (error) { /* iframe ещё не готов */ }
  }

  function openChat(question) {
    if (question) pending = question;
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
    if (!loaded) {
      loaded = true;
      frame.src = 'index.html';
      frame.addEventListener('load', flush);
    } else {
      flush();
    }
  }

  function closeChat() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  var menuLink = document.querySelector('.header-menu__menu-item-link[data-ug-chat]');
  if (menuLink) {
    menuLink.addEventListener('click', function (event) { event.preventDefault(); openChat(''); });
  }

  Array.prototype.forEach.call(document.querySelectorAll('[data-ug-ask]'), function (node) {
    node.addEventListener('click', function () { openChat(node.getAttribute('data-ug-ask') || ''); });
  });

  document.getElementById('ugAskForm').addEventListener('submit', function (event) {
    event.preventDefault();
    var text = (input.value || '').trim();
    if (!text) { input.focus(); return; }
    input.value = '';
    openChat(text);
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

    html = re.sub(r'<script[^>]*src="\./[^"]*_files/[^"]*"[^>]*>\s*</script>', "", html)
    html = re.sub(r'<iframe[^>]*_files/[^"]*\.html[^>]*>\s*</iframe>', "", html)
    html = re.sub(
        r'<link[^>]+href="\./[^"]*_files/app\.[^"]*\.bundle\.css"[^>]*>',
        f'<link rel="stylesheet" href="{CSS_REMOTE}">',
        html,
    )
    html = re.sub(r'<link[^>]*widget\.css[^>]*>', "", html)
    html = re.sub(
        r'\./UserGate _ Безопасность[^"]*_files/([0-9a-f]{8,}\.(?:svg|png|jpg|jpeg|webp|woff2?|ttf))',
        r"https://usergate.com/f/dist/asset/\1",
        html,
    )

    if "data-ug-chat" not in html:
        marker = '<ul class="header-menu__menu">'
        if marker in html:
            html = html.replace(marker, marker + MENU_ITEM, 1)
    if 'id="ugAsk"' not in html:
        html = re.sub(r"(</header>)", r"\1" + PANEL, html, count=1)
    if 'id="ug-chat-style"' not in html:
        html = html.replace("</body>", STYLE + OVERLAY + "</body>", 1)

    TARGET.write_text(html, encoding="utf-8")
    print(f"страница: {TARGET} · {round(TARGET.stat().st_size/1024)} КБ")
    print("меню:", "data-ug-chat" in html, "| панель:", 'id="ugAsk"' in html, "| оверлей:", "ugChatFrame" in html)
    print("внешний CSS:", CSS_REMOTE in html, "| осталось _files:", len(re.findall(r"_files/", html)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
