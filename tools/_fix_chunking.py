"""Блок 3: чанкование по разделам с сохранением заголовка в каждом фрагменте."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

PATH = pathlib.Path("partner/engine/chunking.py")

OLD = '''    def split_text(self, text: str) -> List[str]:
        text = _SPACE_RE.sub("\\n\\n", text.strip())
        if not text:
            return []
        if len(text) <= int(self.chunk_size * 1.15):
            return [text]
        if self._splitter is not None:
            parts = [part.strip() for part in self._splitter.split_text(text)]
            return [part for part in parts if part]
        return _fallback_split(text, self.chunk_size, self.chunk_overlap)'''

NEW = '''    def _sections(self, text: str) -> List[tuple[str, str]]:
        """Делит текст по заголовкам markdown, сохраняя название раздела."""
        matches = list(_HEADING_RE.finditer(text))
        if not matches:
            return [("", text)]
        sections: List[tuple[str, str]] = []
        if matches[0].start() > 0:
            head = text[: matches[0].start()].strip()
            if head:
                sections.append(("", head))
        for index, match in enumerate(matches):
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            title = match.group(2).strip()
            body = text[match.end():end].strip()
            sections.append((title, body))
        return sections

    def split_text(self, text: str) -> List[str]:
        text = _SPACE_RE.sub("\\n\\n", text.strip())
        if not text:
            return []
        if len(text) <= int(self.chunk_size * 1.15):
            return [text]

        sections = self._sections(text)
        if len(sections) > 1:
            # Режем по разделам: заголовок остаётся в каждом фрагменте, поэтому
            # «Кластеры → VRRP» находится по словам заголовка, а списки и
            # таблицы не разрываются между частями.
            chunks: List[str] = []
            buffer = ""
            for title, body in sections:
                block = f"{title}\\n{body}".strip() if title else body
                if not block:
                    continue
                if len(block) <= self.chunk_size:
                    if buffer and len(buffer) + len(block) + 2 <= self.chunk_size:
                        buffer = f"{buffer}\\n\\n{block}"
                    else:
                        if buffer:
                            chunks.append(buffer)
                        buffer = block
                    continue
                if buffer:
                    chunks.append(buffer)
                    buffer = ""
                if self._splitter is not None:
                    parts = [part.strip() for part in self._splitter.split_text(block)]
                else:
                    parts = _fallback_split(block, self.chunk_size, self.chunk_overlap)
                for part in parts:
                    if not part:
                        continue
                    # заголовок повторяем, если он оторвался при делении
                    if title and title not in part[:120]:
                        part = f"{title}\\n{part}"
                    chunks.append(part)
            if buffer:
                chunks.append(buffer)
            return [chunk.strip() for chunk in chunks if chunk.strip()]

        if self._splitter is not None:
            parts = [part.strip() for part in self._splitter.split_text(text)]
            return [part for part in parts if part]
        return _fallback_split(text, self.chunk_size, self.chunk_overlap)'''


def main() -> int:
    text = PATH.read_text(encoding="utf-8")
    if "_sections" in text:
        print("разрез по разделам уже включён")
        return 0
    if OLD not in text:
        print("исходный split_text не найден — правка не применена")
        return 1
    text = text.replace(OLD, NEW)
    if "_HEADING_RE" not in text:
        text = text.replace(
            "_SPACE_RE = re.compile(r\"\\n{3,}\")",
            "_SPACE_RE = re.compile(r\"\\n{3,}\")\n_HEADING_RE = re.compile(r\"(?m)^(#{1,6})\\s+(.+)$\")",
        )
    PATH.write_text(text, encoding="utf-8")
    print("чанкование по разделам включено")
    return 0


if __name__ == "__main__":
    sys.exit(main())
