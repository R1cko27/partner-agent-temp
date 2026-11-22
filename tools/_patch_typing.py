"""Добавляет эффект печати (typewriter) для ответа ассистента."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

NEW_ASK = r'''  async function ask(question) {
    if (busy || !question) return;
    busy = true;
    band.classList.add('is-chat');
    addMessage('user', escapeHtml(question));
    var bot = addMessage('bot', '<span class="ug-msg__typing">Думаю</span>');
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
      renderFollowups(bot, state.chips);
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
          unique.slice(0, 6).forEach(function (item) {
            var url = item.url || item.source || '';
            if (!url) return;
            var link = document.createElement('a');
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener';
            link.textContent = item.title || url;
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
'''

CURSOR_CSS = """.ug-cursor{display:inline-block;width:7px;height:15px;margin-left:2px;vertical-align:-2px;
background:#2f4bff;animation:ugBlink 1s steps(1) infinite}
@keyframes ugBlink{0%,49%{opacity:1}50%,100%{opacity:0}}
"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    start = text.index("  async function ask(question) {")
    end = text.index("  form.addEventListener('submit'", start)
    text = text[:start] + NEW_ASK + "\n" + text[end:]
    changed.append("печать по символам")

    if ".ug-cursor" not in text:
        text = text.replace(
            "@keyframes ugIn{",
            CURSOR_CSS + "@keyframes ugIn{",
            1,
        )
        changed.append("курсор")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("сборщик:", ", ".join(changed))
    return 0


if __name__ == "__main__":
    sys.exit(main())
