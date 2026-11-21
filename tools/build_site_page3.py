"""Страница usergate.com: синяя полоса с чатом, который раскрывается вверх."""

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
/* Полоса на всю ширину, вплотную к шапке, без скруглений. */
.ug-ask{margin:0;padding:0;background:#1f3bff;color:#fff;
background:linear-gradient(120deg,#1f3bff 0%,#2f5bff 48%,#4a7bff 100%)}
.ug-ask__inner{padding:30px max(24px,calc((100vw - 1180px)/2)) 26px}
.ug-ask__title{margin:0 0 8px;font:700 clamp(20px,2.2vw,28px)/1.2 "Granate","Inter",Arial,sans-serif}
.ug-ask__sub{margin:0 0 20px;font:400 16px/1.5 "Granate","Inter",Arial,sans-serif;opacity:.92;max-width:760px}
.ug-ask__chips{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.ug-ask__chip{border:0;border-radius:999px;padding:8px 15px;font:500 14px "Granate","Inter",Arial,sans-serif;
color:#fff;background:rgba(255,255,255,.16);cursor:pointer}
.ug-ask__chip:hover{background:rgba(255,255,255,.28)}
.ug-ask__form{display:flex;align-items:center;gap:10px;background:#fff;border-radius:16px;padding:10px 12px 10px 18px;
box-shadow:0 12px 30px rgba(12,20,60,.18)}
.ug-ask__input{flex:1;border:0;outline:0;font:400 17px "Granate","Inter",Arial,sans-serif;color:#25384a;background:transparent}
.ug-ask__input::placeholder{color:#8a97a8}
.ug-ask__send{width:46px;height:46px;border:0;border-radius:12px;cursor:pointer;display:grid;place-items:center;
background:rgba(31,59,255,.08);color:#2f4bff;font-size:20px}
.ug-ask__send:hover{background:rgba(31,59,255,.16)}

/* Раскрывающийся чат: сообщения выше поля ввода. */
.ug-ask__chat{max-height:0;overflow:hidden;transition:max-height .35s ease;margin:0}
.ug-ask.is-chat .ug-ask__chat{height:320px;max-height:320px;overflow-y:auto;margin:0 0 16px}
.ug-ask__messages{display:flex;flex-direction:column;gap:12px;padding-right:6px}
.ug-msg{border-radius:14px;padding:12px 16px;font:400 15px/1.55 "Granate","Inter",Arial,sans-serif;
max-width:min(820px,100%);white-space:pre-wrap;word-wrap:break-word}
.ug-msg--user{align-self:flex-end;background:rgba(255,255,255,.18)}
.ug-msg--bot{align-self:flex-start;background:#fff;color:#25384a}
.ug-msg--bot a{color:#0c89db}
.ug-msg--bot strong{font-weight:700}
.ug-msg--bot ul{margin:8px 0 0;padding-left:20px}
.ug-msg__sources{margin-top:10px;font-size:13px;color:#5b6b7c}
.ug-msg__sources a{display:block;margin-top:4px;color:#0c89db;text-decoration:none}
.ug-msg__typing{opacity:.6}

@keyframes ugIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes ugDots{0%{content:""}33%{content:"."}66%{content:".."}100%{content:"..."}}
.ug-ask__chat{transition:max-height .42s cubic-bezier(.22,.61,.36,1)}
.ug-ask__messages{justify-content:flex-end;min-height:100%}
.ug-msg{animation:ugIn .3s cubic-bezier(.22,.61,.36,1) both}
.ug-ask__chip{transition:background .18s ease,transform .18s ease}
.ug-ask__chip:hover{transform:translateY(-1px)}
.ug-ask__send{transition:background .18s ease,transform .12s ease}
.ug-ask__send:active{transform:scale(.94)}
.ug-msg__typing::after{content:"";animation:ugDots 1.2s steps(1,end) infinite}

.ug-msg--bot h3{margin:2px 0 8px;font:700 17px/1.3 "Granate","Inter",Arial,sans-serif;color:#1d2b3a}
.ug-msg--bot p{margin:0 0 10px}
.ug-msg--bot p:last-child{margin-bottom:0}
.ug-msg--bot ul{margin:6px 0 10px;padding-left:20px}
.ug-msg--bot li{margin:2px 0}
.ug-msg--bot code{background:#eef2f7;border-radius:5px;padding:1px 5px;font-size:13px}
.ug-table{overflow-x:auto;margin:10px 0}
.ug-table table{border-collapse:collapse;width:100%;font-size:14px}
.ug-table th,.ug-table td{border:1px solid #dfe6ee;padding:8px 10px;text-align:left;vertical-align:top}
.ug-table th{background:#f4f7fb;font-weight:700}
img[src*="_files/"]{display:none!important}
.header-menu__logo{display:inline-block;min-width:120px;height:26px;
background:url("https://usergate.com/f/dist/media/favicons/favicon.svg") no-repeat left center/contain}
@media(max-width:600px){.ug-ask__inner{padding:22px 16px}}
</style>
"""

PANEL = """
<script src="config.js"></script>
<section class="ug-ask" id="ugAsk">
  <div class="ug-ask__inner">
    <h2 class="ug-ask__title">Спросите ИИ-ассистента о продуктах UserGate</h2>
    <p class="ug-ask__sub">Ответы по документации, карточкам продуктов и FAQ — со ссылками на источники.</p>
    <div class="ug-ask__chat" id="ugChatBox">
      <div class="ug-ask__messages" id="ugMessages" aria-live="polite"></div>
    </div>
    <div class="ug-ask__chips" id="ugChips">
      <button class="ug-ask__chip" type="button">Чем NGFW отличается от WAF?</button>
      <button class="ug-ask__chip" type="button">Какие сертификаты ФСТЭК есть у продуктов?</button>
      <button class="ug-ask__chip" type="button">Какие аппаратные платформы поддерживаются?</button>
      <button class="ug-ask__chip" type="button">Что входит в каталог курсов и экзаменов Академии?</button>
    </div>
    <form class="ug-ask__form" id="ugAskForm">
      <input class="ug-ask__input" id="ugAskInput" type="text" placeholder="Введите запрос…" autocomplete="off" />
      <button class="ug-ask__send" type="submit" title="Отправить" aria-label="Отправить">&#10148;</button>
    </form>
  </div>
</section>

<script>
(function () {
  var band = document.getElementById('ugAsk');
  var box = document.getElementById('ugChatBox');
  var list = document.getElementById('ugMessages');
  var form = document.getElementById('ugAskForm');
  var input = document.getElementById('ugAskInput');
  var cfg = window.__AGENT_API__ || {};
  var base = String(cfg.base || '').replace(/\\/+$/, '');
  var token = String(cfg.token || '');
  var session = 'site-' + Math.random().toString(36).slice(2, 10);
  var busy = false;

  function escapeHtml(text) {
    return String(text).replace(/[&<>"]/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch];
    });
  }

  function renderMarkdown(text) {
    var lines = String(text || "").replace(/\r\n/g, "\n").split("\n");
    var out = [];
    var i = 0;

    function fmt(value) {
      var s = escapeHtml(value);
      s = s.replace(/`([^`]+)`/g, "<code>$1</code>");
      s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
      s = s.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
      return s;
    }

    while (i < lines.length) {
      var line = lines[i];
      if (!line.trim()) { i += 1; continue; }

      var head = line.match(/^(#{1,4})\s+(.*)$/);
      if (head) { out.push("<h3>" + fmt(head[2]) + "</h3>"); i += 1; continue; }

      var isRow = line.trim().charAt(0) === "|";
      var nextIsSep = i + 1 < lines.length && /^\|?[\s:|-]+\|?$/.test(lines[i + 1].trim()) && lines[i + 1].indexOf("-") !== -1;
      if (isRow && nextIsSep) {
        var cells = function (value) {
          return value.trim().replace(/^\|/, "").replace(/\|$/, "").split("|").map(function (c) { return c.trim(); });
        };
        var head2 = cells(line);
        i += 2;
        var rows = [];
        while (i < lines.length && lines[i].trim().charAt(0) === "|") { rows.push(cells(lines[i])); i += 1; }
        var html = '<div class="ug-table"><table><thead><tr>' +
          head2.map(function (c) { return "<th>" + fmt(c) + "</th>"; }).join("") +
          "</tr></thead><tbody>";
        rows.forEach(function (row) {
          html += "<tr>" + row.map(function (c) { return "<td>" + fmt(c) + "</td>"; }).join("") + "</tr>";
        });
        out.push(html + "</tbody></table></div>");
        continue;
      }

      if (/^\s*[-*]\s+/.test(line)) {
        var items = [];
        while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
          items.push(lines[i].replace(/^\s*[-*]\s+/, ""));
          i += 1;
        }
        out.push("<ul>" + items.map(function (it) { return "<li>" + fmt(it) + "</li>"; }).join("") + "</ul>");
        continue;
      }

      var buf = [];
      while (
        i < lines.length && lines[i].trim() &&
        !/^(#{1,4})\s+/.test(lines[i]) &&
        lines[i].trim().charAt(0) !== "|" &&
        !/^\s*[-*]\s+/.test(lines[i])
      ) {
        buf.push(fmt(lines[i]));
        i += 1;
      }
      out.push("<p>" + buf.join("<br>") + "</p>");
    }
    return out.join("");
  }

  function addMessage(role, html) {
    var node = document.createElement('div');
    node.className = 'ug-msg ug-msg--' + role;
    node.innerHTML = html;
    list.appendChild(node);
    box.scrollTop = box.scrollHeight;
    return node;
  }

  function expand() {
    band.classList.add('is-chat');
  }

  async function ask(question) {
    if (busy || !question) return;
    busy = true;
    expand();
    addMessage('user', escapeHtml(question));
    var bot = addMessage('bot', '<span class="ug-msg__typing">Думаю…</span>');
    var text = '';
    var sources = [];
    try {
      var headers = { 'Content-Type': 'application/json' };
      if (token) headers['X-Api-Token'] = token;
      var response = await fetch((base || '') + '/api/chat', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({ message: question, session_id: session, show_notes: false, use_cache: true, mode: 'auto', hidden: false })
      });
      if (!response.ok) throw new Error('HTTP ' + response.status);
      var reader = response.body.getReader();
      var decoder = new TextDecoder();
      var buffer = '';
      while (true) {
        var chunk = await reader.read();
        if (chunk.done) break;
        buffer += decoder.decode(chunk.value, { stream: true });
        var lines = buffer.split('\\n');
        buffer = lines.pop();
        for (var i = 0; i < lines.length; i += 1) {
          var line = lines[i].trim();
          if (!line || line.indexOf('data:') !== 0) continue;
          var payload = line.slice(5).trim();
          if (payload === '[DONE]') continue;
          var event;
          try { event = JSON.parse(payload); } catch (error) { continue; }
          if (event.type === 'delta' && event.text) {
            text += event.text;
            bot.innerHTML = renderMarkdown(text);
            box.scrollTop = box.scrollHeight;
          } else if (event.type === 'sources' && event.items) {
            sources = event.items;
          } else if (event.type === 'done') {
            if (event.text) text = event.text;
            if (event.sources) sources = event.sources;
          }
        }
      }
      bot.innerHTML = renderMarkdown(text || 'Не удалось получить ответ.');
      if (sources && sources.length) {
        var block = document.createElement('div');
        block.className = 'ug-msg__sources';
        block.innerHTML = 'Источники:' + sources.slice(0, 4).map(function (item) {
          var url = item.url || item.source || '';
          var title = item.title || url;
          return url ? '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener">' + escapeHtml(title) + '</a>' : '';
        }).join('');
        bot.appendChild(block);
      }
    } catch (error) {
      bot.innerHTML = 'Не удалось получить ответ: ' + escapeHtml(error.message) + '. Проверьте, что сервер и туннель запущены.';
    } finally {
      busy = false;
      box.scrollTop = box.scrollHeight;
    }
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var value = (input.value || '').trim();
    if (!value) { input.focus(); return; }
    input.value = '';
    ask(value);
  });

  Array.prototype.forEach.call(document.querySelectorAll('.ug-ask__chip'), function (chip) {
    chip.addEventListener('click', function () { ask(chip.textContent.trim()); });
  });
})();
</script>
"""

MENU_ITEM = (
    '<li class="header-menu__menu-item">'
    '<a class="header-menu__menu-item-link" href="#ugAsk">Чат с ИИ</a>'
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
        html = html.replace("</header>", "</header>" + PANEL, 1)
    if 'id="ug-chat-style"' not in html:
        html = html.replace("</body>", STYLE + "</body>", 1)

    TARGET.write_text(html, encoding="utf-8")
    print(f"страница: {TARGET} · {round(TARGET.stat().st_size/1024)} КБ")
    print("полоса:", 'id="ugAsk"' in html, "| чат:", 'id="ugMessages"' in html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
