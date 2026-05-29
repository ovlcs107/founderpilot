from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP, InvalidOperation
from typing import Any

from app.config import Settings


ZERO = Decimal("0")
ONE = Decimal("1")


def dec(value: Any, default: str = "0") -> Decimal:
    try:
        return Decimal(str(value if value is not None else default))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def clamp_rate(value: Any, default: str = "0") -> Decimal:
    rate = dec(value, default)
    if rate < ZERO:
        return ZERO
    if rate > Decimal("0.95"):
        return Decimal("0.95")
    return rate


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def ceil_int(value: Decimal) -> int:
    if value <= 0:
        return 0
    return int(value.to_integral_value(rounding=ROUND_CEILING))


def floor_int(value: Decimal) -> int:
    if value <= 0:
        return 0
    return int(value.to_integral_value(rounding=ROUND_FLOOR))


@dataclass(frozen=True)
class GuardedCredits:
    credits: int
    ai_cost_rub: Decimal
    credit_value_rub: Decimal
    monthly_ai_budget_rub: Decimal
    reason: str


def max_ai_cost_share(settings: Settings, plan_key: str) -> Decimal:
    """Return maximum share of net revenue that can be spent on AI for a plan.

    Format: "go:0.35,plus:0.38,pro:0.42,business:0.35,default:0.40".
    """
    raw = getattr(settings, "max_ai_cost_share_by_plan_raw", "") or ""
    fallback = clamp_rate(getattr(settings, "max_ai_cost_share", "0.40"), "0.40")
    found_default: Decimal | None = None
    for chunk in raw.replace(";", ",").split(","):
        if ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        key = key.strip().lower()
        rate = clamp_rate(value, str(fallback))
        if key == plan_key.lower():
            return rate
        if key == "default":
            found_default = rate
    return found_default if found_default is not None else fallback


def payment_fee_rate(settings: Settings, provider: str | None = None) -> Decimal:
    provider_key = str(provider or "yookassa").strip().lower()
    if provider_key in {"telegram_stars", "stars", "xtr"}:
        return clamp_rate(getattr(settings, "telegram_stars_fee_rate", "0.30"), "0.30")
    if provider_key in {"ton"}:
        return clamp_rate(getattr(settings, "ton_fee_rate", "0.02"), "0.02")
    if provider_key in {"btcpay_btc", "btc", "bitcoin"}:
        return clamp_rate(getattr(settings, "btcpay_fee_rate", "0.02"), "0.02")
    return clamp_rate(getattr(settings, "yookassa_fee_rate", getattr(settings, "payment_fee_rate", "0.035")), "0.035")


def provider_revenue_rub(settings: Settings, gross_amount: Decimal, provider: str | None = "yookassa", currency: str | None = "RUB") -> Decimal:
    """Conservative rub revenue after payment conversion, before tax/refund reserves."""
    provider_key = str(provider or "yookassa").strip().lower()
    cur = str(currency or "RUB").strip().upper()
    gross = dec(gross_amount)
    if gross <= 0:
        return ZERO
    if cur == "RUB":
        return gross
    if cur == "XTR" or provider_key in {"telegram_stars", "stars"}:
        return gross * dec(getattr(settings, "telegram_stars_rub_value", "0"))
    if cur == "TON" or provider_key == "ton":
        return gross * dec(getattr(settings, "ton_rub_rate", "0"))
    if cur == "BTC" or provider_key in {"btcpay_btc", "btc"}:
        return gross * dec(getattr(settings, "btc_rub_rate", "0"))
    return gross


def net_revenue_rub(settings: Settings, gross_amount: Decimal, provider: str | None = "yookassa", currency: str | None = "RUB") -> Decimal:
    revenue = provider_revenue_rub(settings, gross_amount, provider, currency)
    if revenue <= 0:
        return ZERO
    total_rate = (
        payment_fee_rate(settings, provider)
        + clamp_rate(getattr(settings, "tax_rate", "0.06"), "0.06")
        + clamp_rate(getattr(settings, "refund_risk_rate", "0.03"), "0.03")
    )
    if total_rate >= ONE:
        return ZERO
    return money(revenue * (ONE - total_rate))


