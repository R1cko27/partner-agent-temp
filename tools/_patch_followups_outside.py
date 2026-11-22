"""Кнопки-продолжения выносим из пузыря сообщения под него."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("tools/build_site_page4.py")


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    changed = []

    if "renderFollowups(list, chips)" not in text:
        text = text.replace("renderFollowups(bot, chips);", "renderFollowups(list, chips);", 1)
        changed.append("вызов с list")

    old_class = "row.className = 'ug-followups';"
    if old_class in text:
        text = text.replace(old_class, "row.className = 'ug-followups ug-followups--after';", 1)
        changed.append("класс строки")

    if ".ug-followups--after{" not in text:
        text = text.replace(
            ".ug-followups{display:flex;",
            ".ug-followups--after{align-self:flex-start;margin:6px 0 0 6px}\n.ug-followups{display:flex;",
            1,
        )
        changed.append("стили под сообщением")

    PATH.write_text(text, encoding="utf-8", newline="\n")
    print("правки:", ", ".join(changed) or "нечего менять")
    return 0


if __name__ == "__main__":
    sys.exit(main())
