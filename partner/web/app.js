/* Partner-Agent — клиент чата: история из SQLite, SSE-стриминг, видимое рассуждение. */

const state = {
  sessionId: null,
  sessions: [],
  streaming: false,
  controller: null,
  health: null,
  stickToBottom: true,
  showNotes: true,
  useCache: true,
  clarificationActive: false,
  mode: 'thinking',
  questionNavFrame: null,
  questionScrollFrame: null,
  questionNavClosed: false,
  chatStarted: false,
  questionLockIndex: null,
  questionLockTimer: null,
};

const NOTES_KEY = 'partner.notes';
const CACHE_KEY = 'partner.cache';
const MODE_KEY = 'partner.mode.v2';

const $ = (sel) => document.querySelector(sel);
const threadEl = $('#thread');
const emptyEl = $('#empty');
const inputEl = $('#input');
const formEl = $('#composer');
const sendBtn = $('#sendBtn');
const stopBtn = $('#stopBtn');
const sessionsEl = $('#sessions');
const questionNavEl = $('#questionNav');
const questionListEl = $('#questionList');
const questionCountEl = $('#questionCount');
const questionRailEl = $('#questionRail');
const questionCloseEl = $('#questionClose');
const questionToggleEl = $('#questionToggle');

let BRAND_AVATAR = 'PA';

function applyBranding(profile) {
  const branding = (profile && profile.branding) || {};
  if (branding.title) document.title = branding.title;
  const mark = document.querySelector('.brand-mark');
  if (mark && branding.avatar) mark.textContent = branding.avatar;
  const name = document.querySelector('.brand-name');
  if (name && branding.brand) name.textContent = branding.brand;
  const heading = document.querySelector('#empty h1');
  if (heading && branding.heading) heading.textContent = branding.heading;
  const subtitle = document.querySelector('#empty p');
  if (subtitle && branding.subtitle) subtitle.textContent = branding.subtitle;
  if (Array.isArray(branding.typing_examples) && branding.typing_examples.length) {
    TYPING_EXAMPLES = branding.typing_examples
      .map((item) => String(item || '').trim())
      .filter(Boolean)
      .slice(0, 20);
    startPlaceholderTyping();
  } else if (branding.placeholder && !state.chatStarted) {
    inputEl.placeholder = branding.placeholder;
  }
  if (Array.isArray(branding.examples) && branding.examples.length) {
    EXAMPLE_QUESTIONS = branding.examples;
    renderExamples();
  }
  if (branding.avatar) {
    BRAND_AVATAR = branding.avatar;
    const mark = document.getElementById('emptyMark');
    if (mark) mark.textContent = branding.avatar;
  }
  if (branding.accent) {
    document.documentElement.style.setProperty('--brand-accent', branding.accent);
  }
}

let EXAMPLE_QUESTIONS = [
  "Чем занимается компания и какие у неё продукты?",
  "Какие условия сотрудничества и как начать работу?",
  "Кто отвечает за продажи и как с ним связаться?",
  "Какие новости и обновления были за последнее время?",
];

let TYPING_EXAMPLES = [
  "Какие направления обучения есть?",
  "Сколько стоит Python-разработчик?",
  "Есть ли рассрочка на обучение?",
  "Подберите курс для новичка",
  "Как проходит обучение?",
  "Нужно обучение для IT-команды",
  "Есть программы для школьников?",
  "Как записаться на консультацию?",
  "Помогите выбрать профессию в IT",
  "Какие форматы обучения доступны?",
  "Сколько длится обучение?",
  "Можно ли учиться онлайн?",
  "Есть ли бесплатный вводный курс?",
  "Поможете с трудоустройством?",
  "Какие документы выдают после курса?",
  "Сколько стоит корпоративное обучение?",
  "Кто преподаватели на курсах?",
  "Как проходит поступление?",
  "Можно ли совмещать обучение с работой?",
  "Есть ли программа для ребёнка 14 лет?",
];
let typingTimer = null;
let typingIndex = 0;
let typingPosition = 0;
let typingDeleting = false;
let typingRunning = false;

function stopPlaceholderTyping() {
  typingRunning = false;
  if (typingTimer) {
    clearTimeout(typingTimer);
    typingTimer = null;
  }
}

const CHAT_PLACEHOLDER = 'Сообщение Ассистенту';

function markChatStarted() {
  if (state.chatStarted) return;
  state.chatStarted = true;
  stopPlaceholderTyping();
  inputEl.placeholder = CHAT_PLACEHOLDER;
}

function startPlaceholderTyping() {
  if (state.chatStarted) return;
  stopPlaceholderTyping();
  if (!TYPING_EXAMPLES.length) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    inputEl.placeholder = TYPING_EXAMPLES[0];
    return;
  }
  if (inputEl.value) return;
  typingRunning = true;
  typingIndex = 0;
  typingPosition = 0;
  typingDeleting = false;
  inputEl.placeholder = '';
  typingTimer = setTimeout(typingTick, 350);
}

function typingTick() {
  if (!typingRunning) return;
  const phrase = TYPING_EXAMPLES[typingIndex % TYPING_EXAMPLES.length] || '';
  if (!phrase) {
    stopPlaceholderTyping();
    return;
  }
  if (!typingDeleting) {
    typingPosition = Math.min(phrase.length, typingPosition + 1);
    inputEl.placeholder = phrase.slice(0, typingPosition);
    if (typingPosition >= phrase.length) {
      typingDeleting = true;
      typingTimer = setTimeout(typingTick, 2100);
    } else {
      typingTimer = setTimeout(typingTick, 34 + Math.random() * 24);
    }
    return;
  }
  typingPosition = Math.max(0, typingPosition - 1);
  inputEl.placeholder = phrase.slice(0, typingPosition);
  if (typingPosition <= 0) {
    typingDeleting = false;
    typingIndex = (typingIndex + 1) % TYPING_EXAMPLES.length;
    typingTimer = setTimeout(typingTick, 420);
  } else {
    typingTimer = setTimeout(typingTick, 18 + Math.random() * 10);
  }
}

/* ------------------------------------------------------------------ */
/* markdown                                                            */
/* ------------------------------------------------------------------ */
function clientText(text) {
  return String(text || '')
    .replace(/`[^`\n]+\.(?:md|txt|pdf|docx|html?|json)`/gi, '')
    .replace(/\s*\((?:[^()\n]*?\.(?:md|txt|pdf|docx|html?|json))\)/gi, '')
    .replace(/^\s*Источник(?:и)?\s*:.*$/gim, '')
    .replace(/[ \t]{2,}/g, ' ')
    .replace(/\s+([.,;:!?])/g, '$1')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function escapeHtml(text) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function imageFigure(alt, url) {
  const src = url.replace(/&amp;/g, '&');
  return `<figure class="inline-shot"><img src="${src}" alt="${alt}" data-full="${src}" loading="lazy" referrerpolicy="no-referrer" title="${alt || 'Открыть'}"></figure>`;
}

function inlineMarkup(text) {
  let out = text;
  out = out.replace(/`([^`\n]+)`/g, (_, code) => `<code>${code}</code>`);
  out = out.replace(
    /!\[([^\]]*)\]\((https?:\/\/[^\s)]+)\)/g,
    (_, alt, url) => imageFigure(alt, url)
  );
  out = out.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
  out = out.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    (_, label, url) =>
      `<a href="${url.replace(/&amp;/g, '&')}" target="_blank" rel="noopener">${label}</a>`
  );
  return out;
}

function inlineImageUrls(text) {
  const urls = new Set();
  String(text || '').replace(
    /!\[[^\]]*\]\((https?:\/\/[^\s)]+)\)/g,
    (_, url) => {
      urls.add(url.replace(/&amp;/g, '&'));
      return '';
    }
  );
  return urls;
}

const NUMERIC_CELL = /^[\d\s.,%+\u2013\u2014-]+$/;

function splitTableRow(line) {
  const trimmed = line.trim().replace(/^\|/, '').replace(/\|$/, '');
  return trimmed.split('|').map((cell) => cell.trim());
}

