"""Ссылка обязательна там, где ответ отсылает к документации."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")

METHOD = '''    # --- ссылки в тексте -------------------------------------------------
    def _attach_doc_links(
        self, answer: str, sources: Optional[Sequence[Dict[str, Any]]]
    ) -> str:
        """Если текст отсылает к документации, рядом должна стоять ссылка.

        Модель любит писать «порядок описан в документации:» и обрывать фразу.
        Тогда подставляем адрес подходящего источника из выдачи, а висящее
        двоеточие убираем.
        """
        if not answer:
            return answer
        links: List[str] = []
        for item in sources or []:
            url = str(item.get("url") or "")
            if not url.startswith("http"):
                continue
            kind = str(item.get("kind") or "")
            if kind in ("doc", "web", "product", "glossary", "about", "company") and url not in links:
                links.append(url)
        if not links:
            return answer

        # Разбиваем по предложениям, сохраняя разделители.
        parts = re.split(r"(?<=[.!?])\\s+", answer)
        result: List[str] = []
        for part in parts:
            refers = _DOC_REF_RE.search(part)
            has_link = "http" in part or "](/" in part
            if refers and not has_link:
                if part.rstrip().endswith(":"):
                    part = part.rstrip()[:-1].rstrip() + f" — {links[0]}."
                else:
                    part = part.rstrip().rstrip(".") + f" ({links[0]})."
            result.append(part)
        text = " ".join(result)
        # Висящее двоеточие в конце ответа: либо ссылка, либо убираем.
        stripped = text.rstrip()
        if stripped.endswith(":"):
            text = stripped[:-1].rstrip() + f" — {links[0]}."
        return text

'''

CALLS = (
    (
        "        answer = self._verified_answer(answer, context_sources)\n",
        "        answer = self._verified_answer(answer, context_sources)\n"
        "        answer = self._attach_doc_links(answer, context_sources)\n",
    ),
    (
        "            answer = self._verified_answer(answer, list(sources.values()))\n",
        "            answer = self._verified_answer(answer, list(sources.values()))\n"
        "            answer = self._attach_doc_links(answer, list(sources.values()))\n",
    ),
)


def main() -> int:
    text = AGENT.read_text(encoding="utf-8")
    changed = []

    if "_attach_doc_links" not in text:
        anchor = "    # --- полнота перечислений -------------------------------------------"
        text = text.replace(anchor, METHOD + anchor, 1)
        changed.append("метод _attach_doc_links")

    if "_DOC_REF_RE" not in text:
        text = text.replace(
            "DOMAIN_ONLY_RE = re.compile(",
            'DOC_REF_RE_SRC = (\n'
            '    r"(в документации|в документацию|на портале документации|в руководстве|"\n'
            '    r"описано в документации|описан в документации|см\\.\\s*документац|"\n'
            '    r"подробнее в документации|по документации)"\n'
            ')\n'
            '_DOC_REF_RE = re.compile(DOC_REF_RE_SRC, re.I)\n\n'
            "DOMAIN_ONLY_RE = re.compile(",
            1,
        )
        changed.append("регулярка отсылок")

    for old, new in CALLS:
        if old in text and new not in text:
            text = text.replace(old, new, 1)
            changed.append("вызов в сборке ответа")

    if changed:
        AGENT.write_text(text, encoding="utf-8")
        print("агент:", ", ".join(changed))
    else:
        print("изменений не требуется")
    return 0


if __name__ == "__main__":
    sys.exit(main())
