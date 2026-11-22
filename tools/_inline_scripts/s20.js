
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
  var session = 'site-' + Math.random().toString(36).slice(2, 10);
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
    s = s.replace(/(https?:\/\/[^\s<]+)/g, function (url) {
      // Запятая и точка в конце адреса — это пунктуация текста, а не часть ссылки.
      var match = url.match(/^(.*?)([.,;:!?)\]]*)$/);
      var clean = match ? match[1] : url;
      var tail = match ? match[2] : '';
      return '<a href="' + clean + '" target="_blank" rel="noopener">' + clean + '</a>' + tail;
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

  function renderClarification(node, payload) {
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
        .map(function (item, position) { return item ? (questions[position].question + ' ' + item) : ''; })
        .filter(function (value) { return value; });
      if (ready.length) ask(ready.join('\n'), { hidden: true });
    }

    function render() {
      var item = questions[index] || {};
      step.textContent = 'Вопрос ' + (index + 1) + ' из ' + questions.length;
      title.textContent = item.question || '';
      field.value = answers[index] || '';
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
      next.disabled = !(answers[index] || field.value.trim());
      next.textContent = index === questions.length - 1 ? 'Готово' : 'Далее';
    }

    next.addEventListener('click', function () {
      var value = (field.value || '').trim();
      if (value) answers[index] = value;
      if (!answers[index]) { field.focus(); return; }
      if (index === questions.length - 1) { finish(); return; }
      index += 1;
      render();
    });

    back.addEventListener('click', function () {
      if (index > 0) { index -= 1; render(); }
    });

    field.addEventListener('input', function () {
      next.disabled = !(field.value.trim() || answers[index]);
    });

    field.addEventListener('keydown', function (event) {
      if (event.key === 'Enter') { event.preventDefault(); next.click(); }
    });

    close.addEventListener('click', function () {
      closed = true;
      stop();
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
    state.question = question;
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
              bot.innerHTML = '<p>' +
                escapeHtml(state.text.slice(0, state.shown)).replace(/\n/g, '<br>') +
                '</p><span class="ug-cursor"></span>';
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
          renderClarification(survey_host, state.clarification);
        } catch (error) {
          var fallback = document.createElement('div');
          fallback.className = 'ug-cl';
          fallback.textContent = (state.clarification.questions || [])
            .map(function (item) { return item.question; }).join(' · ');
          bot.appendChild(fallback);
        }
      }
      var asked = String(state.question || '').trim().toLowerCase();
      var pool = (state.chips && state.chips.length) ? state.chips : DEFAULT_QUESTIONS;
      state.chips = pool.filter(function (item) {
        var text = typeof item === 'string' ? item : (item && (item.question || item.text)) || '';
        return String(text).trim().toLowerCase() !== asked;
      });
      if (state.clarification) state.chips = [];
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
      var response = await fetch((base || '') + '/api/chat', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          message: question,
          session_id: session,
          show_notes: false,
          use_cache: true,
          mode: options.mode || chooseMode(question),
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
            if (!label && event.n) label = 'Шаг ' + event.n + (event.max ? ' из ' + event.max : '');
            if (label) {
              state.status = label;
              if (!state.done && !state.text) {
                bot.innerHTML = '<span class="ug-msg__typing">' + escapeHtml(label) + '</span>';
              }
            }
          } else if (event.type === 'sources' && event.items) {
            state.sources = event.items;
          } else if (event.type === 'clarification') {
            state.clarification = event;
            state.done = true;
          } else if (event.type === 'done') {
            if (event.text) state.text = event.text;
            if (event.sources) state.sources = event.sources;
            if (Array.isArray(event.followups)) state.chips = event.followups;
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