function isTableSeparator(line) {
  return /^\|?[\s:|-]+\|?$/.test(line.trim()) && line.includes('-');
}

function buildTable(lines, start) {
  const header = splitTableRow(lines[start]);
  let index = start + 2;
  const rows = [];
  while (index < lines.length && lines[index].trim().startsWith('|')) {
    rows.push(splitTableRow(lines[index]));
    index += 1;
  }

  const headHtml = header
    .map((cell) => {
      const cls = NUMERIC_CELL.test(cell) ? ' class="num"' : '';
      return `<th${cls}>${inlineMarkup(escapeHtml(cell))}</th>`;
    })
    .join('');
  const bodyHtml = rows
    .map((row) => {
      const cells = row
        .map((cell) => {
          const cls = NUMERIC_CELL.test(cell) ? ' class="num"' : '';
          return `<td${cls}>${inlineMarkup(escapeHtml(cell))}</td>`;
        })
        .join('');
      return `<tr>${cells}</tr>`;
    })
    .join('');

  return {
    html: `<div class="table-wrap"><table><thead><tr>${headHtml}</tr></thead><tbody>${bodyHtml}</tbody></table></div>`,
    next: index - 1,
  };
}

function renderProse(block) {
  const lines = block.split('\n');
  const out = [];
  let paragraph = [];
  let list = null;

  const flushParagraph = () => {
    if (paragraph.length) {
      out.push(`<p>${inlineMarkup(paragraph.join(' '))}</p>`);
      paragraph = [];
    }
  };
  const flushList = () => {
    if (list) {
      out.push(`</${list}>`);
      list = null;
    }
  };

  const imageOnly = (line) => /^!\[([^\]]*)\]\((https?:\/\/[^\s)]+)\)$/.test(line.trim());

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index].trimEnd();
    if (!line.trim()) {
      flushParagraph();
      flushList();
      continue;
    }

    // Группа картинок подряд — одна строка карточек, а не стопка блоков.
    if (imageOnly(line)) {
      flushParagraph();
      flushList();
      const figures = [];
      while (index < lines.length) {
        const current = lines[index].trim();
        const match = current.match(/^!\[([^\]]*)\]\((https?:\/\/[^\s)]+)\)$/);
        if (match) {
          figures.push(imageFigure(escapeHtml(match[1]), match[2]));
          index += 1;
        } else if (!current) {
          index += 1;
        } else {
          break;
        }
      }
      index -= 1;
      out.push(`<div class="inline-row">${figures.join('')}</div>`);
      continue;
    }

    // markdown-таблица: | a | b |  с разделителем |---|---|
    if (
      line.trim().startsWith('|') &&
      index + 1 < lines.length &&
      isTableSeparator(lines[index + 1])
    ) {
      flushParagraph();
      flushList();
      const table = buildTable(lines, index);
      out.push(table.html);
      index = table.next;
      continue;
    }

    const heading = line.match(/^(#{1,4})\s+(.*)$/);
    if (heading) {
      flushParagraph();
      flushList();
      const level = heading[1].length;
      const tag = level <= 1 ? 'h1' : level === 2 ? 'h2' : level === 3 ? 'h3' : 'h4';
      out.push(`<${tag}>${inlineMarkup(escapeHtml(heading[2]))}</${tag}>`);
      continue;
    }

    const quote = line.match(/^>\s?(.*)$/);
    if (quote) {
      flushParagraph();
      flushList();
      out.push(`<blockquote>${inlineMarkup(escapeHtml(quote[1]))}</blockquote>`);
      continue;
    }

    const bullet = line.match(/^\s*[-*•]\s+(.*)$/);
    if (bullet) {
      flushParagraph();
      if (list !== 'ul') {
        flushList();
        out.push('<ul>');
        list = 'ul';
      }
      out.push(`<li>${inlineMarkup(escapeHtml(bullet[1]))}</li>`);
      continue;
    }

    const ordered = line.match(/^\s*\d+[.)]\s+(.*)$/);
    if (ordered) {
      flushParagraph();
      if (list !== 'ol') {
        flushList();
        out.push('<ol>');
        list = 'ol';
      }
      out.push(`<li>${inlineMarkup(escapeHtml(ordered[1]))}</li>`);
      continue;
    }

    flushList();
    paragraph.push(escapeHtml(line.trim()));
  }
  flushParagraph();
  flushList();
  return out.join('');
}

