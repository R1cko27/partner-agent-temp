"""Источники — аккуратная карточка с нумерованными строками и доменом."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

OLD_LINKS = """          unique.slice(0, 6).forEach(function (item) {
            var url = item.url || item.source || '';
            if (!url) return;
            var link = document.createElement('a');
            link.href = url;
            link.target = '_blank';
            link.rel = 'noopener';
            link.textContent = item.title || url;
            details.appendChild(link);
          });"""

NEW_LINKS = """          unique.slice(0, 6).forEach(function (item, index) {
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
            try { host.textContent = new URL(url).host.replace(/^www\\./, ''); } catch (error) { host.textContent = ''; }
            body.appendChild(title);
            if (host.textContent) body.appendChild(host);

            link.appendChild(num);
            link.appendChild(body);
            details.appendChild(link);
          });"""

CSS_OLD = """.ug-msg__sources--after{align-self:flex-start;margin:2px 0 0 6px;font-size:13px;
color:rgba(255,255,255,.8);animation:ugIn .3s ease both}
.ug-msg__sources--after summary{color:#fff}
.ug-msg__sources--after summary:before{color:#fff}
.ug-msg__sources--after a{color:#d7e4ff}
.ug-msg__sources--after a:hover{color:#fff}"""

CSS_NEW = """.ug-msg__sources--after{align-self:stretch;margin:6px 0 2px;padding:12px 16px;max-width:min(820px,100%);
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
.ug-src__num{flex:0 0 auto;width:20px;height:20px;border-radius:6px;display:grid;place-items:center;
background:rgba(255,255,255,.22);color:#fff;font-size:11px;font-weight:700;margin-top:1px}
.ug-src__body{display:flex;flex-direction:column;gap:2px;min-width:0}
.ug-src__title{color:#fff;line-height:1.35;overflow:hidden;text-overflow:ellipsis}
.ug-src__host{color:rgba(255,255,255,.55);font-size:11px;letter-spacing:.02em}"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if OLD_LINKS in text:
        text = text.replace(OLD_LINKS, NEW_LINKS, 1)
        changed.append("строки с номером и доменом")

    if CSS_OLD in text:
        text = text.replace(CSS_OLD, CSS_NEW, 1)
        changed.append("карточка источников")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("сборщик:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
