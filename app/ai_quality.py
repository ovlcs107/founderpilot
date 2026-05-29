from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ChatIntent:
    """Small deterministic intent hint for prompt routing.

    This is not a security boundary and does not replace the model. It only helps
    the backend choose tone, max tokens and the hidden instructions for the next
    answer without an extra AI call.
    """

    key: str
    label: str
    temperature: float
    max_tokens: int
    depth: str


_GREETING_RE = re.compile(r"^(привет|здравствуй|здравствуйте|хай|йо|ку|доброе\s+утро|добрый\s+день|добрый\s+вечер|hello|hi|hey)[!.?,\s-]*$", re.I)
_BUSINESS_WORDS = {
    "бизнес", "стартап", "продажи", "маркетинг", "оффер", "воронка", "конверсия",
    "маржа", "roi", "юнит", "экономика", "wb", "wildberries", "ozon", "карточка",
    "товар", "клиент", "целевая", "аудитория", "инвестор", "презентация", "финмодель",
    "реклама", "лендинг", "подписка", "тариф", "выручка", "прибыль", "план запуска",
}
_CODE_WORDS = {
    "код", "скрипт", "python", "javascript", "typescript", "html", "css", "sql", "api",
    "backend", "frontend", "fastapi", "ошибка", "traceback", "deploy", "railway", "webhook",
}
_CALC_WORDS = {
    "посчитай", "рассчитай", "формула", "сколько", "себестоимость", "окупаемость",
    "маржа", "прибыль", "roi", "юнит", "налог", "комиссия", "%",
}
_TEXT_WORDS = {
    "перепиши", "улучши текст", "сделай текст", "письмо", "пост", "описание", "заголовок",
    "рерайт", "сократи", "сформулируй", "промпт",
}


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-zа-яё0-9_%]+", text.lower()))


def detect_chat_intent(text: str) -> ChatIntent:
    clean = (text or "").strip()
    lowered = clean.lower()
    words = _words(clean)
    if not clean:
        return ChatIntent("empty", "пустое сообщение", 0.45, 600, "short")
    if _GREETING_RE.match(clean) or (len(clean) <= 18 and words & {"привет", "хай", "йо", "ку"}):
        return ChatIntent("casual", "обычное общение", 0.65, 450, "short")
    if words & _CODE_WORDS or "```" in clean:
        return ChatIntent("code", "код/технический вопрос", 0.30, 1800, "technical")
    if words & _CALC_WORDS:
        return ChatIntent("calculation", "расчёты", 0.25, 1700, "numbers")
    if words & _BUSINESS_WORDS:
        return ChatIntent("business", "бизнес-задача", 0.40, 1800, "business")
    if words & _TEXT_WORDS:
        return ChatIntent("writing", "текст/редактура", 0.55, 1500, "writing")
    if len(clean) < 80:
        return ChatIntent("casual", "обычное общение", 0.62, 700, "short")
    return ChatIntent("general", "общий вопрос", 0.50, 1400, "normal")


def plan_answer_budget(plan_key: str | None, requested_max_tokens: int) -> int:
    plan = (plan_key or "free").lower()
    ceilings = {
        "free": 900,
        "go": 1200,
        "plus": 1700,
        "pro": 2300,
        "business": 2800,
    }
    return min(max(300, requested_max_tokens), ceilings.get(plan, 1400))


def plan_depth_text(plan_key: str | None) -> str:
    plan = (plan_key or "free").lower()
    if plan == "business":
        return "Business: отвечай как рабочий консультант для команды — больше структуры, рисков, ролей, метрик и плана внедрения."
    if plan == "pro":
        return "Pro: давай глубокий прикладной ответ, конкретные шаги, цифры, риски и варианты решений."
    if plan == "plus":
        return "Plus: отвечай подробнее среднего, с примерами и понятным планом действий."
    if plan == "go":
        return "Go: отвечай компактно, но полезно; больше практики, меньше теории."
    return "Free: отвечай кратко и полезно; не уходи в длинную консультацию без запроса пользователя."


def build_access_context(access: dict[str, Any] | None) -> str:
    if not access:
        return ""
    parts: list[str] = []
    plan = str(access.get("plan") or "free").lower()
    parts.append(f"Тариф: {plan}")
    status = access.get("status_label") or access.get("status")
    if status:
        parts.append(f"Статус доступа: {status}")
    until = access.get("subscription_until")
    if until:
        parts.append(f"Подписка до: {until}")
    daily_left = access.get("daily_remaining")
    monthly_left = access.get("monthly_remaining")
    if daily_left is not None:
        parts.append(f"Остаток дневных кредитов: {daily_left}")
    if monthly_left is not None:
        parts.append(f"Остаток месячных кредитов: {monthly_left}")
    return "\n".join(parts)


def compact_history(history: list[dict[str, Any]], *, max_messages: int = 24, max_chars: int = 12000) -> list[dict[str, str]]:
    """Return recent conversation context without letting old chats eat the prompt."""
    result: list[dict[str, str]] = []
    used = 0
    for item in list(history)[-max_messages:]:
        role = item.get("role")
        if role not in {"user", "assistant"}:
            continue
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        remaining = max_chars - used
        if remaining <= 0:
            break
        if len(content) > min(3000, remaining):
            content = content[: min(3000, remaining)].rstrip() + "…"
        used += len(content)
        result.append({"role": str(role), "content": content})
    return result


def sanitize_ai_output(text: str) -> str:
    clean = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    clean = re.sub(r"\n{4,}", "\n\n\n", clean)
    clean = re.sub(r"[ \t]+\n", "\n", clean)
    # Remove accidental model wrappers that sometimes appear around markdown answers.
    clean = re.sub(r"^```markdown\s*\n", "", clean, flags=re.I)
    clean = re.sub(r"\n```\s*$", "", clean)
    return clean.strip()


def safe_ai_error(status_code: int | None = None, details: str | None = None) -> str:
    """Convert provider errors into product-safe text for frontend users."""
    status = int(status_code or 0)
    raw = (details or "").strip()
    message = ""
    if raw:
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                err = data.get("error") or data.get("message") or data
                if isinstance(err, dict):
                    message = str(err.get("message") or err.get("code") or "")
                else:
                    message = str(err or "")
        except Exception:
            message = raw[:180]
    lower = message.lower()
    if status in {401, 403} or "auth" in lower or "api key" in lower:
        return "AI временно недоступен. Мы уже знаем о проблеме с подключением модели. Попробуйте позже."
    if status == 402 or "credit" in lower or "balance" in lower:
        return "AI временно недоступен из-за лимита провайдера. Попробуйте позже."
    if status == 429 or "rate" in lower:
        return "AI сейчас перегружен. Подождите немного и повторите запрос."
    if status in {500, 502, 503, 504}:
        return "AI-провайдер временно не отвечает. Попробуйте ещё раз через минуту."
    if status:
        return "AI временно не смог обработать запрос. Повторите попытку чуть позже."
    return "AI временно недоступен. Повторите попытку чуть позже."
