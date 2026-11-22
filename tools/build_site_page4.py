"""Сборка site.html: панель чата, markdown-рендер, фиксированная высота."""

from __future__ import annotations

import io
import pathlib
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SOURCE = pathlib.Path(__file__).resolve().parent / "UserGate _ Безопасность корпоративных сетей и дата-центров.html"
TARGET = pathlib.Path("partner/web/site.html")
CSS_REMOTE = "https://usergate.com/f/dist/app.06e30aaf9470fae2ad91.bundle.css"

STYLE = """
<style id="ug-chat-style">
.ug-ask{margin:0;padding:0;background:#1f3bff;color:#fff;
background:linear-gradient(120deg,#1f3bff 0%,#2f5bff 48%,#4a7bff 100%)}
.ug-ask__inner{padding:30px max(24px,calc((100vw - 1180px)/2)) 26px}
.ug-ask__title{margin:0 0 28px;font:700 clamp(20px,2.2vw,28px)/1.2 "Granate","Inter",Arial,sans-serif}
.ug-ask__sub{margin:0 0 20px;font:400 16px/1.5 "Granate","Inter",Arial,sans-serif;opacity:.92;max-width:760px}
.ug-ask__chips{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px}
.ug-ask__chip{border:0;border-radius:999px;padding:8px 15px;font:500 14px "Granate","Inter",Arial,sans-serif;
color:#fff;background:rgba(255,255,255,.16);cursor:pointer;transition:background .18s ease,transform .18s ease}
.ug-ask__chip:hover{background:rgba(255,255,255,.28);transform:translateY(-1px)}
.ug-ask__chip:focus-visible{outline:2px solid rgba(255,255,255,.75);outline-offset:2px}
.ug-switch{display:flex;flex-direction:column;gap:10px}
.ug-switch__note{text-align:center;color:rgba(255,255,255,.88);font:400 15px/1.4 "Granate","Inter",Arial,sans-serif}
.ug-switch__link{display:flex;align-items:center;justify-content:center;gap:10px;background:#fff;
border-radius:16px;padding:17px 16px;color:#0c89db;font:600 17px "Granate","Inter",Arial,sans-serif;
text-decoration:none;box-shadow:0 1px 2px rgba(9,30,66,.12);transition:background .15s ease}
.ug-switch__link:hover{background:#f2f8ff}
.ug-switch__link:active{transform:scale(.995)}

.ug-ask__form{display:flex;align-items:center;gap:10px;background:#fff;border-radius:16px;padding:10px 12px 10px 18px;
box-shadow:0 12px 30px rgba(12,20,60,.18)}
.ug-ask__input{flex:1;border:0;outline:0;font:400 17px "Granate","Inter",Arial,sans-serif;color:#25384a;background:transparent}
.ug-ask__input::placeholder{color:#8a97a8}
.ug-ask__send{width:46px;height:46px;border:0;border-radius:12px;cursor:pointer;display:grid;place-items:center;
background:rgba(31,59,255,.08);color:#2f4bff;font-size:20px;transition:background .18s ease,transform .12s ease}
.ug-ask__send:hover{background:rgba(31,59,255,.16)}
.ug-ask__send:active{transform:scale(.94)}
.ug-ask__chat{max-height:0;overflow:hidden;transition:max-height .42s cubic-bezier(.22,.61,.36,1);margin:0}
.ug-ask.is-chat .ug-ask__chat{height:min(640px,68vh);max-height:min(640px,68vh);overflow-y:auto;margin:0 0 16px}
.ug-ask__chat{scrollbar-width:thin;scrollbar-color:rgba(255,255,255,.55) transparent}
.ug-ask__chat::-webkit-scrollbar{width:8px}
.ug-ask__chat::-webkit-scrollbar-track{background:transparent}
.ug-ask__chat::-webkit-scrollbar-thumb{background:rgba(255,255,255,.5);border-radius:8px}
.ug-ask__chat::-webkit-scrollbar-thumb:hover{background:rgba(255,255,255,.75)}
.ug-ask__chat::-webkit-scrollbar-button{display:none;width:0;height:0}
.ug-ask__messages{display:flex;flex-direction:column;justify-content:flex-end;gap:12px;min-height:100%;padding-right:6px}
.ug-skel{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}
.ug-skel span{display:block;height:38px;border-radius:12px;
background:linear-gradient(90deg,#eef2f7 0%,#e2e9f1 45%,#eef2f7 90%);
background-size:200% 100%;animation:ugSkel 1.1s ease-in-out infinite}
.ug-skel span:nth-child(1){width:190px}
.ug-skel span:nth-child(2){width:160px}
.ug-skel span:nth-child(3){width:210px}
@keyframes ugSkel{0%{background-position:120% 0}100%{background-position:-20% 0}}
.ug-table{overflow-x:auto}
.ug-table table{min-width:100%}
.ug-table td,.ug-table th{min-width:110px}
.ug-ask__starters{display:flex;gap:10px;flex-wrap:wrap;margin-top:2px}
.ug-ask__starters button{border:0;border-radius:14px;padding:12px 16px;font:400 15px "Granate","Inter",Arial,sans-serif;font-weight:400;
color:#1f2a36;background:#fff;cursor:pointer;text-align:left;box-shadow:0 2px 8px rgba(9,30,66,.12);
transition:background .18s ease,transform .18s ease,box-shadow .18s ease}
.ug-ask__starters button:hover{background:#f2f8ff;transform:translateY(-2px);box-shadow:0 8px 20px rgba(9,30,66,.18)}
.ug-ask__starters button:active{transform:translateY(0)}
.ug-ask__starters{margin:0 0 14px}
.ug-ask__starters.is-hidden{display:none}
.ug-msg{border-radius:14px;padding:12px 16px;font:400 15px/1.55 "Granate","Inter",Arial,sans-serif;
max-width:min(820px,100%);word-wrap:break-word;animation:ugIn .3s cubic-bezier(.22,.61,.36,1) both}
.ug-msg--user,.ug-msg--bot{
background:#fff;color:#22303f;border:1px solid rgba(15,27,40,.06);box-shadow:0 6px 18px rgba(12,25,60,.10)}
.ug-msg--user{align-self:flex-end;white-space:pre-wrap}
.ug-msg--bot{align-self:flex-start}
.ug-msg--bot a:focus,.ug-msg--bot a:focus-visible{outline:none}
.ug-msg--bot a{border:0;box-shadow:none}
.ug-msg--bot a{color:#0c89db;text-decoration:underline}
.ug-msg--bot a:hover{color:#0a6fb0}
.ug-msg--bot h3{margin:2px 0 8px;font:700 17px/1.3 "Granate","Inter",Arial,sans-serif;color:#1d2b3a}
.ug-msg--bot p{margin:0 0 10px}
.ug-msg--bot p:last-child{margin-bottom:0}
.ug-msg--bot ul{margin:6px 0 10px;padding-left:20px}
.ug-msg--bot li{margin:2px 0}
.ug-msg--bot code{background:#eef2f7;border-radius:5px;padding:1px 5px;font-size:13px;color:#22303f}
.ug-table{overflow-x:auto;margin:10px 0}
.ug-table table{border-collapse:collapse;width:100%;font-size:14px}
.ug-table th,.ug-table td{border:1px solid #dfe6ee;padding:8px 10px;text-align:left;vertical-align:top}
.ug-table th{background:#f4f7fb;font-weight:700;color:#1d2b3a}
.ug-followups--after{align-self:flex-start;margin:6px 0 0 6px}
.ug-cl{background:#fff;border:1px solid #e6ebf2;border-radius:18px;padding:18px 20px 16px;
box-shadow:0 10px 28px rgba(20,40,90,.10);position:relative;width:100%;max-width:720px;
animation:ugClIn .22s cubic-bezier(.22,.61,.36,1) both}
@keyframes ugClIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.ug-cl__close{position:absolute;right:14px;top:14px;width:26px;height:26px;border:0;border-radius:50%;
background:transparent;color:#8a97a8;font-size:16px;line-height:1;cursor:pointer;
transition:color .15s ease,transform .12s ease}
.ug-cl__close:hover{color:#25384a}
.ug-cl__close:active{transform:scale(.94)}
.ug-cl__kicker{font-size:11.5px;font-weight:600;letter-spacing:.02em;color:#6b7a8c;margin-bottom:8px}
.ug-cl__hint{font-size:14.5px;line-height:1.45;color:#25384a;margin:0 0 12px;max-width:640px}
.ug-cl__step{font-size:12px;color:#8a97a8;margin-bottom:8px}
.ug-cl__q{font-size:16px;font-weight:700;line-height:1.35;color:#16202b;margin:0 0 12px;padding-right:26px}
.ug-cl__options{display:flex;flex-direction:column;gap:8px}
.ug-cl__option{width:100%;padding:10px 14px;border:1px solid #e6ebf2;border-radius:12px;
background:#fbfcfe;color:#1f2a36;font:400 14.5px/1.4 "Granate","Inter",Arial,sans-serif;
text-align:left;cursor:pointer;transition:border-color .15s ease,background .15s ease}
.ug-cl__option:hover{border-color:#c3d7ea;background:#f2f8ff}
.ug-cl__option.is-picked{border-color:#0c89db;background:#eef6ff;box-shadow:inset 0 0 0 1px #0c89db}
.ug-cl__custom{display:flex;gap:8px;align-items:center;margin-top:12px}
.ug-cl__custom input{flex:1;min-width:0;padding:10px 12px;border:1px solid #e6ebf2;border-radius:10px;
background:#fff;color:#1f2a36;font:400 14px inherit;outline:none;transition:border-color .15s ease}
.ug-cl__custom input:focus{border-color:#8fb6dd}
.ug-cl__footer{display:flex;gap:8px;align-items:center;margin-top:12px}
.ug-cl__back{border:0;border-radius:10px;padding:9px 16px;background:#f1f4f8;color:#3c4b5c;
font:600 14px inherit;cursor:pointer;transition:background .15s ease}
.ug-cl__back:hover{background:#e6ebf2}
.ug-cl__back:disabled{opacity:.45;cursor:default}
.ug-cl__next{border:0;border-radius:10px;padding:9px 18px;background:#0c89db;color:#fff;
font:600 14px inherit;cursor:pointer;transition:background .15s ease,transform .12s ease}
.ug-cl__next:hover{background:#0a76bd}
.ug-cl__next:active{transform:scale(.97)}
.ug-cl__next:disabled{background:#c9d0d8;cursor:default;transform:none}
.ug-msg--survey{background:transparent;border:0;box-shadow:none;padding:0;align-self:stretch;max-width:none}
.ug-ask.is-survey .ug-ask__form,.ug-ask.is-survey .ug-ask__starters{display:none}
.ug-ask.is-survey .ug-ask__chat{margin-bottom:0}
.ug-ask.is-survey .ug-ask__chat{height:auto;max-height:min(640px,68vh)}
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
.ug-msg--bot .ug-msg__sources a.ug-src{display:flex;align-items:flex-start;gap:10px;color:#111;
background:#f4f7fb;padding:8px 10px;border-radius:10px;text-decoration:none}
.ug-msg--bot .ug-msg__sources a.ug-src:hover{background:#e9eff8;text-decoration:none}
.ug-src{display:flex;gap:10px;align-items:flex-start;padding:8px 10px;margin-top:4px;border-radius:10px;
text-decoration:none;color:#111;background:#f4f7fb;transition:background .16s ease,transform .16s ease}
.ug-src:hover{background:#e9eff8;transform:translateX(2px)}
.ug-src__num{flex:0 0 22px;width:22px;height:22px;border-radius:7px;display:inline-flex;
align-items:center;justify-content:center;overflow:hidden;
background:#e6e6e6;color:#111;font:700 12px/1 Granate,Inter,Arial,sans-serif;
letter-spacing:0;margin-top:1px;text-align:center}
.ug-src__body{display:flex;flex-direction:column;gap:2px;min-width:0}
.ug-src__title{color:#111;line-height:1.35;overflow:hidden;text-overflow:ellipsis}
.ug-src__host{color:#4a4a4a;font-size:11px;letter-spacing:.02em}
.ug-msg--bot .ug-msg__sources summary{cursor:pointer;list-style:none;font-weight:600;color:#111;
display:flex;align-items:center;gap:6px;outline:none}
.ug-msg--bot .ug-msg__sources summary::-webkit-details-marker{display:none}
.ug-msg--bot .ug-msg__sources summary:before{content:"▸";font-size:12px}
.ug-msg--bot .ug-msg__sources[open] summary:before{content:"▾"}
.ug-msg--bot .ug-msg__sources a{display:block;margin-top:6px;color:#111;text-decoration:none;line-height:1.4}
.ug-msg--bot .ug-msg__sources a:hover{color:#000;text-decoration:underline}
.ug-msg__typing{display:inline-block;letter-spacing:-.01em;
background:linear-gradient(90deg,#a3b0c0 0%,#25384a 45%,#a3b0c0 90%);
background-size:220% 100%;-webkit-background-clip:text;background-clip:text;
color:transparent;-webkit-text-fill-color:transparent;animation:ugSweep 2s linear infinite}
@keyframes ugSweep{from{background-position:200% 0}to{background-position:-100% 0}}
.ug-cursor{display:inline-block;width:7px;height:15px;margin-left:2px;vertical-align:-2px;
background:#2f4bff;animation:ugBlink 1s steps(1) infinite}
@keyframes ugBlink{0%,49%{opacity:1}50%,100%{opacity:0}}
@keyframes ugIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
33%{content:"."}66%{content:".."}100%{content:"..."}}
img[src*="_files/"]{display:none!important}
.header-menu__logo{display:inline-block;min-width:120px;height:26px;
background:url("https://usergate.com/f/dist/media/favicons/favicon.svg") no-repeat left center/contain}
@media(max-width:600px){.ug-ask__inner{padding:22px 16px}.ug-ask__title{margin-bottom:20px}}
</style>
"""

