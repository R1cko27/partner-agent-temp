"""Промпты, собранные из профиля компании: код не задаёт предметные правила.

Всё, что относится к компании — тон, структура ответа, цитаты, фокус, глоссарий,
CTA — приходит из `AgentProfile` (data/company/agent.json). Здесь только сборка.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from .domain.agent_profile import AgentProfile
from .engine.lang import language_rule

BREVITY_RULES = (
    "Длина: 3–4 коротких абзаца, ориентир — до 900 символов. "
    "Сразу к сути: без вступления, повтора вопроса и общих выводов. "
    "Заголовок `##` и 2–4 жирных акцента на ключевых фактах обязательны. "
    "Между абзацами — пустая строка. Сравнение продуктов оформляй таблицей до 5 строк, "
    "если без неё различие читается хуже; в остальных случаях объясняй словами."
)

FAST_BREVITY_RULES = (
    "Коротко: 2–4 предложения в 1–2 абзаца, до 500 символов. "
    "Короткий заголовок `##` и 1–2 жирных акцента. "
    "Разные мысли разделяй пустой строкой; если перечисляешь — не больше 3 пунктов."
)

SYSTEM_TEMPLATE = """{role}

{knowledge_intro}

{context}

{style_rules}

{brevity_rules}

{citation_rules}

{topic_rules}

{language_rule}

{extra_rules}

{glossary}

{cta}

Инструменты: {tools}.

Правила работы с инструментами:
1. Если в блоке «КОНТЕКСТ» уже есть факты для ответа, отвечай сразу, без инструментов; не ищи те же сущности повторно.
2. Независимые запросы — одним раундом: несколько tool_call сразу.
3. Сложный вопрос (сравнение, «сколько», «кто отвечает») — сначала plan с 2–4 шагами.
4. В каждом вызове заполняй reason — короткую фразу на языке вопроса.
5. Сначала `search_knowledge` по смыслу; точечные `find_product`/`find_person`/`find_faq` — когда вопрос про конкретную сущность.
6. Не пересказывай карточку целиком — только то, что отвечает на вопрос.
7. Если вопрос общий или неоднозначный (одна тема из многих), не угадывай: задай короткий уточняющий вопрос через `ask_clarification`.
8. Кнопки следующих вопросов формируются автоматически после ответа — отдельный инструмент для них не вызывай.
9. Если вызываешь инструменты, не пиши в этом же сообщении текст ответа — только tool_call. Ответ дай следующим сообщением, после результатов.
10. Если для ответа или действия нужны параметры, которые знает только клиент, или запрос допускает несколько равнозначных путей, не задавай вопрос текстом — вызови `ask_clarification` и задай столько вопросов, сколько нужно для полного ответа: обычно 4, для широкого запроса 5–8, максимум 10; 4 — ориентир, а не потолок. У каждого вопроса 2–3 варианта. Не спрашивай то, что уже есть в контексте; после ответов либо ответь, либо уточни недостающее.
"""

FAST_TEMPLATE = """{role}

Отвечай сразу, без рассуждений и плана.

{context}

{style_rules}

{brevity_rules}

{citation_rules}

{language_rule}

{extra_rules}

{cta}

