
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