PANEL = """
<script src="config.js"></script>
<section class="ug-ask" id="ugAsk">
  <div class="ug-ask__inner">
    <h2 class="ug-ask__title">Спросите ИИ-ассистента о продуктах UserGate</h2>
    
    <div class="ug-ask__starters" id="ugStarters">
      <button type="button">Кто такая компания UserGate?</button>
      <button type="button">Какие продукты есть у UserGate?</button>
      <button type="button">Чем UserGate помогает бизнесу?</button>
      <button type="button">Как связаться с UserGate?</button>
    </div>
    <div class="ug-ask__chat" id="ugChatBox">
      <div class="ug-ask__messages" id="ugMessages" aria-live="polite"></div>
    </div>
    <form class="ug-ask__form" id="ugAskForm">
      <input class="ug-ask__input" id="ugAskInput" type="text" placeholder="Введите запрос…" autocomplete="off" />
      <button class="ug-ask__send" type="submit" title="Отправить" aria-label="Отправить">&#10148;</button>
    </form>
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
  // Один раз перезагружаем страницу с меткой версии: браузер не должен
  // показывать старый site.html из кеша.
  if (!/[?&]v=/.test(location.search) && !sessionStorage.getItem('ug_v')) {
    sessionStorage.setItem('ug_v', '1');
    location.replace(location.pathname + '?v=' + Date.now());
  }

  window.__UG_BUILD = '2026-11-21 16:15';
  console.log('SITE_BUILD', window.__UG_BUILD);

  var cfg = window.__AGENT_API__ || {};
  var base = String(cfg.base || '').replace(/\/+$/, '');
  var token = String(cfg.token || '');
  // Одна общая ветка для сайта: все вопросы попадают в один чат,
  // поэтому в index видна вся история переписки с сайта.
  // ?session=<id> — продолжить конкретный чат из index. Без параметра:
  // пустой чат — новый диалог, дальше вопросы идут в него же.
  var sessionParam = new URLSearchParams(location.search).get('session');
  var session = sessionParam || '';
  var TOOL_LABELS = {
    plan: 'Планирую ответ…',
    search_knowledge: 'Ищу в материалах…',
    find_product: 'Подбираю продукт…',
    find_faq: 'Проверяю частые вопросы…',
    company_profile: 'Смотрю профиль компании…',
    kb_stats: 'Считаю состав базы…',
    ask_clarification: 'Уточняю детали…'
  };

  var busy = false;
  var DEFAULT_QUESTIONS = [
    'Кто такая компания UserGate?',
    'Какие продукты есть у UserGate?',
    'Чем UserGate помогает бизнесу?',
    'Как связаться с UserGate?'
  ];

  function escapeHtml(text) {
    return String(text).replace(/[&<>"]/g, function (ch) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch];
    });
  }

    var BARE_DOMAIN = /(^|[\s(«])((?:[a-z0-9-]+\.)+(?:ru|com|org|net|io|su|by|kz)(?:\/[\w\-./?=&%#+]*)?)/gi;
    function linkBareDomains(html) {
      return html.replace(BARE_DOMAIN, function (match, prefix, domain) {
        return prefix + '<a href="https://' + domain + '" target="_blank" rel="noopener">' + domain + '</a>';
      });
    }
  function fmt(value) {
    var s = escapeHtml(value);
    s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
    s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    // Ссылки вида [1](https://…) прячем от автолинковки, иначе адрес
    // внутри скобок станет ссылкой, а «[1]» останется простым текстом.
    var mdLinks = [];
    s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g, function (match, label, url) {
      mdLinks.push('<a href="' + url + '" target="_blank" rel="noopener">' + label + '</a>');
      return '\u0001' + (mdLinks.length - 1) + '\u0001';
    });
    s = s.replace(/(https?:\/\/[^\s<]+)/g, function (url) {
      // Запятая и точка в конце адреса — это пунктуация текста, а не часть ссылки.
      var match = url.match(/^(.*?)([.,;:!?)\]]*)$/);
      var clean = match ? match[1] : url;
      var tail = match ? match[2] : '';
      return '<a href="' + clean + '" target="_blank" rel="noopener">' + clean + '</a>' + tail;
    });
    s = s.replace(/\u0001(\d+)\u0001/g, function (match, index) {
      return mdLinks[Number(index)] || '';
    });
    return linkBareDomains(s);
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

  var askedCount = 0;
  var indexSuggested = false;

  function maybeSuggestIndex() {
    if (indexSuggested || askedCount < 3) return;
    var form = document.querySelector('#ugAsk .ug-ask__form');
    if (!form) return;
    indexSuggested = true;

    var wrap = document.createElement('div');
    wrap.className = 'ug-switch';

    var note = document.createElement('div');
    note.className = 'ug-switch__note';
    note.textContent = 'Пожалуйста, продолжите в полном чате — там история, рассуждения и все источники.';

    var link = document.createElement('a');
    link.className = 'ug-switch__link';
    link.href = (base || '') + '/?session=' + encodeURIComponent(session);
    link.textContent = 'Перейти в чат';

    wrap.appendChild(note);
    wrap.appendChild(link);
    form.parentNode.insertBefore(wrap, form);
    form.style.display = 'none';
  }

  function trimPartialMarkdown(value) {
    var lines = String(value || '').split('\n');
    var last = lines[lines.length - 1] || '';
    // Неполная строка таблицы: нечётное число пайпов — убираем её до готовности.
    if (/^\s*\|/.test(last) && (last.match(/\|/g) || []).length % 2 === 1) {
      lines.pop();
    }
    var text = lines.join('\n');
    if ((text.match(/\*\*/g) || []).length % 2 === 1) {
      text = text.slice(0, text.lastIndexOf('**'));
    }
    return text;
  }

  function showPlaceholders(node) {
    clearPlaceholders(node);
    var row = document.createElement('div');
    row.className = 'ug-skel';
    for (var i = 0; i < 3; i += 1) row.appendChild(document.createElement('span'));
    node.appendChild(row);
  }

  function clearPlaceholders(node) {
    var rows = node.querySelectorAll('.ug-skel');
    for (var i = 0; i < rows.length; i += 1) rows[i].remove();
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

  function renderClarification(node, payload, original) {
    var questions = (payload && payload.questions) || [];
    if (!questions.length) return;

    var card = document.createElement('div');
    card.className = 'ug-cl';

    var close = document.createElement('button');
    close.type = 'button';
    close.className = 'ug-cl__close';
    close.textContent = '\u00d7';
    close.title = 'Закрыть опрос';
    card.appendChild(close);

    var kicker = document.createElement('div');
    kicker.className = 'ug-cl__kicker';
    kicker.textContent = 'Уточним детали';
    card.appendChild(kicker);

    if (payload.intro) {
      var hint = document.createElement('p');
      hint.className = 'ug-cl__hint';
      hint.textContent = payload.intro;
      card.appendChild(hint);
    }

    var step = document.createElement('div');
    step.className = 'ug-cl__step';
    card.appendChild(step);

    var title = document.createElement('p');
    title.className = 'ug-cl__q';
    card.appendChild(title);

    var options = document.createElement('div');
    options.className = 'ug-cl__options';
    card.appendChild(options);

    var custom = document.createElement('div');
    custom.className = 'ug-cl__custom';
    var field = document.createElement('input');
    field.type = 'text';
    custom.appendChild(field);
    card.appendChild(custom);

    var footer = document.createElement('div');
    footer.className = 'ug-cl__footer';
    var back = document.createElement('button');
    back.type = 'button';
    back.className = 'ug-cl__back';
    back.textContent = 'Назад';
    var next = document.createElement('button');
    next.type = 'button';
    next.className = 'ug-cl__next';
    next.textContent = 'Далее';
    footer.appendChild(back);
    footer.appendChild(next);
    card.appendChild(footer);

    var answers = questions.map(function () { return null; });
    var customText = questions.map(function () { return ''; });
    var index = 0;
    var closed = false;

    function stop() {
      card.remove();
      band.classList.remove('is-survey');
    }

    function finish() {
      if (closed) return;
      closed = true;
      stop();
      var ready = answers
        .map(function (item, position) {
          var value = customText[position] || item;
          return value ? (questions[position].question + ' ' + value) : '';
        })
        .filter(function (value) { return value; });
      if (ready.length) ask(ready.join('\n'), { hidden: true });
    }

    function render() {
      var item = questions[index] || {};
      step.textContent = 'Вопрос ' + (index + 1) + ' из ' + questions.length;
      title.textContent = item.question || '';
      field.value = customText[index] || '';
      field.placeholder = item.placeholder || 'Впишите свою ситуацию';
      options.innerHTML = '';
      (item.options || []).forEach(function (option) {
        var label = typeof option === 'string' ? option : (option.label || option.value || '');
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'ug-cl__option' + (answers[index] === label ? ' is-picked' : '');
        button.textContent = label;
        button.addEventListener('click', function () {
          answers[index] = label;
          render();
        });
        options.appendChild(button);
      });
      back.disabled = index === 0;
      next.disabled = !(answers[index] || customText[index] || field.value.trim());
      next.textContent = index === questions.length - 1 ? 'Готово' : 'Далее';
    }

    next.addEventListener('click', function () {
      var value = (field.value || '').trim();
      if (value) customText[index] = value;
      var chosen = customText[index] || answers[index];
      if (!chosen) { field.focus(); return; }
      if (index === questions.length - 1) { finish(); return; }
      index += 1;
      render();
    });

    back.addEventListener('click', function () {
      if (index > 0) { index -= 1; render(); }
    });

    field.addEventListener('input', function () {
      customText[index] = field.value;
      next.disabled = !(field.value.trim() || answers[index]);
    });

    field.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') { event.preventDefault(); next.click(); }
    });

    close.addEventListener('click', function () {
      if (closed) return;
      closed = true;
      stop();
      // Как в основном интерфейсе: закрыли опрос — всё равно отвечаем
      // на исходный вопрос, с учётом уже данных ответов.
      var lines = [];
      if (original) lines.push('Исходный вопрос: ' + original);
      answers.forEach(function (item, position) {
        var value = item || customText[position];
        if (value) lines.push(questions[position].question + ' ' + value);
      });
      lines.push('Клиент закрыл опрос. Ответь на исходный вопрос без дополнительных уточнений.');
      ask(lines.join('\n'), { hidden: true });
    });

    render();
    node.appendChild(card);
    field.focus();
  }

  function chooseMode(text) {
    // Расплывчатый запрос — сначала уточняем (быстрый вызов), иначе обычный режим.
    return /подбер|подскаж|выбрать|посовет|что лучше|какой продукт|помоги/i.test(text)
      ? 'clarify' : 'auto';
  }

  async function ask(question, options) {
    options = options || {};
    askedCount += 1;
    if (busy || !question) return;
    busy = true;
    band.classList.add('is-chat');
    if (starters) starters.classList.add('is-hidden');
    stopTyping();
    if (!options.hidden) addMessage('user', escapeHtml(question));
    var watchdog = window.setTimeout(function () {
      if (state.done) return;
      state.done = true;
      bot.innerHTML = '<span class="ug-msg__typing">Ответ не пришёл за минуту. Попробуйте ещё раз.</span>';
    }, 60000);
    var bot = addMessage('bot', '<span class="ug-msg__typing">Думаю</span>');
    var state = { text: '', shown: 0, done: false, sources: [], chips: [], finalize: null, clarification: null, finalized: false, status: 'Думаю', question: question, startedAt: Date.now() };
    var painting = false;

    function paint() {
      if (painting) return;
      painting = true;
      function safeRender(node, value) {
        var html;
        try {
          html = renderMarkdown(value);
        } catch (error) {
          // Рендер не должен ломать сообщение: показываем текст как есть.
          html = '<p>' + escapeHtml(value).replace(/\n/g, '<br>') + '</p>';
        }
        node.innerHTML = html;
      }

      var lastPaint = 0;
      var lastMarkdown = 0;

      function frame() {
        if (state.shown < state.text.length) {
          var step = Math.max(4, Math.round(state.text.length * 0.03));
          state.shown = Math.min(state.text.length, state.shown + step);
          var now = Date.now();
          if (now - lastPaint > 55) {
            lastPaint = now;
            // Пока текста нет — держим статус («Думаю», шаг, инструмент),
            // а не пустой пузырь. Текст печатаем простым, без markdown.
            if (!state.text.length) {
              bot.innerHTML = '<span class="ug-msg__typing">' +
                escapeHtml(state.status || 'Думаю') + ' · ' + Math.max(1, Math.round((Date.now() - state.startedAt) / 1000)) + ' с' + '</span><span class="ug-cursor"></span>';
            } else {
              // Лёгкая отрисовка во время потока: markdown на таком объёме
              // перерисовывать каждые 55 мс слишком дорого — вкладка подвисает.
              // Markdown на каждом кадре — дорого для таблиц; обновляем не чаще 200 мс.
              if (!lastMarkdown || now - lastMarkdown > 200) {
                lastMarkdown = now;
                var slice = trimPartialMarkdown(state.text.slice(0, state.shown));
                var live = '';
                try { live = renderMarkdown(slice); } catch (error) { live = ''; }
                if (live) {
                  bot.innerHTML = live + '<span class="ug-cursor"></span>';
                }
              }
            }
            box.scrollTop = box.scrollHeight;
          }
          requestAnimationFrame(frame);
          return;
        }
        if (!state.done) {
          requestAnimationFrame(frame);
          return;
        }
        painting = false;
        safeRender(bot, state.text || (state.clarification ? '' : 'Не удалось получить ответ.'));
        if (state.finalize) {
          try { state.finalize(); } catch (error) { /* блоки не критичны */ }
        }
        box.scrollTop = box.scrollHeight;
      }
      requestAnimationFrame(frame);
    }

    function finalize() {
      if (state.finalized) return;
      state.finalized = true;
      if (state.clarification) {
        try {
          // Опрос заменяет переписку: карточка занимает всё окно чата,
          // а лента сообщений на это время скрыта.
          band.classList.add('is-survey');
          bot.remove();
          var survey_host = document.createElement('div');
          survey_host.className = 'ug-msg ug-msg--survey';
          list.appendChild(survey_host);
          renderClarification(survey_host, state.clarification, state.question);
        } catch (error) {
          var fallback = document.createElement('div');
          fallback.className = 'ug-cl';
          fallback.textContent = (state.clarification.questions || [])
            .map(function (item) { return item.question; }).join(' · ');
          bot.appendChild(fallback);
        }
      }
      var asked = String(state.question || '').trim().toLowerCase();
      var pool = (state.chips && state.chips.length) ? state.chips : [];
      state.chips = pool.filter(function (item) {
        var text = typeof item === 'string' ? item : (item && (item.question || item.text)) || '';
        return String(text).trim().toLowerCase() !== asked;
      });
      // Запасных стартовых вопросов здесь быть не должно: кнопки — только
      // продолжения по теме ответа. Если модель их не дала, предлагаем
      // «Подробнее» по заголовку самого ответа.
      if (!state.chips.length && !state.clarification) {
        var heading = String(state.text || '').split('\n')[0].replace(/^#+\s*/, '').trim();
        if (heading) state.chips = ['Подробнее: ' + heading.slice(0, 60)];
      }
      if (state.clarification) state.chips = [];
      if (state.chips && state.chips.length) {
        renderFollowups(list, state.chips);
      } else if (!state.clarification) {
        showPlaceholders(list);
      }
      maybeSuggestIndex();
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
            var raw = String(url || item.source || "");
            var match = raw.match(/https?:\/\/([^\/]+)/i) || raw.match(/([a-z0-9-]+\.(?:ru|com|org|net|io))/i);
            host.textContent = match ? match[1].replace(/^www\./, "") : "";
            body.appendChild(title);
            if (host.textContent) body.appendChild(host);

            link.appendChild(num);
            link.appendChild(body);
            details.appendChild(link);
          });
          bot.appendChild(details);
        }
      }
    }

    try {
      var headers = { 'Content-Type': 'application/json' };
      if (token) headers['X-Api-Token'] = token;
      if (!session) {
        session = 'site-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      }
      var response = await fetch((base || '') + '/api/chat', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          message: question,
          session_id: session,
          show_notes: false,
          use_cache: true,
          mode: options.mode || chooseMode(question),
          client: 'site',
          hidden: !!options.hidden
        })
      });
      if (!response.ok) throw new Error('HTTP ' + response.status);
      var reader = response.body.getReader();
      var decoder = new TextDecoder();
      var buffer = '';
      function consumeBlock(block) {
        block.split('\n').forEach(function (line) {
          if (line.indexOf('data:') !== 0) return;
          var payload = line.slice(5).trim();
          if (!payload) return;
          var event;
          try { event = JSON.parse(payload); } catch (error) { return; }
          if (event.type === 'delta' && event.text) {
            state.text += event.text;
          } else if (event.type === 'tool_call' && event.name) {
            var toolLabel = TOOL_LABELS[event.name];
            if (toolLabel) {
              state.status = toolLabel;
              if (!state.done && !state.text) {
                bot.innerHTML = '<span class="ug-msg__typing">' + escapeHtml(toolLabel) + '</span>';
              }
            }
          } else if (event.type === 'step') {
            var label = String(event.title || event.name || event.label || '').trim();
            if (!label) label = 'Почти готово';
            if (label) {
              state.status = label;
              if (!state.done && !state.text) {
                bot.innerHTML = '<span class="ug-msg__typing">' + escapeHtml(label) + '</span>';
              }
            }
          } else if (event.type === 'sources' && event.items) {
            state.sources = event.items;
          } else if (event.type === 'clarification') {
          if (event.session_id && event.session_id !== session) return;
          if (event.client && event.client !== 'site') return;
          if (
            event.clarification &&
            event.clarification.session_id &&
            String(event.clarification.session_id) !== String(session)
          ) return;
            state.clarification = event;
            state.done = true;
            // Опрос приходит отдельным событием: перерисовываем карточку,
            // даже если сообщение уже было финализировано.
            state.finalized = false;
            try { finalize(); } catch (error) { /* не критично */ }
          } else if (event.type === 'followups' && event.items) {
            if (state.clarification) return;
            clearPlaceholders(list);
            state.chips = event.items;
            if (state.finalized) renderFollowups(list, event.items);
          } else if (event.type === 'done') {
            if (event.text) state.text = event.text;
            if (event.sources) state.sources = event.sources;
            if (Array.isArray(event.followups)) state.chips = event.followups;
            // Не растягиваем печать: сразу показываем готовое оформление.
            state.shown = String(state.text || '').length;
            paint();
          }
        });
      }

      paint();
      while (true) {
        var chunk = await reader.read();
        if (chunk.done) break;
        buffer += decoder.decode(chunk.value, { stream: true });
        var blocks = buffer.split('\n\n');
        buffer = blocks.pop();
        blocks.forEach(consumeBlock);
      }
      buffer += decoder.decode();
      if (buffer.trim()) consumeBlock(buffer);

      window.clearTimeout(watchdog);
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
    'Где находится офис UserGate?',
    'В каких отраслях работает UserGate?',
    'Сколько лет компания на рынке?',
    'Как стать партнёром UserGate?',
    'Какие награды есть у компании?'
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


  if (location.search.indexOf('survey=1') !== -1) {
    band.classList.add('is-chat');
    band.classList.add('is-survey');
    var demo = document.createElement('div');
    demo.className = 'ug-msg ug-msg--survey';
    list.appendChild(demo);
    renderClarification(demo, {
      intro: 'Чтобы рассказ был по делу, уточните пару моментов.',
      questions: [
        { question: 'Что нужно защитить в первую очередь?',
          options: ['Корпоративную сеть и периметр', 'ЦОД или высоконагруженную инфраструктуру', 'Веб-приложения и сайты'],
          placeholder: 'Свой вариант' }
      ]
    });
  }

  var askParam = new URLSearchParams(location.search).get('ask');
  if (askParam) {
    band.classList.add('is-chat');
    window.setTimeout(function () { ask(askParam); }, 300);
  }

  typeRunning = true;
  typeLoop();

  var GREETINGS = [
    'Здравствуйте! Чем могу помочь?',
    'Здравствуйте! Подскажу по продуктам UserGate — что вас интересует?',
    'Здравствуйте! Спросите про продукты, лицензирование, сертификаты или обучение.',
    'Здравствуйте! Готов ответить на вопросы о решениях UserGate.'
  ];
  var greeted = false;

  function greet() {
    if (greeted) return;
    greeted = true;
    var text = GREETINGS[Math.floor(Math.random() * GREETINGS.length)];
    addMessage('bot', renderMarkdown(text));
    box.scrollTop = box.scrollHeight;
  }

  function expandChat() {
    band.classList.add('is-chat');
    if (list.children.length === 0) greet();
  }

  input.addEventListener('focus', function () { expandChat(); });
  input.addEventListener('click', function () { expandChat(); });
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
    html = re.sub(r'<img[^>]*_files/[^>]*>', "", html)
    html = re.sub(r'href="/f/dist/asset/', 'href="https://usergate.com/f/dist/asset/', html)
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
