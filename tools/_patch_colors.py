"""Ответ в том же стиле, что вопрос; источники — контрастные цвета."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")

OLD_MSG = """.ug-msg--user{align-self:flex-end;background:rgba(255,255,255,.18);white-space:pre-wrap}
.ug-msg--bot{align-self:flex-start;background:#fff;color:#25384a}
.ug-msg--bot a{color:#0c89db}
.ug-msg--bot h3{margin:2px 0 8px;font:700 17px/1.3 "Granate","Inter",Arial,sans-serif;color:#1d2b3a}
.ug-msg--bot p{margin:0 0 10px}
.ug-msg--bot p:last-child{margin-bottom:0}
.ug-msg--bot ul{margin:6px 0 10px;padding-left:20px}
.ug-msg--bot li{margin:2px 0}
.ug-msg--bot code{background:#eef2f7;border-radius:5px;padding:1px 5px;font-size:13px}
.ug-table{overflow-x:auto;margin:10px 0}
.ug-table table{border-collapse:collapse;width:100%;font-size:14px}
.ug-table th,.ug-table td{border:1px solid #dfe6ee;padding:8px 10px;text-align:left;vertical-align:top}
.ug-table th{background:#f4f7fb;font-weight:700}"""

NEW_MSG = """.ug-msg--user,.ug-msg--bot{
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
.ug-table th{background:rgba(255,255,255,.14);font-weight:700;color:#fff}"""

OLD_SRC = """.ug-msg__sources{margin-top:10px;font-size:13px;color:#5b6b7c}
.ug-msg__sources summary{cursor:pointer;list-style:none;font-weight:600;color:#2f4bff;
display:flex;align-items:center;gap:6px;outline:none}
.ug-msg__sources summary::-webkit-details-marker{display:none}
.ug-msg__sources summary:before{content:"▸";font-size:12px;transition:transform .18s ease}
.ug-msg__sources[open] summary:before{content:"▾"}
.ug-msg__sources a{display:block;margin-top:6px;color:#0c89db;text-decoration:none;line-height:1.4}
.ug-msg__sources a:hover{text-decoration:underline}"""

NEW_SRC = """.ug-msg__sources{margin-top:10px;font-size:13px}
.ug-msg--bot .ug-msg__sources summary{cursor:pointer;list-style:none;font-weight:600;color:#fff;
display:flex;align-items:center;gap:6px;outline:none}
.ug-msg--bot .ug-msg__sources summary::-webkit-details-marker{display:none}
.ug-msg__sources--after summary::-webkit-details-marker{display:none}
.ug-msg--bot .ug-msg__sources summary:before{content:"▸";font-size:12px}
.ug-msg--bot .ug-msg__sources[open] summary:before{content:"▾"}
.ug-msg--bot .ug-msg__sources a{display:block;margin-top:6px;color:#d7e4ff;text-decoration:none;line-height:1.4}
.ug-msg--bot .ug-msg__sources a:hover{color:#fff;text-decoration:underline}
.ug-msg__sources--after summary{color:#fff}
.ug-msg__sources--after{color:rgba(255,255,255,.85)}"""


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if OLD_MSG in text:
        text = text.replace(OLD_MSG, NEW_MSG, 1)
        changed.append("единый стиль пузырей")

    if OLD_SRC in text:
        text = text.replace(OLD_SRC, NEW_SRC, 1)
        changed.append("контраст источников")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("сборщик:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