function renderMarkdown(text) {
  if (!text) return '';
  const parts = String(text).split(/```/);
  let html = '';
  parts.forEach((part, index) => {
    if (index % 2 === 1) {
      const code = part.replace(/^[a-zA-Z0-9_+-]*\n/, '');
      html += `<pre><code>${escapeHtml(code.replace(/\n$/, ''))}</code></pre>`;
    } else {
      html += renderProse(part);
    }
  });
  return html;
}

/* Картинки, вставленные в текст, не дублируем в ленте под ответом. */
function galleryItems(attachments, text) {
  const inline = inlineImageUrls(text);
  return (attachments || []).filter((item) => item && item.url && !inline.has(item.url));
}

function bindInlineImages(container) {
  container.querySelectorAll('figure.inline-shot img').forEach((image) => {
    image.addEventListener('click', () =>
      openLightbox(image.dataset.full || image.src, image.alt)
    );
  });
}

/* ------------------------------------------------------------------ */
/* helpers                                                             */
/* ------------------------------------------------------------------ */
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function icon(path, size = 16) {
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('width', size);
  svg.setAttribute('height', size);
  svg.setAttribute('fill', 'none');
  svg.setAttribute('stroke', 'currentColor');
  svg.setAttribute('stroke-width', '1.8');
  svg.setAttribute('stroke-linecap', 'round');
  const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
  p.setAttribute('d', path);
  svg.appendChild(p);
  return svg;
}

function plural(count, one, few, many) {
  const value = Math.abs(Number(count) || 0) % 100;
  const last = value % 10;
  if (value > 10 && value < 20) return `${count} ${many}`;
  if (last === 1) return `${count} ${one}`;
  if (last >= 2 && last <= 4) return `${count} ${few}`;
  return `${count} ${many}`;
}

function nearBottom() {
  return threadEl.scrollHeight - threadEl.scrollTop - threadEl.clientHeight < 120;
}

function scrollToBottom(force = false) {
  if (force || state.stickToBottom) threadEl.scrollTop = threadEl.scrollHeight;
  updateScrollButton();
}

function updateScrollButton() {
  const button = document.getElementById('scrollBottom');
  if (!button) return;
  const away =
    threadEl.scrollHeight - threadEl.scrollTop - threadEl.clientHeight > 260;
  button.classList.toggle('hidden', !away);
}

threadEl.addEventListener('scroll', () => {
  state.stickToBottom = nearBottom();
  updateScrollButton();
});

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const payload = await res.json();
      detail = payload.detail || payload.error || detail;
    } catch { /* ignore */ }
    throw new Error(detail);
  }
  if (res.status === 204) return null;
  return res.json();
}

/* ------------------------------------------------------------------ */
/* sessions                                                            */
/* ------------------------------------------------------------------ */
const TOOL_ICONS = {
  search_knowledge: 'M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14M16.5 16.5 21 21',
  company_profile: 'M4 20V6h16v14M9 10h6M9 14h6',
  find_product: 'M4 7l8-4 8 4v10l-8 4-8-4zM4 7l8 4 8-4M12 11v10',
  find_person: 'M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8M4 21a8 8 0 0 1 16 0',
  find_faq: 'M9 9a3 3 0 1 1 5 2c-1 1-2 1-2 3M12 18h.01',
  kb_stats: 'M4 6h16M4 12h16M4 19h10',
  plan: 'M4 6h16M4 12h10M4 18h7',
  default: 'M12 8v8M8 12h8',
};

function groupLabel(iso) {
  const date = new Date(iso.endsWith('Z') || iso.includes('+') ? iso : iso + 'Z');
  const now = new Date();
  const startOfDay = (d) => new Date(d.getFullYear(), d.getMonth(), d.getDate());
  const diff = Math.round((startOfDay(now) - startOfDay(date)) / 86400000);
  if (Number.isNaN(diff)) return 'Ранее';
  if (diff <= 0) return 'Сегодня';
  if (diff === 1) return 'Вчера';
  if (diff < 7) return 'На этой неделе';
  return 'Ранее';
}

function renderSessions() {
  sessionsEl.innerHTML = '';
  if (!state.sessions.length) {
    sessionsEl.appendChild(el('div', 'session-group', 'Пока пусто'));
    return;
  }

  let currentGroup = null;
  state.sessions.forEach((session) => {
    const group = groupLabel(session.updated_at);
    if (group !== currentGroup) {
      sessionsEl.appendChild(el('div', 'session-group', group));
      currentGroup = group;
    }

    const row = el('button', 'session');
    row.type = 'button';
    if (session.id === state.sessionId) row.classList.add('active');
    row.title = session.title;
    row.appendChild(el('span', 'title', session.title));

    const actions = el('span', 'actions');

    const renameBtn = el('button', 'icon-btn');
    renameBtn.type = 'button';
    renameBtn.title = 'Переименовать';
    renameBtn.appendChild(icon('M12 20h9M16.5 3.5a2.1 2.1 0 013 3L7 19l-4 1 1-4z', 14));
    renameBtn.addEventListener('click', async (event) => {
      event.stopPropagation();
      const title = window.prompt('Название чата', session.title);
      if (!title || title.trim() === session.title) return;
      try {
        await api(`/api/sessions/${session.id}`, {
          method: 'PATCH',
          body: JSON.stringify({ title: title.trim() }),
        });
        await loadSessions();
        if (session.id === state.sessionId) $('#topbarTitle').textContent = title.trim();
      } catch (err) {
        window.alert(`Не удалось переименовать: ${err.message}`);
      }
    });

    const deleteBtn = el('button', 'icon-btn');
    deleteBtn.type = 'button';
    deleteBtn.title = 'Удалить';
    deleteBtn.appendChild(icon('M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14', 14));
    deleteBtn.addEventListener('click', async (event) => {
      event.stopPropagation();
      if (!window.confirm(`Удалить чат «${session.title}»?`)) return;
      try {
        await api(`/api/sessions/${session.id}`, { method: 'DELETE' });
        if (state.sessionId === session.id) startNewChat();
        await loadSessions();
      } catch (err) {
        window.alert(`Не удалось удалить: ${err.message}`);
      }
    });

    actions.append(renameBtn, deleteBtn);
    row.appendChild(actions);
    row.addEventListener('click', () => openSession(session.id));
    sessionsEl.appendChild(row);
  });
}

async function loadSessions() {
  try {
    state.sessions = await api('/api/sessions');
  } catch {
    state.sessions = [];
  }
  renderSessions();
}

function startNewChat() {
  setClarificationActive(false);
  state.chatStarted = false;
  state.sessionId = null;
  state.stickToBottom = true;
  // Не очищаем threadEl целиком: пустое состояние с примерами должно остаться.
  threadEl.querySelectorAll('.msg, .thread-error').forEach((node) => node.remove());
  if (!threadEl.contains(emptyEl)) threadEl.appendChild(emptyEl);
  emptyEl.style.display = '';
  emptyEl.classList.remove('hidden');
  renderExamples();
  startPlaceholderTyping();
  $('#topbarTitle').textContent = 'Новый чат';
  history.replaceState({}, '', location.pathname);
  renderSessions();
  inputEl.focus();
}

function clearThread() {
  threadEl.querySelectorAll('.msg, .thread-error').forEach((node) => node.remove());
  emptyEl.classList.add('hidden');
}
function scheduleQuestionNav() {
  if (!questionNavEl || state.questionNavFrame) return;
  state.questionNavFrame = requestAnimationFrame(() => {
    state.questionNavFrame = null;
    renderQuestionNav();
  });
}

function setQuestionActive(active) {
  if (!questionListEl) return;
  questionListEl.querySelectorAll('.question-link').forEach((button, index) => {
    const isActive = index === active;
    button.classList.toggle('active', isActive);
    if (isActive) button.setAttribute('aria-current', 'true');
    else button.removeAttribute('aria-current');
  });
  if (questionRailEl) {
    questionRailEl.querySelectorAll('.rail-mark').forEach((mark, index) => {
      mark.classList.toggle('active', index === active);
    });
  }
}

function updateQuestionNavActive() {
  if (!questionListEl) return;
  const questions = [...threadEl.querySelectorAll('.msg.user')];
  if (!questions.length) return;
  if (state.questionLockIndex !== null) {
    setQuestionActive(state.questionLockIndex);
    return;
  }
  const atBottom =
    threadEl.scrollHeight - threadEl.scrollTop - threadEl.clientHeight < 12;
  if (atBottom) {
    setQuestionActive(questions.length - 1);
    return;
  }
  const threshold = threadEl.getBoundingClientRect().top + 96;
  let active = 0;
  questions.forEach((node, index) => {
    if (node.getBoundingClientRect().top <= threshold) active = index;
  });
  setQuestionActive(active);
}

function syncQuestionNavVisibility(hasQuestions) {
  if (!questionNavEl) return;
  const has = Boolean(hasQuestions);
  if (!has) {
    questionNavEl.classList.add('hidden');
    if (questionToggleEl) questionToggleEl.classList.add('hidden');
    return;
  }
  if (state.questionNavClosed) {
    questionNavEl.classList.add('hidden');
    if (questionToggleEl) questionToggleEl.classList.remove('hidden');
  } else {
    questionNavEl.classList.remove('hidden');
    if (questionToggleEl) questionToggleEl.classList.add('hidden');
  }
}

function setQuestionNavOpen(open) {
  state.questionNavClosed = !open;
  const has = questionListEl && questionListEl.children.length > 0;
  syncQuestionNavVisibility(has);
}

function renderQuestionNav() {
  if (!questionNavEl || !questionListEl) return;
  const questions = [...threadEl.querySelectorAll('.msg.user')]
    .map((node) => {
      const bubble = node.querySelector('.bubble');
      return { node, bubble, text: String((bubble && bubble.textContent) || '').trim() };
    })
    .filter((item) => item.text);

  questionNavEl.classList.toggle('has-questions', questions.length > 0);
  if (questionCountEl) questionCountEl.textContent = questions.length ? String(questions.length) : '';
  questionListEl.innerHTML = '';
  if (questionRailEl) questionRailEl.innerHTML = '';

  questions.forEach((item, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'question-link';
    button.title = item.text;

    const text = document.createElement('span');
    text.className = 'question-text';
    text.textContent = item.text;
    button.append(text);

    button.addEventListener('click', () => {
      state.questionLockIndex = index;
      setQuestionActive(index);
      if (state.questionLockTimer) clearTimeout(state.questionLockTimer);
      state.questionLockTimer = setTimeout(() => {
        state.questionLockIndex = null;
        state.questionLockTimer = null;
        updateQuestionNavActive();
      }, 720);
      const target = item.bubble || item.node;
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      target.classList.remove('question-focus');
      void target.offsetWidth;
      target.classList.add('question-focus');
      setTimeout(() => target.classList.remove('question-focus'), 950);
    });
    questionListEl.appendChild(button);

    if (questionRailEl) {
      const mark = document.createElement('span');
      mark.className = 'rail-mark';
      questionRailEl.appendChild(mark);
    }
  });
  updateQuestionNavActive();
  syncQuestionNavVisibility(questions.length > 0);
}

threadEl.addEventListener(
  'scroll',
  () => {
    if (state.questionScrollFrame) return;
    state.questionScrollFrame = requestAnimationFrame(() => {
      state.questionScrollFrame = null;
      updateQuestionNavActive();
    });
  },
  { passive: true },
);

/* ------------------------------------------------------------------ */
/* messages                                                            */
/* ------------------------------------------------------------------ */
function addUserMessage(text) {
  markChatStarted();
  const wrap = el('div', 'msg user');
  wrap.appendChild(el('div', 'bubble', text));
  threadEl.appendChild(wrap);
  scheduleQuestionNav();
  scrollToBottom(true);
}

function buildAssistantMessage() {
  const wrap = el('div', 'msg assistant');
  wrap.appendChild(el('div', 'avatar', BRAND_AVATAR));

  const body = el('div', 'body');

  const genStatus = el('div', 'gen-status hidden');
  const genText = el('span', 'gen-text', 'Думаю…');
  genStatus.appendChild(genText);
  body.appendChild(genStatus);

  const modeBadge = el('div', 'mode-badge hidden');
  if (state.showNotes) body.appendChild(modeBadge);

  const reasoning = document.createElement('details');
  reasoning.className = 'reasoning live';
  reasoning.open = true;
  const summary = el('summary');
  const chevron = el('span', 'chevron');
  chevron.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>';
  summary.appendChild(chevron);
  summary.appendChild(el('span', 'reasoning-label', 'Размышление'));
  summary.appendChild(el('span', 'reasoning-time', ''));
  const reasoningBody = el('div', 'reasoning-body');
  reasoning.append(summary, reasoningBody);
  reasoning.addEventListener('toggle', () => {
    reasoning.dataset.userToggled = '1';
  });

  const steps = document.createElement('details');
  steps.className = 'steps hidden';
  const stepsSummary = el('summary');
  const stepsChevron = el('span', 'chevron');
  stepsChevron.innerHTML = '<svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>';
  stepsSummary.appendChild(stepsChevron);
  const stepsLabel = el('span', 'steps-label', 'Действия');
  stepsSummary.appendChild(stepsLabel);
  const stepsList = el('ul', 'steps-list');
  steps.append(stepsSummary, stepsList);
  steps.addEventListener('toggle', () => {
    steps.dataset.userToggled = '1';
  });

  const answer = el('div', 'answer');
  const gallery = el('div', 'gallery hidden');
  const followups = el('div', 'followups hidden');
  const clarify = el('div', 'clarify hidden');
  const sources = el('div', 'sources hidden');
  const tokens = el('div', 'token-badge hidden');
  const cacheBadge = el('div', 'cache-badge hidden');
  cacheBadge.innerHTML = '<span class="cache-dot"></span><span>из кэша</span>';
  const actions = el('div', 'msg-actions');

  const copyBtn = el('button', 'icon-btn');
  copyBtn.type = 'button';
  copyBtn.title = 'Скопировать ответ';
  copyBtn.appendChild(icon('M9 9h10v12H9zM5 15H3V3h12v2', 14));
  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(answer.innerText);
      copyBtn.classList.add('copied');
      setTimeout(() => copyBtn.classList.remove('copied'), 1200);
    } catch { /* clipboard может быть недоступен */ }
  });
  actions.appendChild(copyBtn);

  if (state.showNotes) body.append(reasoning, steps);
  body.append(answer, gallery, followups, clarify);
  if (state.showNotes) body.append(sources, tokens);
  body.append(cacheBadge, actions);
  wrap.appendChild(body);

  return {
    wrap, body, reasoning, reasoningBody, steps, stepsList, stepsLabel,
    answer, gallery, followups, clarify, sources, tokens, cacheBadge, actions, modeBadge,
    genStatus, genText,
  };
}

function showCacheBadge(ui, sourceQuestion) {
  if (!ui.cacheBadge) return;
  ui.cacheBadge.classList.remove('hidden');
  ui.cacheBadge.title = sourceQuestion
    ? `Сохранённый ответ на вопрос: «${sourceQuestion}»`
    : 'Сохранённый ответ из кэша';
}

function fallbackFollowups(text) {
  const body = String(text || '').toLowerCase();
  if (body.length < 180) return [];
  if (/тариф|стоим|цен/.test(body)) {
    return ['Что входит в тариф?', 'Чем тарифы отличаются?', 'Как получить расчёт?'];
  }
  if (/пилот|внедрен|миграц/.test(body)) {
    return ['Сколько длится внедрение?', 'Что нужно подготовить?', 'Кто отвечает за запуск?'];
  }
  if (/интеграц|1с|gps|трекер/.test(body)) {
    return ['Какие интеграции есть?', 'Как настроить интеграцию?', 'Как с вами связаться?'];
  }
  return ['Расскажите подробнее о продуктах', 'Как проходит пилот?', 'Как с вами связаться?'];
}

function setClarificationActive(active) {
  state.clarificationActive = active;
  document.body.classList.toggle('clarifying', active);
}

function clarificationQuestions(data) {
  if (Array.isArray(data.questions) && data.questions.length) {
    return data.questions
      .map((item) => ({
        question: String((item && item.question) || '').trim(),
        options: ((item && item.options) || [])
          .map((option) => String(option || '').trim())
          .filter(Boolean)
          .slice(0, 3),
        placeholder: String((item && item.placeholder) || '').trim(),
      }))
      .filter((item) => item.question && item.options.length >= 2)
      .slice(0, 10);
  }
  if (data.question) {
    return [{
      question: String(data.question).trim(),
      options: (data.options || [])
        .map((option) => String(option || '').trim())
        .filter(Boolean)
        .slice(0, 3),
      placeholder: String(data.placeholder || '').trim(),
    }];
  }
  return [];
}

function renderClarification(ui, data, meta = {}) {
  const box = ui.clarify;
  if (!box) return;
  const questions = clarificationQuestions(data);
  box.innerHTML = '';
  box.classList.remove('hidden');
  if (!questions.length) return;

  if (meta.answered) {
    box.classList.add('hidden');
    setClarificationActive(false);
    return;
  }

  ui.answer.classList.add('hidden');
  if (ui.genStatus) ui.genStatus.classList.add('hidden');
  if (ui.modeBadge) ui.modeBadge.classList.add('hidden');
  if (ui.reasoning) ui.reasoning.classList.add('hidden');
  if (ui.steps) ui.steps.classList.add('hidden');
  if (ui.sources) ui.sources.classList.add('hidden');
  if (ui.followups) ui.followups.classList.add('hidden');
  if (ui.gallery) ui.gallery.classList.add('hidden');
  setClarificationActive(true);

  const answers = questions.map(() => '');
  let index = 0;

  const card = el('div', 'clarify-card');
  const close = el('button', 'clarify-close', '×');
  close.type = 'button';
  close.title = 'Закрыть опрос и сразу ответить';
  close.setAttribute('aria-label', 'Закрыть опрос и сразу ответить');
  card.appendChild(close);
  card.appendChild(el('div', 'clarify-kicker', 'Уточним детали'));
  if (data.intro) card.appendChild(el('div', 'clarify-intro', String(data.intro)));
  const progress = el('div', 'clarify-progress', '');
  card.appendChild(progress);
  const step = el('div', 'clarify-step');
  card.appendChild(step);

  const actions = el('div', 'clarify-actions');
  const back = el('button', 'clarify-back', 'Назад');
  back.type = 'button';
  const next = el('button', 'clarify-submit', 'Далее');
  next.type = 'button';
  actions.append(back, next);
  card.appendChild(actions);

  const finish = () => {
    if (state.streaming) return;
    if (answers.some((answer) => !String(answer).trim())) return;
    const text = questions
      .map((item, i) => `${item.question} ${answers[i].trim()}`)
      .join('\n');
    ui.clarify.classList.add('hidden');
    ui.clarify.innerHTML = '';
    setClarificationActive(false);
    if (ui.wrap) ui.wrap.remove();
    sendMessage(text, { hidden: true });
  };

  const skip = () => {
    if (state.streaming) return;
    const bubbles = threadEl.querySelectorAll('.msg.user .bubble');
    const original = bubbles.length
      ? String(bubbles[bubbles.length - 1].textContent || '').trim()
      : '';
    const lines = [];
    if (original) lines.push(`Исходный вопрос: ${original}`);
    questions.forEach((item, i) => {
      const answer = String(answers[i] || '').trim();
      if (answer) lines.push(`${item.question} ${answer}`);
    });
    lines.push('Клиент закрыл опрос. Ответь на исходный вопрос без дополнительных уточнений.');
    ui.clarify.classList.add('hidden');
    ui.clarify.innerHTML = '';
    setClarificationActive(false);
    if (ui.wrap) ui.wrap.remove();
    sendMessage(lines.join('\n'), { hidden: true });
  };
  close.addEventListener('click', skip);

  const goNext = () => {
    if (!String(answers[index]).trim()) return;
    if (index >= questions.length - 1) {
      finish();
      return;
    }
    index += 1;
    paint();
  };

  function paint() {
    const item = questions[index];
    progress.textContent = `Вопрос ${index + 1} из ${questions.length}`;
    back.hidden = index === 0;
    next.textContent = index === questions.length - 1 ? 'Готово' : 'Далее';
    next.disabled = !String(answers[index]).trim();

    step.innerHTML = '';
    step.appendChild(el('div', 'clarify-q', item.question));

    const list = el('div', 'clarify-options');
    const input = document.createElement('input');
    input.type = 'text';
    input.maxLength = 300;
    input.placeholder = item.placeholder || 'Свой вариант…';
    input.setAttribute('aria-label', `Ответ на вопрос ${index + 1}`);
    input.value = item.options.includes(answers[index]) ? '' : answers[index];

    const refresh = () => {
      list.querySelectorAll('.clarify-option').forEach((button) => {
        button.classList.toggle('selected', button.textContent === answers[index]);
      });
      next.disabled = !String(answers[index]).trim();
    };

    const choose = (value) => {
      answers[index] = String(value || '').trim();
      input.value = '';
      refresh();
    };

    item.options.forEach((option) => {
      const button = el('button', 'clarify-option', option);
      button.type = 'button';
      button.addEventListener('click', () => choose(option));
      list.appendChild(button);
    });
    step.appendChild(list);

    const custom = el('div', 'clarify-custom');
    custom.appendChild(input);
    input.addEventListener('input', () => {
      answers[index] = input.value;
      list.querySelectorAll('.clarify-option').forEach((button) => button.classList.remove('selected'));
      next.disabled = !String(answers[index]).trim();
    });
    input.addEventListener('keydown', (event) => {
      if (event.key === 'Enter') {
        event.preventDefault();
        goNext();
      }
    });
    step.appendChild(custom);
    refresh();

    step.classList.remove('enter');
    void step.offsetWidth;
    step.classList.add('enter');
    setTimeout(() => input.focus(), 30);
  }

  back.addEventListener('click', () => {
    if (index === 0) return;
    index -= 1;
    paint();
  });
  next.addEventListener('click', goNext);

  box.appendChild(card);
  paint();
}
function renderFollowups(ui, items) {
  const box = ui.followups;
  if (!box) return;
  const unique = [];
  const seen = new Set();
  (items || []).forEach((item) => {
    const text = String(item || '').trim();
    if (!text || seen.has(text.toLowerCase())) return;
    seen.add(text.toLowerCase());
    unique.push(text);
  });
  if (!unique.length) {
    box.classList.add('hidden');
    return;
  }
  box.innerHTML = '';
  box.classList.remove('hidden');

  const all = unique.slice(0, 8);
  const addButton = (text, index) => {
    const btn = el('button', 'followup', text);
    btn.type = 'button';
    btn.style.setProperty('--i', String(index));
    btn.addEventListener('click', () => {
      if (state.streaming) return;
      state.stickToBottom = true;
      sendMessage(text);
    });
    box.appendChild(btn);
  };

  all.slice(0, 4).forEach((text, index) => addButton(text, index));

  if (all.length > 4) {
    const more = el('button', 'followup more', `Показать ещё ${all.length - 4}`);
    more.type = 'button';
    more.addEventListener('click', () => {
      more.remove();
      all.slice(4).forEach((text, index) => addButton(text, 4 + index));
    });
    box.appendChild(more);
  }
}

/* ------------------------------------------------------------------ */
/* gallery & lightbox                                                  */
/* ------------------------------------------------------------------ */
function openLightbox(url, title) {
  const box = $('#lightbox');
  const img = $('#lightboxImg');
  img.src = url;
  img.alt = title || '';
  box.classList.remove('hidden');
}

function closeLightbox() {
  $('#lightbox').classList.add('hidden');
  $('#lightboxImg').removeAttribute('src');
}

function renderGallery(container, items) {
  if (!container) return;
  const unique = [];
  const seen = new Set();
  (items || []).forEach((item) => {
    const url = (item && item.url) || '';
    if (!url || seen.has(url)) return;
    seen.add(url);
    unique.push(item);
  });
  if (!unique.length) return;

  container.classList.remove('hidden');
  container.innerHTML = '';

  const row = el('div', 'gallery-row');
  unique.forEach((item) => {
    const figure = el('figure', 'shot');
    const image = document.createElement('img');
    image.src = item.url.replace(/imw=\d+/, 'imw=637');
    image.alt = item.title || '';
    image.loading = 'lazy';
    image.referrerPolicy = 'no-referrer';
    image.title = item.title || 'Открыть';
    image.addEventListener('click', () => openLightbox(item.url, item.title));
    figure.appendChild(image);
    row.appendChild(figure);
  });
  container.appendChild(row);
  scrollToBottom();
}

function renderSources(container, items) {
  if (!items || !items.length) return;
  container.classList.remove('hidden');
  container.innerHTML = '';

  const details = document.createElement('details');
  const summary = el('summary');
  summary.appendChild(icon('M4 6h16M4 12h16M4 18h10', 13));
  summary.appendChild(el('span', null, `Источники (${items.length})`));
  details.appendChild(summary);

  const list = el('div', 'source-list');
  items.forEach((item) => {
    const card = el('div', 'source');
    const head = el('div', 's-head');
    head.appendChild(el('span', 's-kind', item.kind || 'doc'));
    head.appendChild(el('span', 's-title', item.title || item.id));
    if (item.score) head.appendChild(el('span', 's-score', Number(item.score).toFixed(3)));
    card.appendChild(head);
    card.appendChild(el('div', 's-excerpt', item.excerpt || ''));
    list.appendChild(card);
  });

  details.appendChild(list);
  container.appendChild(details);
}

function updateStepsLabel(ui) {
  const total = ui.stepsList.children.length;
  const running = ui.stepsList.querySelectorAll('.step.running').length;
  ui.stepsLabel.textContent = running ? 'Действия · выполняется' : `Действия · ${total}`;
}

function appendStep(ui, id, name, text) {
  if (!state.showNotes) return null;
  const row = el('li', 'step running');
  row.dataset.step = id;
  const ico = el('span', 's-ico');
  ico.appendChild(icon(TOOL_ICONS[name] || TOOL_ICONS.default, 12));
  row.appendChild(ico);
  row.appendChild(el('span', 's-text', text));
  row.appendChild(el('span', 's-status', '…'));
  ui.stepsList.appendChild(row);
  ui.steps.classList.remove('hidden');
  ui.steps.open = true;
  updateStepsLabel(ui);
  scrollToBottom();
  return row;
}

function finishStep(ui, id, summary, failed = false) {
  const row = ui.stepsList.querySelector(`[data-step="${id}"]`);
  if (!row) return;
  row.classList.remove('running');
  row.classList.add(failed ? 'fail' : 'done');
  const status = row.querySelector('.s-status');
  if (status) status.textContent = failed ? '!' : '✓';
  if (summary) row.title = summary;
  updateStepsLabel(ui);
}

function renderStoredMessage(message, meta = {}) {
  if (message.hidden) return;
  if (message.role === 'user') {
    addUserMessage(message.content);
    return;
  }

  const ui = buildAssistantMessage();
  threadEl.appendChild(ui.wrap);

  const askCall = (message.tool_calls || []).find(
    (call) => call && call.name === 'ask_clarification',
  );
  if (askCall) {
    if (meta.answered) {
      ui.wrap.remove();
      return;
    }
    const args = askCall.arguments || {};
    ui.answer.innerHTML = '';
    renderClarification(ui, args, meta);
    scrollToBottom(true);
    return;
  }

  if (message.reasoning) {
    ui.reasoning.classList.remove('live');
    ui.reasoning.open = false;
    ui.reasoningBody.textContent = message.reasoning;
  } else {
    ui.reasoning.remove();
  }

  if (message.tool_calls && message.tool_calls.length) {
    message.tool_calls.forEach((call, index) => {
      if (call.name === 'plan' || call.name === 'offer_followups') return;
      const stepId = `stored-${index}`;
      const text = (call.reason || '').trim() || call.name;
      appendStep(ui, stepId, call.name, text);
      finishStep(ui, stepId, call.summary);
    });
    ui.steps.open = false;
  }

  const visible = state.showNotes ? message.content : clientText(message.content);
  ui.answer.innerHTML = renderMarkdown(visible);
  bindInlineImages(ui.answer);
  renderGallery(ui.gallery, galleryItems(message.attachments, message.content));
  const storedFollowups = [];
  (message.tool_calls || []).forEach((call) => {
    if (call.name !== 'offer_followups') return;
    const args = call.arguments || {};
    (args.items || []).forEach((item) => storedFollowups.push(item));
  });
  if (!storedFollowups.length) {
    storedFollowups.push(...fallbackFollowups(message.content));
  }
  renderFollowups(ui, storedFollowups);
  renderSources(ui.sources, message.sources);
  if (message.tokens) setTokenBadge(ui, Number(message.tokens));
  if (message.cached) showCacheBadge(ui, null);
  scrollToBottom(true);
}

/* ------------------------------------------------------------------ */
/* chat streaming                                                      */
/* ------------------------------------------------------------------ */
const TOOL_STATUS = {
  plan: 'Составляю план…',
  search_knowledge: 'Ищу в материалах…',
  company_profile: 'Открываю профиль компании…',
  find_product: 'Смотрю продукты…',
  find_person: 'Проверяю команду…',
  find_faq: 'Читаю частые вопросы…',
  kb_stats: 'Считаю состав базы…',
  offer_followups: 'Подбираю варианты…',
  ask_clarification: 'Формулирую уточнение…',
};

function setTokenBadge(ui, usage) {
  if (!ui || !ui.tokens || !state.showNotes) return;
  const value = typeof usage === 'number' ? { total_tokens: usage } : (usage || {});
  const total = Number(value.total_tokens || 0);
  if (!total) {
    ui.tokens.classList.add('hidden');
    return;
  }
  const prompt = Number(value.prompt_tokens || 0);
  const completion = Number(value.completion_tokens || 0);
  const calls = Number(value.calls || 0);
  ui.tokens.textContent = `Токенов: ${total.toLocaleString('ru-RU')}`;
  ui.tokens.title = [
    prompt ? `prompt: ${prompt.toLocaleString('ru-RU')}` : '',
    completion ? `completion: ${completion.toLocaleString('ru-RU')}` : '',
    calls ? `запросов: ${calls}` : '',
  ].filter(Boolean).join(' · ');
  ui.tokens.classList.remove('hidden');
}

function setGenStatus(ui, text, fresh = false) {
  if (!ui || !ui.genText || ui._statusClosed) return;
  const node = ui.genText;
  const next = String(text || '').trim();
  if (!next) return;
  ui.genStatus.classList.remove('hidden', 'done');
  if (fresh || !node.textContent || node.textContent === 'Думаю…') {
    node.textContent = next;
    return;
  }
  if (node.textContent === next) return;
  if (ui._statusTimer) clearTimeout(ui._statusTimer);
  node.classList.add('swap');
  ui._statusTimer = setTimeout(() => {
    node.textContent = next;
    node.classList.remove('swap');
    ui._statusTimer = null;
  }, 110);
}

function hideGenStatus(ui) {
  if (!ui || !ui.genStatus || ui._statusClosed) return;
  ui._statusClosed = true;
  if (ui._statusTimer) {
    clearTimeout(ui._statusTimer);
    ui._statusTimer = null;
  }
  ui.genStatus.classList.add('leaving');
  setTimeout(() => ui.genStatus.classList.add('hidden'), 180);
}

function toolStatus(name) {
  if (!state.showNotes) return 'Проверяю информацию…';
  return TOOL_STATUS[name] || 'Читаю данные…';
}

function setBusy(busy) {
  state.streaming = busy;
  sendBtn.disabled = busy;
  sendBtn.classList.toggle('hidden', busy);
  stopBtn.classList.toggle('hidden', !busy);
  inputEl.disabled = busy;
  $('#thinkingHint').classList.add('hidden');
  formEl.classList.toggle('busy', busy);
  if (!busy) inputEl.focus();
}

function addErrorBox(message) {
  const box = el('div', 'thread-error error-box', message);
  const wrap = el('div', 'msg assistant');
  wrap.appendChild(el('div', 'avatar', '!'));
  const body = el('div', 'body');
  body.appendChild(box);
  wrap.appendChild(body);
  threadEl.appendChild(wrap);
  scrollToBottom(true);
}

async function sendMessage(text, options = {}) {
  const question = text.trim();
  const hidden = Boolean(options && options.hidden);
  if (!question || state.streaming) return;
  markChatStarted();

  emptyEl.classList.add('hidden');
  if (!hidden) addUserMessage(question);
  state.stickToBottom = true;

  const ui = buildAssistantMessage();
  ui.actions.classList.add('hidden');
  threadEl.appendChild(ui.wrap);
  setGenStatus(ui, 'Думаю…', true);
  scrollToBottom(true);

  let planText = '';
  let reasoningText = '';
  let answerText = '';
  let attachmentsBuffer = [];
  let frame = null;

  const paintAnswer = () => {
    frame = null;
    ui.answer.classList.add('streaming');
    const visible = state.showNotes ? answerText : clientText(answerText);
    ui._rendered = visible;
    ui.answer.innerHTML =
      renderMarkdown(visible) + '<span class="stream-caret" aria-hidden="true"></span>';
    bindInlineImages(ui.answer);
    const items = galleryItems(attachmentsBuffer, answerText);
    if (items.length) renderGallery(ui.gallery, items);
    scrollToBottom();
  };
  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(paintAnswer);
  };

  let reasoningFrame = null;
  let reasoningStarted = 0;
  let reasoningTimer = null;
  const tickReasoning = () => {
    const node = ui.reasoning.querySelector('.reasoning-time');
    if (!node || !reasoningStarted) return;
    node.textContent = `${Math.round((Date.now() - reasoningStarted) / 1000)} с`;
  };
  const startReasoningClock = () => {
    if (reasoningStarted) return;
    reasoningStarted = Date.now();
    reasoningTimer = setInterval(tickReasoning, 500);
  };
  const stopReasoningClock = () => {
    if (reasoningTimer) clearInterval(reasoningTimer);
    reasoningTimer = null;
  };
  const paintReasoning = () => {
    reasoningFrame = null;
    if (!state.showNotes) return;
  const content = [planText, reasoningText].filter(Boolean).join('\n\n');
    ui.reasoningBody.textContent = content;
    ui.reasoningBody.classList.toggle('has-text', Boolean(content));
    if (content) ui.reasoning.classList.remove('hidden');
    ui.reasoningBody.scrollTop = ui.reasoningBody.scrollHeight;
    scrollToBottom();
  };
  const setReasoning = () => {
    startReasoningClock();
    if (!reasoningFrame) reasoningFrame = requestAnimationFrame(paintReasoning);
  };

  setBusy(true);
  state.controller = new AbortController();
  let finished = false;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: question,
        session_id: state.sessionId,
        show_notes: state.showNotes,
        use_cache: state.useCache,
        mode: state.mode,
        hidden,
      }),
      signal: state.controller.signal,
    });

    if (!res.ok) {
      let detail = `HTTP ${res.status}`;
      try {
        const payload = await res.json();
        detail = payload.detail || detail;
      } catch { /* ignore */ }
      throw new Error(detail);
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let split;
      while ((split = buffer.indexOf('\n\n')) !== -1) {
        const block = buffer.slice(0, split);
        buffer = buffer.slice(split + 2);
        for (const line of block.split('\n')) {
          if (!line.startsWith('data:')) continue;
          const raw = line.slice(5).trim();
          if (!raw) continue;
          let event;
          try {
            event = JSON.parse(raw);
          } catch {
            continue;
          }
          handleEvent(event);
        }
      }
    }
  } catch (err) {
    if (err.name === 'AbortError') {
      answerText += answerText ? '\n\n_остановлено пользователем_' : '_остановлено пользователем_';
    } else {
      ui.wrap.remove();
      addErrorBox(`Не удалось получить ответ: ${err.message}`);
    }
  } finally {
    if (frame) cancelAnimationFrame(frame);
    stopReasoningClock();
    ui.reasoning.classList.remove('live');
    if (reasoningText || planText) {
      ui.reasoning.open = ui.reasoning.dataset.userToggled === '1' ? ui.reasoning.open : false;
    } else {
      ui.reasoning.remove();
    }
    if (ui.stepsList.children.length) {
      ui.steps.open = ui.steps.dataset.userToggled === '1' ? ui.steps.open : false;
      updateStepsLabel(ui);
    }
    if (answerText) {
      ui.answer.classList.remove('streaming');
      const visible = state.showNotes ? answerText : clientText(answerText);
      if (ui._rendered === visible) {
        // Ответ уже отрисован стримом — убираем каретку без повторного рендера.
        ui.answer.querySelectorAll('.stream-caret').forEach((node) => node.remove());
      } else {
        ui.answer.innerHTML = renderMarkdown(visible);
        bindInlineImages(ui.answer);
        ui.answer.classList.add('settled');
      }
      const items = galleryItems(attachmentsBuffer, answerText);
      if (items.length) renderGallery(ui.gallery, items);
      finished = true;
    } else if (!finished) {
      ui.answer.innerHTML = '';
    }
    if (!ui._clarified) hideGenStatus(ui);
    setBusy(false);
    state.controller = null;
    scrollToBottom();
  }

  function handleEvent(event) {
    switch (event.type) {
      case 'clarification': {
        setGenStatus(ui, 'Уточняю пару деталей…');
        ui._clarified = true;
        renderClarification(ui, event);
        break;
      }
      case 'start': {
        if (event.answer_mode === 'fast') {
          setGenStatus(ui, 'Готовлю быстрый ответ…');
        } else if (event.answer_mode === 'clarify') {
          setGenStatus(ui, 'Уточняю пару деталей…');
        } else {
          setGenStatus(ui, 'Думаю…');
        }
        if (ui.modeBadge && state.showNotes) {
          const chosen = event.answer_mode === 'fast'
            ? 'быстрый ответ'
            : (event.answer_mode === 'clarify' ? 'уточнение' : 'глубокий разбор');
          ui.modeBadge.textContent = event.auto ? `Авто · ${chosen}` : '';
          ui.modeBadge.classList.toggle('hidden', !event.auto);
          ui.modeBadge.title = event.complexity || '';
        }
        break;
      }
      case 'session': {
        setGenStatus(ui, 'Думаю…');
        const isNew = !state.sessionId;
        state.sessionId = event.id;
        $('#topbarTitle').textContent = event.title || 'Чат';
        history.replaceState({}, '', `?session=${event.id}`);
        if (isNew) loadSessions();
        break;
      }
      case 'plan': {
        setGenStatus(ui, 'Составляю план…');
        const steps = event.steps || [];
        if (steps.length) {
          planText = `План:\n${steps.map((step, index) => `${index + 1}. ${step}`).join('\n')}`;
          setReasoning();
          const stepId = `plan-${Date.now()}`;
          appendStep(ui, stepId, 'plan', `составил план: ${steps.length} шага`);
          finishStep(ui, stepId, steps.join(' · '));
        }
        break;
      }
      case 'cache': {
        setGenStatus(ui, 'Достаю сохранённый ответ…');
        showCacheBadge(ui, event.question);
        break;
      }
      case 'reasoning_delta': {
        setGenStatus(ui, 'Размышляю…');
        reasoningText += event.text;
        setReasoning();
        break;
      }
      case 'tool_call': {
        setGenStatus(ui, toolStatus(event.name));
        if (event.name === 'plan' || event.name === 'offer_followups') break;
        const reason = (event.reason || '').trim();
        const args = event.arguments || {};
        const hint = reason || [event.name, args.name || args.query || ''].join(' ').trim();
        appendStep(ui, event.id, event.name, hint);
        break;
      }
      case 'tool_result': {
        setGenStatus(ui, 'Проверяю факты…');
        if (event.name === 'plan' || event.name === 'offer_followups') break;
        const failed = /ошибка|не найден/i.test(event.summary || '');
        finishStep(ui, event.id, event.summary, failed);
        if (event.sources && event.sources.length) renderSources(ui.sources, event.sources);
        break;
      }
      case 'delta': {
        if (!ui._writing) {
          ui._writing = true;
          hideGenStatus(ui);
        }
        answerText += event.text;
        schedule();
        break;
      }
      case 'sources': {
        if (event.items && event.items.length) renderSources(ui.sources, event.items);
        break;
      }
      case 'attachments': {
        if (event.items && event.items.length) {
          attachmentsBuffer = event.items;
          renderGallery(ui.gallery, galleryItems(attachmentsBuffer, answerText));
        }
        break;
      }
      case 'done': {
        if (event.clarification) break;
        ui.actions.classList.remove('hidden');
        hideGenStatus(ui);
        answerText = event.text || answerText;
        if (event.reasoning) reasoningText = event.reasoning;
        if (event.attachments) attachmentsBuffer = event.attachments;
        setReasoning();
        const items = galleryItems(attachmentsBuffer, answerText);
        if (items.length) renderGallery(ui.gallery, items);
        if (event.sources && event.sources.length) renderSources(ui.sources, event.sources);
        setTokenBadge(ui, event.usage_total || event.usage);
        renderFollowups(ui, event.followups);
        break;
      }
      case 'error': {
        addErrorBox(event.message || 'Неизвестная ошибка');
        break;
      }
      default:
        break;
    }
  }
}

/* ------------------------------------------------------------------ */
/* session loading                                                     */
/* ------------------------------------------------------------------ */
async function openSession(sessionId) {
  if (state.streaming) return;
  setClarificationActive(false);
  // Флаг читаем до replaceState: ниже URL перезаписывается и параметр бы потерялся.
  const wantExpand = new URLSearchParams(location.search).get('expand') === '1';
  try {
    const session = await api(`/api/sessions/${sessionId}`);
    state.sessionId = session.id;
    clearThread();
    $('#topbarTitle').textContent = session.title;
    history.replaceState({}, '', `?session=${session.id}`);

    if (!session.messages.length) {
      emptyEl.classList.remove('hidden');
    }
    session.messages.forEach((message, index) => {
      let meta = {};
      const hasAsk = (message.tool_calls || []).some(
        (call) => call && call.name === 'ask_clarification',
      );
      if (message.role === 'assistant' && hasAsk) {
        const nextUser = session.messages
          .slice(index + 1)
          .find((item) => item.role === 'user');
        if (nextUser) meta = { answered: true, choice: nextUser.content };
      }
      renderStoredMessage(message, meta);
    });
    if (session.messages.length) markChatStarted();
    else {
      state.chatStarted = false;
      startPlaceholderTyping();
    }
    scheduleQuestionNav();
    if (wantExpand) {
      threadEl.querySelectorAll('details.steps').forEach((node) => {
        node.open = true;
        node.dataset.userToggled = '1';
      });
    }
    scrollToBottom(true);
    renderSessions();
    closeSidebar();
  } catch (err) {
    addErrorBox(`Не удалось открыть чат: ${err.message}`);
  }
}

/* ------------------------------------------------------------------ */
/* health                                                              */
/* ------------------------------------------------------------------ */
async function loadHealth() {
  try {
    try {
      const profile = await api('/api/agent/profile');
      applyBranding(profile);
    } catch { /* профиль необязателен */ }

    const health = await api('/api/health');
    state.health = health;

    $('#modelChip').textContent = health.model;
    $('#modeDot').className = `dot ${health.mode === 'demo' ? 'demo' : ''}`;
    $('#modeText').textContent = health.mode === 'demo'
      ? 'демо-режим (нет модели)'
      : (health.provider === 'ollama'
        ? 'локальная Qwen · Ollama'
        : (health.thinking ? 'DeepSeek · thinking' : 'DeepSeek API'));

    const kb = [
      plural(health.chunks, 'фрагмент', 'фрагмента', 'фрагментов'),
      plural(health.products, 'продукт', 'продукта', 'продуктов'),
      `${health.chunks.toLocaleString('ru-RU')} чанков`,
    ];
    $('#kbLine').textContent = kb.join(' · ');
    $('#kbLine').title = `${health.embedding}\nВекторов: ${health.vectors}\nКомпания: ${health.company}`;
  } catch (err) {
    $('#modeText').textContent = 'сервер недоступен';
    $('#modeDot').className = 'dot demo';
    $('#kbLine').textContent = err.message;
  }
}

/* ------------------------------------------------------------------ */
/* layout                                                              */
/* ------------------------------------------------------------------ */
function openSidebar() {
  document.body.classList.add('sidebar-open');
  document.body.classList.remove('sidebar-hidden');
  $('#backdrop').classList.remove('hidden');
}
function closeSidebar() {
  document.body.classList.remove('sidebar-open');
  $('#backdrop').classList.add('hidden');
}

function applyNotesMode() {
  const hidden = !state.showNotes;
  document.documentElement.classList.toggle('notes-off', hidden);
  document.body.classList.toggle('notes-off', hidden);
}

function renderExamples() {
  const box = $('#examples');
  box.innerHTML = '';
  EXAMPLE_QUESTIONS.forEach((question) => {
    const btn = el('button', 'example', question);
    btn.type = 'button';
    btn.addEventListener('click', () => {
      inputEl.value = question;
      autoResize();
      formEl.requestSubmit();
    });
    box.appendChild(btn);
  });
}

function autoResize() {
  inputEl.style.height = 'auto';
  inputEl.style.height = `${Math.min(inputEl.scrollHeight, 200)}px`;
}

/* ------------------------------------------------------------------ */
/* theme                                                               */
/* ------------------------------------------------------------------ */
const THEME_PARAM = new URLSearchParams(location.search).get('theme');
const THEME_KEY = 'partner.theme';
const darkQuery = window.matchMedia('(prefers-color-scheme: dark)');

function paintTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const button = document.getElementById('themeToggle');
  if (button) {
    button.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
    button.setAttribute(
      'aria-label',
      theme === 'dark' ? 'Включить светлую тему' : 'Включить тёмную тему',
    );
    button.title = theme === 'dark' ? 'Светлая тема' : 'Тёмная тема';
  }
}

function setTheme(theme, persist = true) {
  paintTheme(theme);
  if (persist) {
    try { localStorage.setItem(THEME_KEY, theme); } catch { /* приватный режим */ }
  }
}

function applyTheme() {
  const saved = THEME_PARAM || localStorage.getItem(THEME_KEY);
  setTheme(saved || (darkQuery.matches ? 'dark' : 'light'), false);
}

document.getElementById('themeToggle')?.addEventListener('click', () => {
  const current = document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
  if (new URL(location.href).searchParams.has('theme')) {
    const url = new URL(location.href);
    url.searchParams.delete('theme');
    history.replaceState({}, '', url.pathname + url.search + url.hash);
  }
  setTheme(current === 'dark' ? 'light' : 'dark');
});

if (typeof darkQuery.addEventListener === 'function') {
  darkQuery.addEventListener('change', () => {
    if (!THEME_PARAM && !localStorage.getItem(THEME_KEY)) applyTheme();
  });
}
applyTheme();

/* ------------------------------------------------------------------ */
/* init                                                                */
/* ------------------------------------------------------------------ */
const notesToggle = $('#notesToggle');
state.showNotes = localStorage.getItem(NOTES_KEY) !== '0';
notesToggle.checked = state.showNotes;
applyNotesMode();
notesToggle.addEventListener('change', () => {
  state.showNotes = notesToggle.checked;
  localStorage.setItem(NOTES_KEY, state.showNotes ? '1' : '0');
  applyNotesMode();
  if (!state.streaming && state.sessionId) openSession(state.sessionId);
});

const cacheToggle = $('#cacheToggle');
state.useCache = localStorage.getItem(CACHE_KEY) !== '0';
if (cacheToggle) {
  cacheToggle.checked = state.useCache;
  cacheToggle.addEventListener('change', () => {
    state.useCache = cacheToggle.checked;
    localStorage.setItem(CACHE_KEY, state.useCache ? '1' : '0');
  });
}

const modeSwitch = $('#modeSwitch');
const savedMode = localStorage.getItem(MODE_KEY);
state.mode = ['auto', 'fast', 'thinking'].includes(savedMode) ? savedMode : 'auto';
const paintMode = () => {
  if (!modeSwitch) return;
  modeSwitch.querySelectorAll('.mode-option').forEach((button) => {
    button.classList.toggle('active', button.dataset.mode === state.mode);
  });
  document.body.classList.toggle('fast-mode', state.mode === 'fast');
  document.body.classList.toggle('auto-mode', state.mode === 'auto');
};
paintMode();
if (modeSwitch) {
  modeSwitch.addEventListener('click', (event) => {
    const button = event.target.closest('.mode-option');
    if (!button) return;
    const picked = button.dataset.mode;
    state.mode = ['auto', 'fast', 'thinking'].includes(picked) ? picked : 'auto';
    localStorage.setItem(MODE_KEY, state.mode);
    paintMode();
  });
}

inputEl.addEventListener('input', () => {
  autoResize();
  if (inputEl.value) stopPlaceholderTyping();
  else startPlaceholderTyping();
});
inputEl.addEventListener('focus', () => {
  if (!inputEl.value) startPlaceholderTyping();
});
inputEl.addEventListener('blur', () => {
  if (!inputEl.value) startPlaceholderTyping();
});
inputEl.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    formEl.requestSubmit();
  }
});

formEl.addEventListener('submit', (event) => {
  event.preventDefault();
  const text = inputEl.value;
  if (!text.trim() || state.streaming) return;
  inputEl.value = '';
  autoResize();
  sendMessage(text);
});

stopBtn.addEventListener('click', () => state.controller?.abort());

document.getElementById('scrollBottom')?.addEventListener('click', () => {
  state.stickToBottom = true;
  scrollToBottom(true);
});

$('#newChatBtn').addEventListener('click', () => {
  if (state.streaming) return;
  startNewChat();
  closeSidebar();
});

const mobileQuery = window.matchMedia('(max-width: 860px)');

$('#menuBtn').addEventListener('click', () => {
  if (mobileQuery.matches) {
    if (document.body.classList.contains('sidebar-open')) closeSidebar();
    else openSidebar();
    return;
  }
  document.body.classList.toggle('sidebar-hidden');
});

$('#collapseBtn').addEventListener('click', () => {
  if (mobileQuery.matches) closeSidebar();
  else document.body.classList.add('sidebar-hidden');
});
$('#backdrop').addEventListener('click', closeSidebar);
$('#lightbox').addEventListener('click', (event) => {
  if (event.target.id !== 'lightboxImg') closeLightbox();
});
$('#lightboxClose').addEventListener('click', closeLightbox);

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') {
    closeSidebar();
    closeLightbox();
  }
});

(async function init() {
  renderExamples();
  startPlaceholderTyping();
  autoResize();
  await loadHealth();
  await loadSessions();

  const params = new URLSearchParams(location.search);
  const sessionId = params.get('session');
  if (sessionId) {
    await openSession(sessionId);
    return;
  }

  threadEl.appendChild(emptyEl);
  const preset = params.get('q');
  if (preset && preset.trim()) {
    inputEl.value = preset.trim();
    autoResize();
    formEl.requestSubmit();
    return;
  }
  inputEl.focus();
})();
