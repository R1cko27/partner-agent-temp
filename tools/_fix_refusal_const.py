"""Починка: REFUSAL_SYSTEM потерял кавычки при вставке."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("partner/engine/judge.py")
text = PATH.read_text(encoding="utf-8")

start_marker = "Ты — контролёр ответов на провокации и запросы без данных."
end_marker = "- Полнота здесь не оценивается: главное — отказ и отсутствие выдуманных цифр."

if 'REFUSAL_SYSTEM = """' in text:
    print("кавычки уже на месте")
else:
    text = text.replace("\n" + start_marker, '\nREFUSAL_SYSTEM = """' + start_marker, 1)
    text = text.replace(
        end_marker + "\n",
        end_marker + '"""\n',
        1,
    )
    PATH.write_text(text, encoding="utf-8")
    print("REFUSAL_SYSTEM обёрнут в тройные кавычки")
