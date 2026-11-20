"""Клиент DeepSeek API на httpx: стриминг, reasoning и tool calling.

Особенности:
* `thinking: {"type": "enabled"}` включает режим рассуждений — модель отдаёт
  `reasoning_content`, который UI показывает как «Размышление»;
* если модель/эндпоинт не поддерживает `thinking`, клиент один раз повторяет
  запрос без этого поля и запоминает факт (без падения чата);
* tool_calls собираются из дельт потока по `index`;
* ретраи на 408/429/5xx и сетевые ошибки.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

import httpx

from ..config import Settings
from .logbook import write_log

RETRY_STATUSES = {408, 409, 429, 500, 502, 503, 504}
RETRY_DELAYS = (1.0, 3.0, 6.0)


class LLMError(RuntimeError):
    def __init__(self, message: str, status: Optional[int] = None) -> None:
        super().__init__(message)
        self.status = status


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: str

    def parse_arguments(self) -> Dict[str, Any]:
        if not (self.arguments or "").strip():
            return {}
        try:
            parsed = json.loads(self.arguments)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}


@dataclass
class StreamEvent:
    type: str  # delta | reasoning | tool_calls | done
    text: str = ""
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = ""
    usage: Dict[str, Any] = field(default_factory=dict)


def _friendly_error(status: int, body: str) -> LLMError:
    detail = (body or "").strip()
    try:
        payload = json.loads(body)
        detail = (
            (payload.get("error") or {}).get("message")
            or payload.get("message")
            or detail
        )
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass

    hints = {
        400: "Некорректный запрос к API",
        401: "Неверный API-ключ DeepSeek (проверьте DEEPSEEK_API_KEY в .env)",
        402: "На балансе DeepSeek недостаточно средств",
        403: "Доступ к модели запрещён для этого ключа",
        404: "Модель или эндпоинт не найдены",
        422: "API отклонил параметры запроса",
        429: "Превышен лимит запросов DeepSeek, попробуйте позже",
        500: "Внутренняя ошибка DeepSeek",
        503: "DeepSeek перегружен, попробуйте позже",
    }
    message = hints.get(status, f"Ошибка DeepSeek API ({status})")
    return LLMError(f"{message}. {detail}"[:600], status=status)


class DeepSeekClient:
    """Клиент DeepSeek API или локальной модели через Ollama.

    Оба варианта говорят на OpenAI-совместимом протоколе, поэтому отличается
    только базовый URL, имя модели и заголовок авторизации. У локальной модели
    нет reasoning_content и нет ключа API.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.local = settings.is_local
        if not self.local and not settings.api_key:
            raise LLMError("DEEPSEEK_API_KEY не задан", status=401)
        self.url = f"{settings.effective_base_url.rstrip('/')}/chat/completions"
        self.thinking_supported = bool(settings.thinking) and not self.local
        headers = {"Accept": "text/event-stream"}
        if not self.local and settings.api_key:
            headers["Authorization"] = f"Bearer {settings.api_key}"
        self._client = httpx.Client(
            timeout=httpx.Timeout(connect=20.0, read=240.0, write=60.0, pool=20.0),
            headers=headers,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._client.close()

    # --- отладка --------------------------------------------------------
    def _dump_prompt(self, payload: Dict[str, Any]) -> None:
        """Печатает в консоль полный промпт, который уходит в модель."""
        if not self.settings.log_prompts:
            return
        messages = payload.get("messages") or []
        tools = [
            (tool.get("function") or {}).get("name", "?")
            for tool in payload.get("tools") or []
        ]
        rules = "=" * 78
        lines = [
            "",
            rules,
            f"PROMPT → {payload.get('model')} · сообщений: {len(messages)} · "
            f"max_tokens: {payload.get('max_tokens')} · "
            f"temperature: {payload.get('temperature')} · tools: {', '.join(tools) or '—'}",
            rules,
        ]
        for index, message in enumerate(messages, start=1):
            role = message.get("role", "?")
            content = message.get("content") or ""
            lines.append(f"--- [{index}] {role} ---")
            lines.append(content if str(content).strip() else "(пусто)")
            for call in message.get("tool_calls") or []:
                function = call.get("function") or {}
                lines.append(f"  ↳ tool_call {function.get('name')}: {function.get('arguments')}")
            if message.get("tool_call_id"):
                lines.append(f"  ↳ ответ на tool_call_id: {message['tool_call_id']}")
        lines.append(rules)
        write_log("\n".join(lines))

    def _log_tokens(self, usage: Dict[str, Any], label: str = "ответ") -> None:
        """Печатает расход токенов одного запроса к модели."""
        if not self.settings.log_tokens or not usage:
            return
        prompt = int(usage.get("prompt_tokens") or 0)
        completion = int(usage.get("completion_tokens") or 0)
        total = int(usage.get("total_tokens") or (prompt + completion))
        cached = usage.get("prompt_cache_hit_tokens")
        if cached is None:
            cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
        reasoning = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")

        parts = [f"prompt: {prompt}"]
        if cached:
            parts.append(f"из кэша: {cached}")
        parts.append(f"completion: {completion}")
        if reasoning:
            parts.append(f"из них размышления: {reasoning}")
        parts.append(f"всего: {total}")
        write_log(f"TOKENS · {label} · " + " · ".join(parts))

    # --- запрос ---------------------------------------------------------
    def _payload(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        stream: bool,
        max_tokens: Optional[int] = None,
        allow_thinking: bool = True,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.settings.effective_model,
            "messages": messages,
            "temperature": self.settings.temperature,
            "max_tokens": max_tokens or self.settings.max_tokens,
            "stream": stream,
        }
        if stream:
            payload["stream_options"] = {"include_usage": True}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if allow_thinking and self.thinking_supported:
            payload["thinking"] = {"type": "enabled"}
        return payload

    def _open_stream(self, payload: Dict[str, Any]):
        """Открывает поток с ретраями; возвращает httpx.Response."""
        last_error: Optional[Exception] = None
        for delay in (0.0,) + RETRY_DELAYS:
            if delay:
                time.sleep(delay)
            try:
                request = self._client.build_request("POST", self.url, json=payload)
                response = self._client.send(request, stream=True)
            except httpx.HTTPError as exc:
                last_error = LLMError(f"Нет связи с DeepSeek API: {exc}")
                continue

            if response.status_code < 400:
                return response

            body = response.read().decode("utf-8", "replace")
            response.close()
            if response.status_code in RETRY_STATUSES:
                last_error = _friendly_error(response.status_code, body)
                continue
            raise _friendly_error(response.status_code, body)

        raise last_error or LLMError("Не удалось выполнить запрос к DeepSeek API")

    # --- стриминг -------------------------------------------------------
    def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tools_first: bool = True,
        allow_thinking: bool = True,
        max_tokens: Optional[int] = None,
    ) -> Iterator[StreamEvent]:
        payload = self._payload(
            messages, tools, stream=True, max_tokens=max_tokens, allow_thinking=allow_thinking
        )
        self._dump_prompt(payload)
        try:
            response = self._open_stream(payload)
        except LLMError as exc:
            # Модель может не поддерживать thinking — повторяем без него.
            if allow_thinking and self.thinking_supported and exc.status == 400 and "thinking" in str(exc).lower():
                self.thinking_supported = False
                payload = self._payload(
                    messages, tools, stream=True, max_tokens=max_tokens, allow_thinking=False
                )
                response = self._open_stream(payload)
            else:
                raise

        collected: Dict[int, Dict[str, Any]] = {}
        finish_reason = ""
        usage: Dict[str, Any] = {}

        try:
            for line in response.iter_lines():
                if not line:
                    continue
                line = line.strip()
                if line.startswith(":"):
                    continue
                if not line.startswith("data:"):
                    continue
                data = line[len("data:"):].strip()
                if data == "[DONE]":
                    break
                try:
                    packet = json.loads(data)
                except json.JSONDecodeError:
                    continue

                if isinstance(packet, dict) and packet.get("error"):
                    message = (packet["error"] or {}).get("message", "ошибка потока")
                    raise LLMError(f"DeepSeek вернул ошибку в потоке: {message}")

                if packet.get("usage"):
                    usage = packet["usage"]

                choices = packet.get("choices") or []
                if not choices:
                    continue
                choice = choices[0]
                delta = choice.get("delta") or {}

                reasoning = delta.get("reasoning_content") or delta.get("reasoning")
                if reasoning:
                    yield StreamEvent(type="reasoning", text=reasoning)

                text = delta.get("content")
                if text:
                    yield StreamEvent(type="delta", text=text)

                for call in delta.get("tool_calls") or []:
                    index = call.get("index", 0)
                    slot = collected.setdefault(index, {"id": "", "name": "", "arguments": ""})
                    if call.get("id"):
                        slot["id"] = call["id"]
                    function = call.get("function") or {}
                    if function.get("name"):
                        slot["name"] = function["name"]
                    if function.get("arguments"):
                        slot["arguments"] += function["arguments"]

                if choice.get("finish_reason"):
                    finish_reason = choice["finish_reason"]
        finally:
            response.close()

        self._log_tokens(usage, "вызов")

        calls = [
            ToolCall(
                id=slot["id"] or f"call_{index}",
                name=slot["name"],
                arguments=slot["arguments"],
            )
            for index, slot in sorted(collected.items())
            if slot["name"]
        ]
        if calls:
            yield StreamEvent(type="tool_calls", tool_calls=calls, finish_reason=finish_reason)
        yield StreamEvent(type="done", finish_reason=finish_reason, usage=usage)

    # --- обычный запрос -------------------------------------------------
    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: Optional[int] = None,
        allow_thinking: bool = True,
    ) -> Dict[str, Any]:
        payload = self._payload(
            messages, tools, stream=False, max_tokens=max_tokens, allow_thinking=allow_thinking
        )
        self._dump_prompt(payload)
        last_error: Optional[Exception] = None
        for delay in (0.0,) + RETRY_DELAYS:
            if delay:
                time.sleep(delay)
            try:
                response = self._client.post(self.url, json=payload)
            except httpx.HTTPError as exc:
                last_error = LLMError(f"Нет связи с DeepSeek API: {exc}")
                continue
            if response.status_code >= 400:
                error = _friendly_error(response.status_code, response.text)
                if response.status_code in RETRY_STATUSES:
                    last_error = error
                    continue
                if self.thinking_supported and response.status_code == 400 and "thinking" in str(error).lower():
                    self.thinking_supported = False
                    payload = self._payload(messages, tools, stream=False, max_tokens=max_tokens)
                    last_error = error
                    continue
                raise error
            try:
                data = response.json()
            except json.JSONDecodeError as exc:
                raise LLMError(f"Некорректный ответ API: {response.text[:300]}") from exc
            self._log_tokens(data.get("usage") or {}, "вызов (без стрима)")
            return data
        raise last_error or LLMError("Не удалось выполнить запрос к DeepSeek API")

    def ping(self) -> str:
        # Без thinking-параметра, но с запасом токенов: модель всё равно может
        # потратить часть лимита на reasoning_content и вернуть пустой content.
        result = self.complete(
            [
                {"role": "system", "content": "Отвечай одним словом."},
                {"role": "user", "content": "Скажи: работает"},
            ],
            max_tokens=300,
            allow_thinking=False,
        )
        choices = result.get("choices") or []
        if not choices:
            raise LLMError("Модель не вернула вариантов ответа")
        message = choices[0].get("message") or {}
        content = (message.get("content") or "").strip()
        if not content:
            raise LLMError(
                "Модель вернула пустой content: лимит токенов ушёл на рассуждение"
            )
        return content
