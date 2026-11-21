"""Обращение к LLM: OpenRouter или локальная модель (OpenAI-совместимый API)."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple

import httpx

NO_DATA = "В базе нет информации"

SYSTEM_PROMPT = (
    "Ты — ассистент по загруженным документам. Отвечай ТОЛЬКО по фрагментам из блока КОНТЕКСТ.\n"
    "Правила:\n"
    "1. Если в контексте нет ответа — ответь ровно одной фразой: «В базе нет информации». "
    "Не добавляй догадок, примеров и общих знаний.\n"
    "2. Не придумывай числа, даты, названия, версии и цены. Если чего-то нет в контексте — этого нет и в ответе.\n"
    "3. Пиши кратко и по делу, на языке вопроса.\n"
    "4. После ответа перечисли источники, из которых взяты факты, — по одному на строку, "
    "в виде «— имя файла или URL». Бери только те источники, которые есть в контексте."
)

DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"
DEFAULT_OPENROUTER_URL = "https://openrouter.ai/api/v1"
DEFAULT_LOCAL_MODEL = "qwen2.5:3b-instruct"
DEFAULT_LOCAL_URL = "http://127.0.0.1:11434/v1"


class LLMError(RuntimeError):
    """Ошибка обращения к модели с человекочитаемым текстом."""


def provider_defaults(provider: str) -> Tuple[str, str]:
    """Возвращает (base_url, model) по умолчанию для провайдера."""
    if provider == "local":
        return (
            os.environ.get("LOCAL_BASE_URL", DEFAULT_LOCAL_URL),
            os.environ.get("LOCAL_MODEL", DEFAULT_LOCAL_MODEL),
        )
    return (
        os.environ.get("OPENROUTER_BASE_URL", DEFAULT_OPENROUTER_URL),
        os.environ.get("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL),
    )


def build_context(hits: List[Dict[str, Any]]) -> str:
    """Собирает контекст из найденных фрагментов, нумеруя их для цитирования."""
    blocks: List[str] = []
    for position, hit in enumerate(hits, start=1):
        source = hit.get("source") or hit.get("title") or "без источника"
        blocks.append(f"[{position}] Источник: {source}\n{hit.get('text', '').strip()}")
    return "\n\n".join(blocks)


def chat(
    messages: List[Dict[str, str]],
    provider: str = "openrouter",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 900,
    timeout: float = 90.0,
) -> str:
    """Один вызов chat/completions. Поддерживает OpenRouter и локальный сервер."""
    default_url, default_model = provider_defaults(provider)
    base = (base_url or default_url).rstrip("/")
    model = model or default_model

    if provider == "local":
        key = api_key or os.environ.get("LOCAL_API_KEY") or "ollama"
    else:
        key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not key:
            raise LLMError(
                "Не задан OPENROUTER_API_KEY. Укажите ключ в переменной окружения "
                "или переключитесь на локальную модель."
            )

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "RAG Streamlit Prototype",
    }

    try:
        response = httpx.post(
            f"{base}/chat/completions", json=payload, headers=headers, timeout=timeout
        )
    except httpx.HTTPError as exc:
        raise LLMError(f"Не удалось связаться с моделью: {exc}") from exc

    if response.status_code != 200:
        detail = response.text[:400]
        raise LLMError(f"Модель вернула HTTP {response.status_code}: {detail}")

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, ValueError) as exc:
        raise LLMError(f"Неожиданный ответ модели: {response.text[:300]}") from exc

    return (content or "").strip()


def answer(
    question: str,
    hits: List[Dict[str, Any]],
    provider: str = "openrouter",
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 900,
) -> Dict[str, Any]:
    """Готовит ответ по найденным фрагментам.

    Если фрагментов нет — модель не вызывается вообще: гарантированно
    возвращается «В базе нет информации».
    """
    if not hits:
        return {"text": NO_DATA, "used_model": False, "context": ""}

    context = build_context(hits)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"КОНТЕКСТ:\n{context}\n\nВОПРОС: {question}\n\n"
            "Ответь по контексту. Если ответа нет — напиши ровно: «В базе нет информации».",
        },
    ]
    text = chat(
        messages,
        provider=provider,
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    # Страховка: пустой ответ модели трактуем как отсутствие данных.
    if not text:
        text = NO_DATA
    return {"text": text, "used_model": True, "context": context}