def monthly_ai_budget_rub(settings: Settings, plan: Any, provider: str | None = "yookassa", currency: str | None = "RUB") -> Decimal:
    plan_key = str(getattr(plan, "key", "free") or "free").lower()
    if plan_key == "free":
        return money(dec(getattr(settings, "free_ai_monthly_budget_rub", "0")))
    net = net_revenue_rub(settings, dec(getattr(plan, "price_rub", "0")), provider, currency)
    return money(net * max_ai_cost_share(settings, plan_key))


def credit_value_rub(settings: Settings, plan: Any, provider: str | None = "yookassa", currency: str | None = "RUB") -> Decimal:
    monthly_limit = max(1, int(getattr(plan, "monthly_limit", 1) or 1))
    raw_value = monthly_ai_budget_rub(settings, plan, provider, currency) / Decimal(monthly_limit)
    min_value = dec(getattr(settings, "minimum_credit_value_rub", "0.01"), "0.01")
    if min_value > 0:
        return max(raw_value, min_value)
    return max(raw_value, Decimal("0.0001"))


def ai_cost_rub(settings: Settings, input_tokens: int, output_tokens: int) -> Decimal:
    model_name = str(getattr(settings, "openrouter_model", "") or "").lower()
    if not bool(getattr(settings, "estimate_free_model_cost", False)) and ("/free" in model_name or ":free" in model_name or model_name.endswith("free")):
        return ZERO
    input_m = Decimal(max(0, int(input_tokens or 0))) / Decimal(1_000_000)
    output_m = Decimal(max(0, int(output_tokens or 0))) / Decimal(1_000_000)
    usd = (
        input_m * dec(getattr(settings, "ai_input_cost_usd_per_m_tokens", "1.0"), "1.0")
        + output_m * dec(getattr(settings, "ai_output_cost_usd_per_m_tokens", "4.0"), "4.0")
    )
    usd *= ONE + clamp_rate(getattr(settings, "openrouter_fee_rate", "0.055"), "0.055")
    rub = usd * dec(getattr(settings, "usd_rub_rate", "100"), "100")
    rub *= dec(getattr(settings, "ai_cost_safety_multiplier", "2.0"), "2.0")
    return money(rub)


def guard_credits_for_margin(settings: Settings, plan: Any, estimate: Any) -> GuardedCredits:
    base_credits = max(1, int(getattr(estimate, "credits", 1) or 1))
    if not bool(getattr(settings, "profit_guard_enabled", True)):
        return GuardedCredits(
            credits=base_credits,
            ai_cost_rub=ZERO,
            credit_value_rub=ZERO,
            monthly_ai_budget_rub=ZERO,
            reason="profit_guard=off",
        )

    input_tokens = int(getattr(estimate, "input_tokens_estimated", 0) or 0)
    output_tokens = int(getattr(estimate, "output_tokens_reserved", 0) or 0)
    cost = ai_cost_rub(settings, input_tokens, output_tokens)
    plan_key = str(getattr(plan, "key", "free") or "free").lower()
    budget = monthly_ai_budget_rub(settings, plan)
    if plan_key == "free" and budget <= 0 and cost > 0:
        return GuardedCredits(
            credits=1_000_000_000,
            ai_cost_rub=cost,
            credit_value_rub=ZERO,
            monthly_ai_budget_rub=ZERO,
            reason="profit_guard: Free blocks paid AI cost; use openrouter/free or set FREE_AI_MONTHLY_BUDGET_RUB",
        )
    value = credit_value_rub(settings, plan)
    required_by_cost = ceil_int(cost / value) if value > 0 else base_credits
    guarded = max(base_credits, required_by_cost)
    reason = (
        f"profit_guard: cost≈{money(cost)} RUB, credit_value≈{money(value)} RUB, "
        f"base={base_credits}, guarded={guarded}"
    )
    return GuardedCredits(
        credits=guarded,
        ai_cost_rub=cost,
        credit_value_rub=money(value),
        monthly_ai_budget_rub=budget,
        reason=reason,
    )


