from __future__ import annotations

import asyncio
import logging
from typing import Any
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from app.ai_quality import (
    ChatIntent,
    build_access_context,
    compact_history,
    detect_chat_intent,
    plan_answer_budget,
    plan_depth_text,
    safe_ai_error,
    sanitize_ai_output,
)
from app.config import Settings
from app.prompts import CHAT_SYSTEM_PROMPT, SYSTEM_PROMPT, build_user_prompt


logger = logging.getLogger(__name__)


class AIClientError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def model_for_plan(self, plan_key: str | None = None) -> str:
        plan = (plan_key or "free").strip().lower()
        by_plan = {
            "free": self.settings.openrouter_model_free,
            "go": self.settings.openrouter_model_go,
            "plus": self.settings.openrouter_model_plus,
            "pro": self.settings.openrouter_model_pro,
            "business": self.settings.openrouter_model_business,
        }
        return (by_plan.get(plan) or self.settings.openrouter_model or "openrouter/free").strip()

    def candidate_models(self, primary_model: str | None) -> list[str]:
        result: list[str] = []
        primary = (primary_model or self.settings.openrouter_model or "openrouter/free").strip()
        if primary:
            result.append(primary)
        for model in self.settings.openrouter_fallback_models:
            if model and model not in result:
                result.append(model)
        return result or ["openrouter/free"]

    def _runtime_context(self) -> str:
        now = datetime.now(ZoneInfo("Europe/Moscow"))
        return (
            "Актуальный runtime-контекст FounderPilot:\n"
            f"- Текущая дата: {now:%Y-%m-%d} ({now:%d.%m.%Y}).\n"
            f"- Текущее время: {now:%H:%M} МСК.\n"
            "- Таймзона сервиса: Europe/Moscow.\n"
            "- Не считай, что сейчас 2024 год или любая другая старая дата.\n"
            "- Если пользователь спрашивает про срок, сегодня, завтра, месяц, квартал или год — используй дату из этого runtime-контекста.\n"
            "- Если вопрос зависит от свежих внешних данных, цен, законов, API или условий платежных систем, прямо скажи, что без онлайн-поиска данные могут быть неполными.\n"
            "- Ответ должен быть в безопасном Markdown: заголовки, списки, нумерованные шаги, таблицы только когда реально полезны, код в fenced code blocks, без HTML."
        )

    def _with_runtime_context(self, prompt: str) -> str:
        return f"{prompt}\n\n{self._runtime_context()}"

    def _headers(self, title: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.settings.webapp_public_url,
            "X-Title": title,
        }

    async def _post_chat_completion(self, payload: dict[str, Any], *, title: str) -> dict[str, Any]:
        if not self.settings.openrouter_api_key.strip():
            raise AIClientError("AI временно недоступен. Попробуйте позже.")

        max_retries = max(0, int(self.settings.ai_max_retries))
        timeout = max(15.0, float(self.settings.ai_request_timeout_seconds))
        retry_statuses = {408, 409, 425, 429, 500, 502, 503, 504}
        failover_statuses = {408, 409, 425, 429, 500, 502, 503, 504}
        last_error = ""
        last_status: int | None = None
        primary_model = str(payload.get("model") or "").strip()

        for model_index, model in enumerate(self.candidate_models(primary_model)):
            model_payload = dict(payload)
            model_payload["model"] = model
            for attempt in range(max_retries + 1):
                try:
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.post(self.base_url, headers=self._headers(title), json=model_payload)
                except httpx.TimeoutException:
                    last_error = "timeout"
                    last_status = None
                    if attempt < max_retries:
                        await asyncio.sleep(0.55 * (2**attempt))
                        continue
                    break
                except httpx.HTTPError as exc:
                    last_error = str(exc)
                    last_status = None
                    if attempt < max_retries:
                        await asyncio.sleep(0.55 * (2**attempt))
                        continue
                    break

                last_status = response.status_code
                if response.status_code < 400:
                    try:
                        data = response.json()
                    except ValueError as exc:
                        raise AIClientError("AI-провайдер вернул повреждённый ответ. Повторите запрос позже.") from exc
                    if not isinstance(data, dict):
                        raise AIClientError("AI-провайдер вернул неожиданный ответ. Повторите запрос позже.")
                    if model_index > 0:
                        logger.warning("OpenRouter failover succeeded with fallback model %s", model)
                    return data

                last_error = response.text[:1000]
                if response.status_code in retry_statuses and attempt < max_retries:
                    await asyncio.sleep(0.65 * (2**attempt))
                    continue
                break

            # Try the next fallback model only for temporary/provider-capacity errors.
            if last_status in failover_statuses or last_error == "timeout" or "timeout" in last_error.lower():
                logger.warning("OpenRouter model %s failed temporarily; trying fallback if available", model)
                continue
            break

        if last_error == "timeout":
            raise AIClientError("AI-модель отвечает слишком долго. Повторите запрос позже.")
        raise AIClientError(safe_ai_error(last_status, last_error))

    @staticmethod
    def _extract_answer(data: dict[str, Any]) -> str:
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIClientError("AI-провайдер вернул неожиданный формат ответа.") from exc
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    parts.append(part["text"])
                elif isinstance(part, str):
                    parts.append(part)
            content = "\n".join(parts)
        if not isinstance(content, str) or not content.strip():
            raise AIClientError("AI-модель вернула пустой ответ.")
        return sanitize_ai_output(content)

    async def ask_business_ai(
        self,
        mode: str,
        user_text: str,
        optional_fields: dict[str, Any] | None = None,
        *,
        plan_key: str | None = None,
        access_context: dict[str, Any] | None = None,
    ) -> str:
        if not user_text.strip():
            raise AIClientError("Пустой запрос. Опишите идею, бизнес-задачу или проблему.")

        model = self.model_for_plan(plan_key)
        hidden_context = {
            "founderpilot_plan_policy": plan_depth_text(plan_key),
            "founderpilot_access_state": build_access_context(access_context),
        }
        fields = dict(optional_fields or {})
        fields.update({key: value for key, value in hidden_context.items() if value})

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self._with_runtime_context(SYSTEM_PROMPT)},
                {"role": "user", "content": build_user_prompt(mode, user_text, fields)},
            ],
            "temperature": 0.42,
            "max_tokens": plan_answer_budget(plan_key, 1900),
        }

        data = await self._post_chat_completion(payload, title="FounderPilot AI Telegram Mini App")
        return self._extract_answer(data)

    async def ask_chat(
        self,
        history: list[dict[str, str]],
        user_message: str,
        business_context: str | None = None,
        *,
        plan_key: str | None = None,
        access_context: dict[str, Any] | None = None,
        intent: ChatIntent | None = None,
    ) -> str:
        if not user_message.strip():
            raise AIClientError("Пустое сообщение. Напишите вопрос или сообщение.")

        model = self.model_for_plan(plan_key)
        detected_intent = intent or detect_chat_intent(user_message)
        max_tokens = plan_answer_budget(plan_key, detected_intent.max_tokens)
        system_prompt = self._with_runtime_context(CHAT_SYSTEM_PROMPT)
        assistant_context = [
            "Внутренний контекст качества ответа:",
            f"- Распознанный тип запроса: {detected_intent.label} ({detected_intent.key}).",
            f"- Глубина ответа: {detected_intent.depth}.",
            f"- Режим качества: {self.settings.ai_answer_quality_mode}.",
            f"- {plan_depth_text(plan_key)}",
        ]
        access_text = build_access_context(access_context)
        if access_text:
            assistant_context.append("- Доступ пользователя:\n" + access_text)
        if business_context:
            assistant_context.append("- Контекст пользователя/проекта:\n" + business_context)
        assistant_context.append(
            "- Не сообщай пользователю внутренние названия тарифной политики, env, backend, model routing или токены. "
            "Используй это только для качества ответа."
        )
        system_prompt = f"{system_prompt}\n\n" + "\n".join(assistant_context)

        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        messages.extend(
            compact_history(
                history,
                max_messages=max(4, int(self.settings.ai_chat_history_messages)),
                max_chars=max(2000, int(self.settings.ai_chat_history_chars)),
            )
        )
        messages.append({"role": "user", "content": user_message.strip()})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": detected_intent.temperature,
            "max_tokens": max_tokens,
        }

        data = await self._post_chat_completion(payload, title="FounderPilot AI Chat")
        return self._extract_answer(data)
