"""Сборка site.html: панель чата, markdown-рендер, фиксированная высота."""

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
.ug-glow{position:fixed;inset:0;z-index:9997;pointer-events:none;padding:3px;opacity:0;
transition:opacity .55s ease;
-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
-webkit-mask-composite:xor;mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);
mask-composite:exclude}
.ug-glow.on{opacity:1}
.ug-glow i{position:absolute;inset:-45%;display:block;
background:conic-gradient(from 0deg,#ff2d55,#ff9500,#ffe600,#34c759,#32ade6,#5856d6,#ff2d55);
animation:ugSpin 5.5s linear infinite}
@keyframes ugSpin{to{transform:rotate(360deg)}}
.ug-ask{margin:0;padding:0;background:#1f3bff;color:#fff;
background:linear-gradient(120deg,#1f3bff 0%,#2f5bff 48%,#4a7bff 100%)}
.ug-ask__inner{padding:30px max(24px,calc((100vw - 1180px)/2)) 26px}
.ug-ask__title{margin:0 0 8px;font:700 clamp(20px,2.2vw,28px)/1.2 "Granate","Inter",Arial,sans-serif}
.ug-ask__sub{margin:0 0 20px;font:400 16px/1.5 "Granate","Inter",Arial,sans-serif;opacity:.92;max-width:760px}
.ug-ask__chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.ug-ask__chip{border:0;border-radius:999px;padding:8px 15px;font:500 14px "Granate","Inter",Arial,sans-serif;
color:#fff;background:rgba(255,255,255,.16);cursor:pointer;transition:background .18s ease,transform .18s ease}
.ug-ask__chip:hover{background:rgba(255,255,255,.28);transform:translateY(-1px)}
.ug-ask__chip:focus-visible{outline:2px solid rgba(255,255,255,.75);outline-offset:2px}
.ug-ask__form{display:flex;align-items:center;gap:10px;background:#fff;border-radius:16px;padding:10px 12px 10px 18px;
box-shadow:0 12px 30px rgba(12,20,60,.18)}
.ug-ask__input{flex:1;border:0;outline:0;font:400 17px "Granate","Inter",Arial,sans-serif;color:#25384a;background:transparent}
.ug-ask__input::placeholder{color:#8a97a8}
.ug-ask__send{width:46px;height:46px;border:0;border-radius:12px;cursor:pointer;display:grid;place-items:center;
background:rgba(31,59,255,.08);color:#2f4bff;font-size:20px;transition:background .18s ease,transform .12s ease}
.ug-ask__send:hover{background:rgba(31,59,255,.16)}
.ug-ask__send:active{transform:scale(.94)}
.ug-ask__chat{max-height:0;overflow:hidden;transition:max-height .42s cubic-bezier(.22,.61,.36,1);margin:0}
.ug-ask.is-chat .ug-ask__chat{height:min(540px,60vh);max-height:min(540px,60vh);overflow-y:auto;margin:0 0 16px}
.ug-ask__chat{scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.55) transparent}
.ug-ask__chat::-webkit-scrollbar{width:8px}
.ug-ask__chat::-webkit-scrollbar-track{background:transparent}
.ug-ask__chat::-webkit-scrollbar-thumb{background:rgba(255,255,255,.5);border-radius:8px}
.ug-ask__chat::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.75)}
.ug-ask__chat::-webkit-scrollbar-button{display:none;width:0;height:0}
.ug-ask__messages{display:flex;flex-direction:column;justify-content:flex-end;gap:12px;min-height:100%;padding-right:6px}
.ug-ask__starters{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.ug-ask__starters button{border:0;border-radius:999px;padding:8px 15px;font:500 14px "Granate","Inter",Arial,sans-serif;
color:#fff;background:rgba(255,255,255,.16);cursor:pointer;transition:background .18s ease,transform .18s ease}
.ug-ask__starters button:hover{background:rgba(255,255,255,.3);transform:translateY(-1px)}
.ug-ask__starters.is-hidden{display:none}
.ug-msg{border-radius:14px;padding:12px 16px;font:400 15px/1.55 "Granate","Inter",Arial,sans-serif;
max-width:min(820px,100%);word-wrap:break-word;animation:ugIn .3s cubic-bezier(.22,.61,.36,1) both}
.ug-msg--user,.ug-msg--bot{
background:rgba(255,255,255,.18);color:#fff;border:1px solid rgba(255,255,255,.22)}
.ug-msg--user{align-self:flex-end;white-space:pre-wrap}
.ug-msg--bot{align-self:flex-start}
.ug-msg--bot a{color:#d7e4ff;text-decoration:underline}
.ug-msg--bot a:hover{color:#fff}
.ug-msg--bot h3{margin:2px 0 8px;font:700 17px/1.3 "Granate","Inter",Arial,sans-serif;color:#fff}
.ug-msg--bot p{margin:0 0 10px}
.ug-msg--bot p:last-child{margin-bottom:0}
.ug-msg--bot ul{margin:6px 0 10px;padding-left:20px}
.ug-msg--bot li{margin:2px 0}
.ug-msg--bot code{background:rgba(255,255,255,.22);border-radius:5px;padding:1px 5px;font-size:13px;color:#fff}
.ug-table{overflow-x:auto;margin:10px 0}
.ug-table table{border-collapse:collapse;width:100%;font-size:14px}
.ug-table th,.ug-table td{border:1px solid rgba(255,255,255,.32);padding:8px 10px;text-align:left;vertical-align:top}
.ug-table th{background:rgba(255,255,255,.14);font-weight:700;color:#fff}
.ug-followups--after{align-self:flex-start;margin:6px 0 0 6px}
.ug-followups{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;animation:ugIn .3s ease both}
.ug-followups button{border:0;border-radius:999px;padding:8px 14px;font:500 13px "Granate","Inter",Arial,sans-serif;
color:#2050d0;background:#eef3ff;cursor:pointer;transition:background .18s ease}
.ug-followups button:hover{background:#dfe9ff}
.ug-msg__sources{margin-top:10px;font-size:13px;color:#5b6b7c}
.ug-msg__sources--after{align-self:stretch;margin:6px 0 2px;padding:12px 16px;max-width:min(820px,100%);
background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);border-radius:14px;
backdrop-filter:blur(4px);font-size:13px;animation:ugIn .3s ease both}
.ug-msg__sources--after summary{color:#fff;font-weight:600;display:flex;align-items:center;gap:8px;
padding:2px 0;letter-spacing:.01em}
.ug-msg__sources--after summary:before{content:"▸";color:#fff;transition:transform .18s ease}
.ug-msg__sources--after[open] summary:before{content:"▾"}
.ug-msg__sources--after[open] summary{margin-bottom:8px}
.ug-src{display:flex;gap:10px;align-items:flex-start;padding:8px 10px;margin-top:4px;border-radius:10px;
text-decoration:none;color:#eaf1ff;background:rgba(255,255,255,.06);transition:background .16s ease,transform .16s ease}
.ug-src:hover{background:rgba(255,255,255,.16);transform:translateX(2px)}
.ug-src__num{flex:0 0 22px;width:22px;height:22px;border-radius:7px;display:inline-flex;
align-items:center;justify-content:center;overflow:hidden;
background:rgba(255,255,255,.24);color:#fff;font:700 12px/1 Granate,Inter,Arial,sans-serif;
letter-spacing:0;margin-top:1px;text-align:center}
.ug-src__body{display:flex;flex-direction:column;gap:2px;min-width:0}
.ug-src__title{color:#fff;line-height:1.35;overflow:hidden;text-overflow:ellipsis}
.ug-src__host{color:rgba(255,255,255,.55);font-size:11px;letter-spacing:.02em}
.ug-msg--bot .ug-msg__sources summary{cursor:pointer;list-style:none;font-weight:600;color:#fff;
display:flex;align-items:center;gap:6px;outline:none}
.ug-msg--bot .ug-msg__sources summary::-webkit-details-marker{display:none}
.ug-msg--bot .ug-msg__sources summary:before{content:"▸";font-size:12px}
.ug-msg--bot .ug-msg__sources[open] summary:before{content:"▾"}
.ug-msg--bot .ug-msg__sources a{display:block;margin-top:6px;color:#d7e4ff;text-decoration:none;line-height:1.4}
.ug-msg--bot .ug-msg__sources a:hover{color:#fff;text-decoration:underline}
.ug-msg__typing{opacity:.6}
.ug-msg__typing::after{content:"";animation:ugDots 1.2s steps(1,end) infinite}
.ug-cursor{display:inline-block;width:7px;height:15px;margin-left:2px;vertical-align:-2px;
background:#2f4bff;animation:ugBlink 1s steps(1) infinite}
@keyframes ugBlink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes ugIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes ugDots{0%{content:""}33%{content:"."}66%{content:".."}100%{content:"..."}}
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
    <form class="ug-ask__form" id="ugAskForm">
      <input class="ug-ask__input" id="ugAskInput" type="text" placeholder="Введите запрос…" autocomplete="off" />
      <button class="ug-ask__send" type="submit" title="Отправить" aria-label="Отправить">&#10148;</button>
    </form>
    <div class="ug-ask__starters" id="ugStarters">
      <button type="button">Чем NGFW отличается от WAF?</button>
      <button type="button">Какие сертификаты ФСТЭК есть у продуктов?</button>
      <button type="button">Какие аппаратные платформы поддерживаются?</button>
      <button type="button">Что входит в каталог курсов и экзаменов Академии?</button>
    </div>
  </div>
</section>
"""

JS = r"""
(function () {
  var band = document.getElementById('ugAsk');
  var box = document.getElementById('ugChatBox');
  var list = document.getElementById('ugMessages');
  var form = document.getElementById('ugAskForm');
  var input = document.getElementById('ugAskInput');
  var cfg = window.__AGENT_API__ || {};
  var base = String(cfg.base || '').replace(/\/+$/, '');
  var token = String(cfg.token || '');
  var session = 'site-' + Math.random().toString(36).slice(2, 10);
  var busy = false;
  var DEFAULT_QUESTIONS = [
    'Чем NGFW отличается от WAF?',
    'Какие сертификаты ФСТЭК есть у продуктов?',
    'Какие аппаратные платформы поддерживаются?',
    'Что входит в каталог курсов и экзаменов Академии?'
  ];

  function escapeHtml(text) {
    return String(text).replace(/[&<>"]/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch];
    });
  }

  function fmt(value) {
    var s = escapeHtml(value);
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    s = s.replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank" rel="noopener">$1</a>');
    return s;
  }

  function renderMarkdown(text) {
    var lines = String(text || '').replace(/\r\n/g, '\n').split('\n');
    var out = [];
    var i = 0;

    function cells(value) {
      return value.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(function (c) { return c.trim(); });
    }

    while (i < lines.length) {
      var line = lines[i];
      if (!line.trim()) { i += 1; continue; }

      var head = line.match(/^(#{1,4})\s+(.*)$/);
      if (head) { out.push('<h3>' + fmt(head[2]) + '</h3>'); i += 1; continue; }

      var isRow = line.trim().charAt(0) === '|';
      var nextIsSep = i + 1 < lines.length &&
        /^\|?[\s:|-]+\|?$/.test(lines[i + 1].trim()) && lines[i + 1].indexOf('-') !== -1;
      if (isRow && nextIsSep) {
        var header = cells(line);
        i += 2;
        var rows = [];
        while (i < lines.length && lines[i].trim().charAt(0) === '|') { rows.push(cells(lines[i])); i += 1; }
        var html = '<div class="ug-table"><table><thead><tr>' +
          header.map(function (c) { return '<th>' + fmt(c) + '</th>'; }).join('') + '</tr></thead><tbody>';
        rows.forEach(function (row) {
          html += '<tr>' + row.map(function (c) { return '<td>' + fmt(c) + '</td>'; }).join('') + '</tr>';
        });
        out.push(html + '</tbody></table></div>');
        continue;
      }

      if (/^\s*[-*]\s+/.test(line)) {
        var items = [];
        while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
          items.push(lines[i].replace(/^\s*[-*]\s+/, ''));
          i += 1;
        }
        out.push('<ul>' + items.map(function (it) { return '<li>' + fmt(it) + '</li>'; }).join('') + '</ul>');
        continue;
      }

      var buf = [];
      while (
        i < lines.length && lines[i].trim() &&
        !/^(#{1,4})\s+/.test(lines[i]) &&
        lines[i].trim().charAt(0) !== '|' &&
        !/^\s*[-*]\s+/.test(lines[i])
      ) {
        buf.push(fmt(lines[i]));
        i += 1;
      }
      out.push('<p>' + buf.join('<br>') + '</p>');
    }
    return out.join('');
  }

  function addMessage(role, html) {
    var node = document.createElement('div');
    node.className = 'ug-msg ug-msg--' + role;
    node.innerHTML = html;
    list.appendChild(node);
    box.scrollTop = box.scrollHeight;
    return node;
  }

  function renderFollowups(node, items) {
    var questions = (items || []).map(function (item) {
      if (typeof item === 'string') return item;
      return (item && (item.question || item.text)) || '';
    }).filter(function (value) { return value; }).slice(0, 4);
    if (!questions.length) return;
    var row = document.createElement('div');
    row.className = 'ug-followups ug-followups--after';
    questions.forEach(function (question) {
      var button = document.createElement('button');
      button.type = 'button';
      button.textContent = question;
      button.addEventListener('click', function () { ask(question); });
      row.appendChild(button);
    });
    node.appendChild(row);
  }

  async function ask(question) {
    if (busy || !question) return;
    busy = true;
    band.classList.add('is-chat');
    if (starters) starters.classList.add('is-hidden');
    stopTyping();
    addMessage('user', escapeHtml(question));
    var bot = addMessage('bot', '<span class="ug-msg__typing">Думаю</span>');
    if (glow) glow.classList.add('on');
    var state = { text: '', shown: 0, done: false, sources: [], chips: [], finalize: null };
    var painting = false;

    function paint() {
      if (painting) return;
      painting = true;
      function frame() {
        if (state.shown < state.text.length) {
          var step = Math.max(3, Math.round(state.text.length * 0.02));
          state.shown = Math.min(state.text.length, state.shown + step);
          bot.innerHTML = renderMarkdown(state.text.slice(0, state.shown)) + '<span class="ug-cursor"></span>';
          box.scrollTop = box.scrollHeight;
          requestAnimationFrame(frame);
          return;
        }
        if (!state.done) {
          requestAnimationFrame(frame);
          return;
        }
        painting = false;
        bot.innerHTML = renderMarkdown(state.text || 'Не удалось получить ответ.');
        if (state.finalize) state.finalize();
        box.scrollTop = box.scrollHeight;
      }
      requestAnimationFrame(frame);
    }

    function finalize() {
      if (!state.chips.length) state.chips = DEFAULT_QUESTIONS;
      renderFollowups(list, state.chips);
      if (state.sources && state.sources.length) {
        var seen = {};
        var unique = state.sources.filter(function (item) {
          var key = String(item.url || item.source || item.title || '');
          if (!key || seen[key]) return false;
          seen[key] = true;
          return true;
        });
        if (unique.length) {
          var details = document.createElement('details');
          details.className = 'ug-msg__sources';
          var summary = document.createElement('summary');
          summary.textContent = 'Источники (' + unique.length + ')';
          details.appendChild(summary);
          unique.slice(0, 6).forEach(function (item, index) {
            var url = item.url || item.source || '';
            if (!url) return;
            var link = document.createElement('a');
            link.className = 'ug-src';
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener';

            var num = document.createElement('span');
            num.className = 'ug-src__num';
            num.textContent = String(index + 1);

            var body = document.createElement('span');
            body.className = 'ug-src__body';
            var title = document.createElement('span');
            title.className = 'ug-src__title';
            title.textContent = item.title || url;
            var host = document.createElement('span');
            host.className = 'ug-src__host';
            try { host.textContent = new URL(url).host.replace(/^www\./, ''); } catch (error) { host.textContent = ''; }
            body.appendChild(title);
            if (host.textContent) body.appendChild(host);

            link.appendChild(num);
            link.appendChild(body);
            details.appendChild(link);
          });
          details.classList.add('ug-msg__sources--after');
          list.appendChild(details);
        }
      }
    }

    try {
      var headers = { 'Content-Type': 'application/json' };
      if (token) headers['X-Api-Token'] = token;
      var response = await fetch((base || '') + '/api/chat', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          message: question,
          session_id: session,
          show_notes: false,
          use_cache: true,
          mode: 'auto',
          hidden: false
        })
      });
      if (!response.ok) throw new Error('HTTP ' + response.status);
      var reader = response.body.getReader();
      var decoder = new TextDecoder();
      var buffer = '';
      paint();
      while (true) {
        var chunk = await reader.read();
        if (chunk.done) break;
        buffer += decoder.decode(chunk.value, { stream: true });
        var blocks = buffer.split('\n\n');
        buffer = blocks.pop();
        blocks.forEach(function (block) {
          block.split('\n').forEach(function (line) {
            if (line.indexOf('data:') !== 0) return;
            var payload = line.slice(5).trim();
            if (!payload) return;
            var event;
            try { event = JSON.parse(payload); } catch (error) { return; }
            if (event.type === 'delta' && event.text) {
              if (glow) glow.classList.remove('on');
              state.text += event.text;
            } else if (event.type === 'sources' && event.items) {
              state.sources = event.items;
            } else if (event.type === 'done') {
              if (event.text) state.text = event.text;
              if (event.sources) state.sources = event.sources;
              if (Array.isArray(event.followups)) state.chips = event.followups;
            }
          });
        });
      }
      state.done = true;
      state.finalize = finalize;
    } catch (error) {
      state.text = 'Не удалось получить ответ: ' + error.message + '. Проверьте, что сервер и туннель запущены.';
      state.done = true;
      state.finalize = null;
      paint();
    } finally {
      busy = false;
    }
  }

  var starters = document.getElementById('ugStarters');
  if (starters) {
    Array.prototype.forEach.call(starters.querySelectorAll('button'), function (button) {
      button.addEventListener('click', function () { ask(button.textContent.trim()); });
    });
  }

  var EXAMPLES = [
    'Чем NGFW отличается от WAF?',
    'Какие сертификаты ФСТЭК есть у продуктов?',
    'Какие аппаратные платформы поддерживаются?',
    'Что входит в каталог курсов и экзаменов Академии?'
  ];
  var typeIndex = 0;
  var typePos = 0;
  var typeDeleting = false;
  var typeTimer = null;
  var typeRunning = false;

  function stopTyping() {
    typeRunning = false;
    if (typeTimer) { clearTimeout(typeTimer); typeTimer = null; }
    input.placeholder = 'Введите запрос…';
  }

  function typeLoop() {
    if (!typeRunning) return;
    var text = EXAMPLES[typeIndex % EXAMPLES.length];
    if (!typeDeleting) {
      typePos += 1;
      if (typePos >= text.length) {
        input.placeholder = text;
        typeDeleting = true;
        typeTimer = setTimeout(typeLoop, 1700);
        return;
      }
    } else {
      typePos -= 1;
      if (typePos <= 0) {
        typeDeleting = false;
        typeIndex += 1;
        typePos = 0;
      }
    }
    input.placeholder = typePos > 0 ? text.slice(0, typePos) : 'Введите запрос…';
    typeTimer = setTimeout(typeLoop, typeDeleting ? 24 : 58);
  }

  var glow = document.createElement('div');
  glow.className = 'ug-glow';
  glow.appendChild(document.createElement('i'));
  document.body.appendChild(glow);
  window.setTimeout(function () { glow.classList.add('on'); }, 60);
  window.setTimeout(function () { glow.classList.remove('on'); }, 1700);

  var header = document.querySelector('header');
  function pullUp() {
    if (!header || !band) return;
    var gap = band.getBoundingClientRect().top - header.getBoundingClientRect().bottom;
    if (gap > 0.5) band.style.marginTop = (-gap) + 'px';

    // Содержимое страницы после полосы: убираем его собственный большой отступ,
    // чтобы заголовок шёл сразу под чатом с ровным интервалом.
    var next = band.nextElementSibling;
    while (next && next.nodeType !== 1) next = next.nextElementSibling;
    if (next) {
      next.style.marginTop = '0';
      next.style.paddingTop = '0';
      var first = next.firstElementChild;
      if (first) {
        first.style.marginTop = '0';
        if (first.tagName === 'SECTION' || first.tagName === 'DIV') first.style.paddingTop = '28px';
      }
    }
  }
  window.addEventListener('load', pullUp);
  window.addEventListener('resize', pullUp);

  typeRunning = true;
  typeLoop();

  input.addEventListener('focus', stopTyping);
  input.addEventListener('input', function () { if (input.value) stopTyping(); });

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var value = (input.value || '').trim();
    if (!value) { input.focus(); return; }
    input.value = '';
    ask(value);
  });

})();
"""

MENU_ITEM = (
    '<li class="header-menu__item" role="presentation">'
    '<a class="header-menu__item-link" href="#ugAsk"><span>Чат с ИИ</span></a>'
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

    if ">Чат с ИИ<" not in html:
        menubar = '<ul class="" role="menubar">'
        start = html.find(menubar)
        if start >= 0:
            html = html[: start + len(menubar)] + MENU_ITEM + html[start + len(menubar):]

    if 'id="ugAsk"' not in html:
        html = html.replace("</header>", "</header>" + PANEL, 1)

    if 'id="ug-chat-style"' not in html:
        html = html.replace("</body>", STYLE + "<script>" + JS + "</script>" + "</body>", 1)

    TARGET.write_text(html, encoding="utf-8")
    print(f"страница: {TARGET} · {round(TARGET.stat().st_size/1024)} КБ")
    print("меню:", "data-ug-chat" in html, "| панель:", 'id="ugAsk"' in html, "| рендер:", "renderMarkdown" in html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
