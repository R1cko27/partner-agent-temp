"""Правила стиля ответа: проверяются кодом, без модели-судьи.

Судья оценивает факты, а стиль надёжнее проверять правилами: они
воспроизводимы и не зависят от настроения модели.

    from partner.engine.style_lint import style_lint
    problems = style_lint(answer, question, expects_absent=True)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

# Разговор о себе вместо ответа клиенту.
META_PHRASES = (
    "у меня нет",
    "в моей базе",
    "по памяти",
    "не буду придумывать",
    "придумывать адрес не буду",
    "я не нашёл",
    "я не нашел",
    "не могу порекомендовать",
)

# Маркетинговые штампы и канцелярит.
BAD_STYLE = (
    "инновационн",
    "лучшее решение на рынке",
    "как известно",
    "стоит отметить",
    "в рамках",
    "осуществляется",
    "данный функционал",
)

# Начало ответа, которого не должно быть.
BAD_START = ("конечно", "отличный вопрос", "хороший вопрос", "спасибо за вопрос")

CHANNEL_RE = re.compile(r"sales@|academy@|registry-entry|usergate\.com|tel:|8\s?\d{3}", re.I)
HEADING_RE = re.compile(r"^#{2,3}\s+\S", re.M)


@dataclass
class StyleIssue:
    rule: str
    detail: str

    def as_dict(self) -> dict:
        return {"rule": self.rule, "detail": self.detail}


def style_lint(
    answer: str,
    question: str = "",
    expects_absent: bool = False,
    max_chars: int = 1400,
) -> List[StyleIssue]:
    """Возвращает список нарушений стиля (пусто — всё в порядке)."""
    text = (answer or "").strip()
    if not text:
        return [StyleIssue("пустой ответ", "модель вернула пустой текст")]

    low = text.lower()
    issues: List[StyleIssue] = []

    for phrase in META_PHRASES:
        if phrase in low:
            issues.append(StyleIssue("разговор о себе", f"«{phrase}»"))

    for phrase in BAD_STYLE:
        if phrase in low:
            issues.append(StyleIssue("штамп или канцелярит", f"«{phrase}»"))

    for phrase in BAD_START:
        if low.startswith(phrase):
            issues.append(StyleIssue("неудачное начало", f"«{phrase}…»"))
            break

    if not HEADING_RE.search(text):
        issues.append(StyleIssue("нет заголовка", "ожидается короткий заголовок ##"))

    if len(text) > max_chars:
        issues.append(StyleIssue("длинный ответ", f"{len(text)} символов при лимите {max_chars}"))

    if expects_absent and not CHANNEL_RE.search(text):
        issues.append(StyleIssue("нет официального канала", "при отсутствии данных нужен контакт компании"))

    return issues
