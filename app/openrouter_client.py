from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.prompts import CHAT_SYSTEM_PROMPT, SYSTEM_PROMPT, build_user_prompt


class AIClientError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def ask_business_ai(
        self,
        mode: str,
        user_text: str,
        optional_fields: dict[str, Any] | None = None,
    ) -> str:
        if not user_text.strip():
            raise AIClientError("Пустой запрос. Опишите идею, бизнес-задачу или проблему.")

        payload = {
            "model": self.settings.openrouter_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(mode, user_text, optional_fields)},
            ],
            "temperature": 0.45,
            "max_tokens": 1600,
        }

        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.settings.webapp_public_url,
            "X-Title": "FounderPilot AI Telegram Mini App",
        }

        try:
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise AIClientError("AI-модель отвечает слишком долго. Повторите запрос позже.") from exc
        except httpx.HTTPError as exc:
            raise AIClientError(f"Ошибка сети при запросе к OpenRouter: {exc}") from exc

        if response.status_code >= 400:
            details = response.text[:800]
            raise AIClientError(f"OpenRouter вернул ошибку {response.status_code}: {details}")

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIClientError("OpenRouter вернул неожиданный формат ответа.") from exc

        if not isinstance(content, str) or not content.strip():
            raise AIClientError("AI-модель вернула пустой ответ.")

        return content.strip()

    async def ask_chat(
        self,
        history: list[dict[str, str]],
        user_message: str,
        business_context: str | None = None,
    ) -> str:
        if not user_message.strip():
            raise AIClientError("Пустое сообщение. Напишите бизнес-задачу или вопрос.")

        system_prompt = CHAT_SYSTEM_PROMPT
        if business_context:
            system_prompt = f"{system_prompt}\n\nБизнес-профиль пользователя:\n{business_context}"
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for item in history[-20:]:
            role = item.get("role")
            content = str(item.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": user_message.strip()})

        payload = {
            "model": self.settings.openrouter_model,
            "messages": messages,
            "temperature": 0.45,
            "max_tokens": 1600,
        }

        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.settings.webapp_public_url,
            "X-Title": "FounderPilot AI Chat",
        }

        try:
            async with httpx.AsyncClient(timeout=90) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise AIClientError("AI-модель отвечает слишком долго. Повторите запрос позже.") from exc
        except httpx.HTTPError as exc:
            raise AIClientError(f"Ошибка сети при запросе к OpenRouter: {exc}") from exc

        if response.status_code >= 400:
            details = response.text[:800]
            raise AIClientError(f"OpenRouter вернул ошибку {response.status_code}: {details}")

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AIClientError("OpenRouter вернул неожиданный формат ответа.") from exc

        if not isinstance(content, str) or not content.strip():
            raise AIClientError("AI-модель вернула пустой ответ.")

        return content.strip()
