from __future__ import annotations

from dataclasses import dataclass
from math import ceil
from typing import Any
from uuid import uuid4


@dataclass(frozen=True)
class CreditEstimate:
    request_id: str
    tool_id: str
    credits: int
    input_tokens_estimated: int
    output_tokens_reserved: int
    total_tokens_estimated: int
    input_chars: int
    history_chars: int
    reason: str


BASE_CREDITS: dict[str, int] = {
    # Economic defaults: one normal AI action costs at least 10 credits.
    # Smart/Deep modes are detected separately and have higher floors.
    "chat": 10,
    "fast": 10,
    "strategy": 15,
    "seo": 12,
    "marketing": 15,
    "offer": 10,
    "swot": 18,
    "unit": 12,
    "wb_ozon_card": 18,
    "margin_calc": 12,
    "product_idea": 18,
    "product_description": 15,
    "ad_offer": 15,
    "review_reply": 10,
    "competitor_analysis": 25,
    "content_plan": 20,
    "sales_plan": 20,
    "idea_check": 18,
    "smart": 25,
    "deep": 150,
}

OUTPUT_BUDGET_TOKENS: dict[str, int] = {
    "chat": 900,
    "review_reply": 500,
    "offer": 700,
    "ad_offer": 900,
    "margin_calc": 900,
    "product_description": 1000,
    "wb_ozon_card": 1400,
    "swot": 1400,
    "content_plan": 1600,
    "sales_plan": 1600,
    "competitor_analysis": 1800,
    "strategy": 1600,
}


def estimate_tokens_from_text(text: str | None) -> int:
    """Cheap tokenizer approximation: 1 token ~= 4 UTF-8-ish characters."""
    if not text:
        return 0
    return max(1, ceil(len(str(text)) / 4))


def length_surcharge(chars: int) -> int:
    if chars <= 1500:
        return 0
    if chars <= 5000:
        return 3
    if chars <= 10000:
        return 8
    if chars <= 20000:
        return 15
    return 25


def history_surcharge(chars: int) -> int:
    if chars <= 3000:
        return 0
    if chars <= 10000:
        return 3
    return 7



MODE_FLOOR_CREDITS = {
    "fast": 10,
    "chat": 10,
    "smart": 25,
    "deep": 150,
}
WEB_SEARCH_SURCHARGE_CREDITS = 30


def mode_floor_credits(tool_id: str, model: str | None = None) -> int:
    name = f"{tool_id or ''} {model or ''}".lower()
    if any(key in name for key in ("deep", "gpt-5.5", "reason", "max")):
        return MODE_FLOOR_CREDITS["deep"]
    if any(key in name for key in ("smart", "pro", "gpt-5.4")):
        return MODE_FLOOR_CREDITS["smart"]
    return MODE_FLOOR_CREDITS["fast"]


def has_web_search(optional_fields: dict[str, Any] | None) -> bool:
    if not optional_fields:
        return False
    for key, value in optional_fields.items():
        key_l = str(key).lower()
        if key_l in {"web", "web_search", "search", "online", "internet"} and bool(value):
            return True
    return False

def model_multiplier(model: str | None) -> float:
    name = (model or "").lower()
    # Keep MVP pricing simple. Premium/heavy models can be made more expensive.
    if any(key in name for key in ("gpt-4", "claude-3-opus", "sonnet", "gemini-1.5-pro", "deepseek-r1")):
        return 1.5
    if any(key in name for key in ("free", "mini", "flash", "haiku", "small")):
        return 1.0
    return 1.2


def estimate_credits(
    tool_id: str,
    user_text: str,
    *,
    history_text: str = "",
    model: str | None = None,
    optional_fields: dict[str, Any] | None = None,
) -> CreditEstimate:
    clean_tool = (tool_id or "chat").strip() or "chat"
    input_chars = len(user_text or "")
    history_chars = len(history_text or "")
    field_chars = 0
    if optional_fields:
        field_chars = sum(len(str(value)) for value in optional_fields.values() if value is not None)
    total_input_chars = input_chars + field_chars
    input_tokens = estimate_tokens_from_text(user_text) + estimate_tokens_from_text(history_text)
    output_budget = OUTPUT_BUDGET_TOKENS.get(clean_tool, 1200)
    total_tokens = input_tokens + output_budget

    base = BASE_CREDITS.get(clean_tool, BASE_CREDITS["chat"])
    floor = mode_floor_credits(clean_tool, model)
    surcharge = length_surcharge(total_input_chars) + history_surcharge(history_chars)
    web_surcharge = WEB_SEARCH_SURCHARGE_CREDITS if has_web_search(optional_fields) else 0
    token_component = ceil((total_tokens / 1000) * model_multiplier(model))
    credits = max(floor, base + surcharge + web_surcharge + token_component)
    return CreditEstimate(
        request_id=f"req_{uuid4().hex}",
        tool_id=clean_tool,
        credits=credits,
        input_tokens_estimated=input_tokens,
        output_tokens_reserved=output_budget,
        total_tokens_estimated=total_tokens,
        input_chars=total_input_chars,
        history_chars=history_chars,
        reason=f"{clean_tool}: floor={floor}, base={base}, surcharge={surcharge}, web={web_surcharge}, token_component={token_component}",
    )


def estimate_output_tokens(answer: str | None) -> int:
    return estimate_tokens_from_text(answer)