{sections}"""


CLIENT_MODE_RULE = (
    "КЛИЕНТСКИЙ РЕЖИМ. Пиши только как консультант компании, от её лица. "
    "Запрещено упоминать материалы, документы, разделы, базу знаний, источники, "
    "выгрузку, инструменты и методы поиска. Если данных нет — скажи «уточню у коллег» "
    "или предложи контакт, без объяснения, откуда взялись факты."
)


def _fn(name: str, description: str, properties: Dict[str, Any], required: List[str]) -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


_REASON_PROP = {
    "type": "string",
    "description": "Одна короткая фраза на языке пользователя: зачем ты вызываешь этот инструмент.",
}

ALL_TOOLS: List[Dict[str, Any]] = [
    _fn(
        "plan",
        "Зафиксировать план решения. Вызывай первым шагом для сложных вопросов.",
        {
            "steps": {"type": "array", "items": {"type": "string"}, "description": "2–4 шага."},
            "reasoning": {"type": "string", "description": "Короткое обоснование плана."},
        },
        ["steps"],
    ),
    _fn(
        "search_knowledge",
        "Гибридный поиск по базе знаний компании: сайт, документы, FAQ, новости.",
        {
            "query": {"type": "string", "description": "Поисковый запрос."},
            "top_k": {"type": "integer", "description": "Сколько фрагментов вернуть (1–10)."},
        },
        ["query"],
    ),
    _fn(
        "company_profile",
        "Карточка компании: название, отрасль, описание, продукты, контакты.",
        {},
        [],
    ),
    _fn(
        "find_product",
        "Найти продукт или услугу компании по названию/описанию.",
        {"query": {"type": "string", "description": "Название или описание продукта."}},
        ["query"],
    ),
    _fn(
        "find_person",
        "Найти сотрудника компании: имя, роль, контакты.",
        {"query": {"type": "string", "description": "Имя, фамилия или роль."}},
        ["query"],
    ),
    _fn(
        "find_faq",
        "Найти ответ в частых вопросах (FAQ) компании.",
        {"query": {"type": "string", "description": "Вопрос или его часть."}},
        ["query"],
    ),
    _fn(
        "kb_stats",
        "Состав базы знаний: сколько документов, продуктов, людей, FAQ, новостей.",
        {},
        [],
    ),
    _fn(
        "ask_clarification",
        "Уточнить у клиента параметры выбора. Для общего запроса задай 2–4 вопроса; максимум 10; "
        "клиент ответит на них в одной карточке и сможет ввести свой вариант.",
        {
            "intro": {
                "type": "string",
                "description": "Короткое вступление, зачем нужны вопросы (необязательно).",
            },
            "questions": {
                "type": "array",
                "description": "Обычно 4 вопроса, для широкого запроса 5–8, максимум 10; 4 не потолок.",
                "items": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "Короткий вопрос на языке пользователя.",
                        },
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "2–3 конкретных варианта.",
                        },
                        "placeholder": {
                            "type": "string",
                            "description": "Подсказка для своего варианта.",
                        },
                    },
                    "required": ["question", "options"],
                },
            },
        },
        ["questions"],
    ),
    _fn(
        "offer_followups",
        "Предложить 2–4 вопроса, которые логично задать следующими после этого ответа. "
        "Каждый вопрос цепляется за предмет ответа: назови в нём продукт, сборку или версию, "
        "раздел, сертификат, термин либо контакт из ответа. Общие вопросы о компании, "
        "реклама и продающие темы (цена, скидки, пробный период) не подходят. "
        "Сотруднику нужны рабочие вопросы: соседние сборки и изменения, совместимость, "
        "ограничения, актуальность, где проверить, кто отвечает. Не повторяй заданный "
        "вопрос и не предлагай тем, которых нет в материалах. Если привязать вопрос "
        "не к чему — не вызывай инструмент. "
        "В обычном режиме кнопки собираются автоматически, вызывать его не нужно.",
        {
            "items": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2–4 коротких вопроса на языке пользователя.",
            }
        },
        ["items"],
    ),
]

for _tool in ALL_TOOLS:
    if _tool["function"]["name"] == "plan":
        continue
    _tool["function"]["parameters"]["properties"]["reason"] = dict(_REASON_PROP)


def tools_for(profile: AgentProfile) -> List[Dict[str, Any]]:
    """Только инструменты, разрешённые профилем компании."""
    allowed = set(profile.tools or [])
    # Кнопки-продолжения собираются локально после ответа (partner/followups.py).
    # Отдельный вызов модели — лишний шаг в потоке и повод предложить вопрос
    # не по теме, поэтому инструмент модели не показываем.
    return [
        tool
        for tool in ALL_TOOLS
        if tool["function"]["name"] in allowed
        and tool["function"]["name"] != "offer_followups"
    ]


def _context(profile: AgentProfile) -> str:
    """Первоначальный контекст кейса: для кого работаем и о чём вообще речь."""
    if not profile.context:
        return ""
    return "Что важно знать сразу:\n" + "\n".join(f"- {line}" for line in profile.context)


def _style_rules(profile: AgentProfile) -> str:
    style = profile.style
    lines = ["Как говорить:"]
    if style.heading:
        lines.append(
            "- Начни с короткого заголовка `##`: он называет предмет разговора "
            "(«Различие NGFW и WAF»), а не действие («Разбираем ваш вопрос»)."
        )
    else:
        lines.append("- Без заголовка: сразу переходи к делу.")
    lines.append(
        "- Объясняй, а не отчитывайся: сначала что это и зачем нужно, потом детали. "
        "Читатель должен понять причину, а не только вывод."
    )
    lines.append(
        "- Говори живым языком консультанта: короткие абзацы по 1–3 предложения, "
        "пустая строка между мыслями. Без канцелярита («в рамках», «осуществляется», "
        "«данный функционал»), без маркетинга («инновационный», «лучшее решение на рынке») "
        "и без штампов вроде «как известно» и «стоит отметить»."
    )
    lines.append(
        "- Термин при первом упоминании расшифровывай коротко и по-русски, "
        "если пользователь может его не знать."
    )
    lines.append(
        "- Выделяй **жирным** 2–4 действительно важных факта. "
        "Не выделяй целые абзацы и заголовки."
    )
    lines.append(
        f"- Перечисление — когда сравниваешь варианты или перечисляешь состав: "
        f"до {style.max_bullets} пунктов"
        + (" или таблица до 5 строк" if style.allow_tables else "")
        + ". В остальных случаях — связный текст."
    )
    if style.observations == 1:
        lines.append("- В конце уместно одно короткое наблюдение по существу — только на фактах.")
    elif style.observations > 1:
        lines.append(
            f"- В конце уместно до {style.observations} наблюдений по существу — только на фактах."
        )
    lines.append(
        "- Не рассуждай о себе и своих ограничениях. Запрещены формулировки вида "
        "«у меня нет», «я не нашёл», «не могу порекомендовать», «не буду придумывать», "
        "«в моей базе», «по памяти». Говори о материалах и о том, что нужно клиенту: "
        "«этих сведений в открытых материалах компании нет» — и сразу давай канал, "
        "где их подтвердят. Ответ — клиенту, а не отчёт о своей работе."
    )
    lines.append(
        "- Не комментируй состояние и качество материалов: не упоминай расхождения в данных, "
        "пометки, снимки, выгрузки, «в одной справке так, в другой иначе». Если нужно уточнить "
        "факт — назови актуальное значение и предложи официальную страницу проверки."
    )
    lines.append(
        "- Не пересказывай вопрос и не начинай с «Конечно!» или «Отличный вопрос». "
        "Не заканчивай общими словами — заканчивай по делу."
    )
    lines.append(
        "- Держи нить разговора: продолжения вроде «а где этому научиться», "
        "«а если ещё и веб-приложение» относятся к предыдущей теме — не начинай заново "
        "и не переспрашивай уже известное."
    )
    lines.append(f"- Тон: {profile.persona.tone}.")
    return "\n".join(lines)


def _citation_rules(profile: AgentProfile, show_notes: bool = True) -> str:
    if not show_notes:
        return (
            "Клиентский режим: клиенту не нужны источники и внутренние детали. "
            "Не упоминай файлы, документы, базу знаний и методы, не вставляй пути к файлам "
            "и фразы о материалах. Отвечай как консультант клиенту: уверенно, по делу, "
            "только факты. Ссылки на сайт компании и контакты можно, если они есть в контексте."
        )
    citations = profile.citations
    if not citations.required or citations.style == "none":
        return "Источники: ссылки не обязательны, но не искажай факты."
    if citations.style == "section":
        return (
            "Источники: каждый факт должен опираться на материалы; в конце ответа "
            f"добавь блок «{citations.section_title}» с 1–4 ссылками на источники."
        )
    if citations.style == "both":
        return (
            "Источники: после факта указывай источник в скобках, а в конце добавь блок "
            f"«{citations.section_title}» с 1–4 ссылками."
        )
    return (
        "Источники: после каждого существенного факта указывай источник из поля `source`: "
        "`[название](url)` для веб-страницы или `` `файл` `` для материала компании."
    )


def _topic_rules(profile: AgentProfile) -> str:
    lines: List[str] = []
    if profile.topics.focus:
        lines.append("Фокус компании: " + ", ".join(profile.topics.focus) + ".")
    if profile.topics.avoid:
        lines.append(
            "Не обсуждай темы: " + ", ".join(profile.topics.avoid)
            + ". Если спросят — вежливо скажи, что это вне базы знаний, и предложи контакт."
        )
    return "\n".join(lines)


def _language_line(profile: AgentProfile, lang: str) -> str:
    if profile.language and profile.language != "auto":
        return language_rule(profile.language)
    return language_rule(lang)


def _extra_rules(profile: AgentProfile) -> str:
    if not profile.rules:
        return ""
    return "Правила компании:\n" + "\n".join(f"- {rule}" for rule in profile.rules)


def _glossary(profile: AgentProfile) -> str:
    if not profile.glossary:
        return ""
    items = "\n".join(f"- {term}: {meaning}" for term, meaning in profile.glossary.items())
    return "Термины компании (используй эти значения):\n" + items


def _cta(profile: AgentProfile) -> str:
    if not profile.cta:
        return ""
    text = profile.cta.get("text") or ""
    contact = profile.cta.get("contact") or profile.cta.get("url") or ""
    if not text and not contact:
        return ""
    return "Если данных не хватает: " + " ".join(part for part in (text, contact) if part)


def _fallback(profile: AgentProfile) -> str:
    return f"Если данных нет — скажи: «{profile.fallback}»"


def build_system_prompt(
    stats: Dict[str, Any],
    profile: AgentProfile,
    lang: str = "ru",
    show_notes: bool = True,
    include_tools: bool = True,
) -> str:
    prompt = SYSTEM_TEMPLATE.format(
        role=profile.persona.role,
        chunks=stats.get("chunks", 0),
        audience=profile.persona.audience,
        knowledge_intro=(
            f"Ты работаешь по базе знаний компании: {stats.get('chunks', 0)} фрагментов "
            "из открытых источников и материалов, которые предоставила компания. "
            f"Аудитория: {profile.persona.audience}."
            if show_notes
            else "Ты консультируешь клиентов компании: отвечай по существу, "
            "опираясь на факты из справки, без ссылок на внутренние материалы."
        ),
        style_rules=_style_rules(profile) + "\n\n" + _fallback(profile),
        context=_context(profile),
        brevity_rules=BREVITY_RULES,
        citation_rules=_citation_rules(profile, show_notes),
        topic_rules=_topic_rules(profile),
        language_rule=_language_line(profile, lang),
        extra_rules=_extra_rules(profile),
        glossary=_glossary(profile),
        cta=_cta(profile),
        tools=", ".join(tool["function"]["name"] for tool in tools_for(profile)),
    )
    if not include_tools:
        prompt = prompt.split("\n\nИнструменты: ", 1)[0].strip()
    if not show_notes:
        prompt = prompt.rstrip() + "\n\n" + CLIENT_MODE_RULE
    return prompt.strip()


def build_fast_prompt(
    sections: str,
    profile: AgentProfile,
    lang: str = "ru",
    show_notes: bool = True,
) -> str:
    body = sections.strip() or "КОНТЕКСТ: данных по вопросу не нашлось."
    prompt = FAST_TEMPLATE.format(
        role=profile.persona.role,
        context=_context(profile),
        style_rules=_style_rules(profile) + "\n\n" + _fallback(profile),
        brevity_rules=FAST_BREVITY_RULES,
        citation_rules=_citation_rules(profile, show_notes),
        language_rule=_language_line(profile, lang),
        extra_rules=_extra_rules(profile),
        cta=_cta(profile),
        sections=f"КОНТЕКСТ:\n{body}",
    )
    return prompt


def tools_json(profile: AgentProfile) -> str:
    return json.dumps(tools_for(profile), ensure_ascii=False, indent=2)
