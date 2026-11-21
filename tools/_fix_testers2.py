"""Остальные замечания: кликабельные домены, повтор при пустом ответе."""

from __future__ import annotations

import io
import pathlib
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

AGENT = pathlib.Path("partner/agent.py")

HOST_METHOD = '''    def _link_bare_hosts(
        self, answer: str, sources: Optional[Sequence[Dict[str, Any]]]
    ) -> str:
        """Делает кликабельными голые домены, если знаем адрес источника.

        Тестировщик справедливо заметил: «(static.usergate.com, стр. 14)» и
        «(docs.usergate.com)» в тексте не нажимаются. Если для этого хоста есть
        адрес в найденных источниках — превращаем упоминание в ссылку.
        """
        if not answer or not sources:
            return answer
        by_host: Dict[str, str] = {}
        for item in sources:
            url = str(item.get("url") or "")
            host = _url_host(url)
            if host and url.startswith("http"):
                by_host.setdefault(host.removeprefix("www."), url)
        if not by_host:
            return answer

        def repl(match: re.Match) -> str:
            host = match.group(1)
            url = by_host.get(host.removeprefix("www."))
            if not url:
                return match.group(0)
            return f"[{host}]({url})"

        pattern = re.compile(
            r"(?<![\\w/.@-])((?:[a-z0-9-]+\\.)+(?:com|ru|org|net|io))", re.I
        )
        return pattern.sub(repl, answer)

'''

RETRY_METHOD = '''    def _retry_answer(self, question: str, context: str, lang: str) -> str:
        """Один короткий повтор, если модель вернула пустой ответ.

        Тестировщик получил «Не удалось сформулировать ответ» на сложный вопрос
        про обход DPI. Вместо отказа пробуем ещё раз с простой инструкцией.
        """
        if not self.client:
            return ""
        prompt = build_system_prompt(
            self.stats, self.profile, lang=lang, include_tools=False
        )
        prompt += (
            "\\n\\nОтветь коротко и по делу: 2–4 абзаца, только факты из контекста. "
            "Если фактов нет — скажи, что в материалах этого нет, и предложи канал связи."
        )
        messages: List[Dict[str, Any]] = [{"role": "system", "content": prompt}]
        messages.append(
            {"role": "user", "content": f"{question}\\n{context}" if context else question}
        )
        parts: List[str] = []
        try:
            for event in self.client.stream_chat(
                messages, None, allow_thinking=False, max_tokens=900
            ):
                if event.type == "delta":
                    parts.append(event.text)
        except Exception:  # noqa: BLE001
            return ""
        return sanitize_text("".join(parts).strip(), lang)

'''


def main() -> int:
    text = AGENT.read_text(encoding="utf-8")
    changed = []

    if "_link_bare_hosts" not in text:
        anchor = "    def _attach_doc_links("
        text = text.replace(anchor, HOST_METHOD + anchor, 1)
        changed.append("кликабельные домены")

    old_call = "        answer = self._attach_doc_links(answer, context_sources)"
    new_call = (
        "        answer = self._attach_doc_links(answer, context_sources)\n"
        "        answer = self._link_bare_hosts(answer, context_sources)"
    )
    if new_call not in text and old_call in text:
        text = text.replace(old_call, new_call, 1)
        changed.append("вызов доменов")

    if "_retry_answer" not in text:
        anchor = "    def _rechecked_answer("
        text = text.replace(anchor, RETRY_METHOD + anchor, 1)
        changed.append("повтор при пустом ответе")

    old_answer = '        answer = sanitize_text("".join(answer_parts).strip(), lang) or fallback_text(lang)'
    new_answer = (
        '        answer = sanitize_text("".join(answer_parts).strip(), lang)\n'
        '        if not answer:\n'
        '            answer = self._retry_answer(question, context, lang)\n'
        '        answer = answer or fallback_text(lang)'
    )
    if old_answer in text:
        text = text.replace(old_answer, new_answer, 1)
        changed.append("подключён повтор")

    AGENT.write_text(text, encoding="utf-8")
    print("агент:", ", ".join(changed) or "без изменений")
    return 0


if __name__ == "__main__":
    sys.exit(main())