def plan_features(plan_key: str) -> dict[str, Any]:
    key = str(plan_key or "free").lower()
    data: dict[str, dict[str, Any]] = {
        "free": {
            "tools": ["chat", "idea_check", "margin_calc"],
            "exports": False,
            "history_days": 7,
            "projects": 1,
            "team_members": 0,
            "priority_support": False,
        },
        "go": {
            "tools": ["chat", "idea_check", "margin_calc", "offer", "review_reply"],
            "exports": False,
            "history_days": 30,
            "projects": 2,
            "team_members": 0,
            "priority_support": False,
        },
        "plus": {
            "tools": "all_basic",
            "exports": True,
            "history_days": 180,
            "projects": 5,
            "team_members": 0,
            "priority_support": False,
        },
        "pro": {
            "tools": "all",
            "exports": True,
            "history_days": 365,
            "projects": 20,
            "team_members": 0,
            "priority_support": True,
        },
        "business": {
            "tools": "all",
            "exports": True,
            "history_days": 730,
            "projects": 100,
            "team_members": 10,
            "priority_support": True,
            "organization": True,
            "roles": ["owner", "admin", "member"],
        },
    }
    return data.get(key, data["free"])


def plan_economics(settings: Settings, plan: Any, provider: str | None = "yookassa") -> dict[str, Any]:
    key = str(getattr(plan, "key", "free") or "free").lower()
    gross = dec(getattr(plan, "price_rub", "0"))
    net = net_revenue_rub(settings, gross, provider, "RUB")
    ai_budget = monthly_ai_budget_rub(settings, plan, provider, "RUB")
    monthly_limit = max(1, int(getattr(plan, "monthly_limit", 1) or 1))
    credit_value = credit_value_rub(settings, plan, provider, "RUB")
    reserved_profit = money(net - ai_budget)
    if key == "free" and net <= 0:
        reserved_profit = ZERO if ai_budget <= 0 else -ai_budget
    profit_margin = (reserved_profit / net) if net > 0 else ZERO
    return {
        "plan": key,
        "gross_revenue_rub": float(money(gross)),
        "net_revenue_after_fees_rub": float(money(net)),
        "max_ai_budget_rub": float(money(ai_budget)),
        "reserved_profit_rub": float(money(reserved_profit)),
        "reserved_profit_margin": float(money(profit_margin * Decimal("100"))),
        "monthly_credits": monthly_limit,
        "credit_value_rub": float(money(credit_value)),
        "payment_fee_rate": float(payment_fee_rate(settings, provider)),
        "tax_rate": float(clamp_rate(getattr(settings, "tax_rate", "0.06"), "0.06")),
        "refund_risk_rate": float(clamp_rate(getattr(settings, "refund_risk_rate", "0.03"), "0.03")),
        "max_ai_cost_share": float(max_ai_cost_share(settings, key)),
        "features": plan_features(key),
    }


def credit_pack_margin(settings: Settings, pack: dict[str, Any], provider: str | None = "yookassa") -> dict[str, Any]:
    amount = dec(pack.get("amount") or 0)
    credits = max(1, int(pack.get("credits") or 1))
    net = net_revenue_rub(settings, amount, provider, "RUB")
    min_value = dec(getattr(settings, "minimum_credit_value_rub", "0.01"), "0.01")
    ai_budget = money(Decimal(credits) * min_value)
    reserved_profit = money(net - ai_budget)
    return {
        "pack_key": pack.get("key") or pack.get("id"),
        "amount_rub": float(money(amount)),
        "credits": credits,
        "net_revenue_after_fees_rub": float(money(net)),
        "max_ai_budget_rub": float(money(ai_budget)),
        "reserved_profit_rub": float(money(reserved_profit)),
        "is_profitable": reserved_profit >= 0,
    }
