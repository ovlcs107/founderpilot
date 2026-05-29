from dataclasses import replace

from app.billing import plan_catalog
from app.config import Settings, require_runtime_settings
from app.credits import estimate_credits
from app.economics import credit_pack_margin, guard_credits_for_margin, plan_economics


def make_settings(**overrides):
    base = {
        "BOT_TOKEN": "123:token",
        "OPENROUTER_API_KEY": "openrouter-key",
        "APP_SECRET": "x" * 32,
        "ADMIN_SECRET": "y" * 32,
    }
    base.update(overrides)
    return Settings(_env_file=None, **base)


def test_profit_guard_increases_credits_for_expensive_model():
    settings = make_settings(
        OPENROUTER_MODEL="openai/gpt-4.1",
        AI_INPUT_COST_USD_PER_M_TOKENS="10",
        AI_OUTPUT_COST_USD_PER_M_TOKENS="30",
        USD_RUB_RATE="100",
        AI_COST_SAFETY_MULTIPLIER="2",
    )
    plan = plan_catalog(settings)["go"]
    estimate = estimate_credits("chat", "x" * 2000, model="expensive-model")
    guarded = guard_credits_for_margin(settings, plan, estimate)

    assert guarded.credits >= estimate.credits
    assert guarded.ai_cost_rub > 0
    assert guarded.credit_value_rub > 0


def test_plan_economics_keeps_positive_reserved_profit():
    settings = make_settings()
    econ = plan_economics(settings, plan_catalog(settings)["pro"])

    assert econ["gross_revenue_rub"] == 2490
    assert econ["net_revenue_after_fees_rub"] > 0
    assert econ["reserved_profit_rub"] > 0
    assert econ["max_ai_budget_rub"] > 0


def test_credit_pack_prices_cover_minimum_credit_value():
    settings = make_settings()
    packs = [
        {"key": "credits_1000", "credits": 1000, "amount": 199},
        {"key": "credits_50000", "credits": 50000, "amount": 5490},
    ]

    for pack in packs:
        margin = credit_pack_margin(settings, pack)
        assert margin["is_profitable"] is True
        assert margin["reserved_profit_rub"] > 0


def test_stars_requires_rub_value_or_explicit_override():
    settings = make_settings(BILLING_ENABLE_STARS=True, TELEGRAM_STARS_RUB_VALUE="0")
    try:
        require_runtime_settings(settings)
    except RuntimeError as exc:
        assert "TELEGRAM_STARS_RUB_VALUE" in str(exc)
    else:
        raise AssertionError("Unpriced Stars must be rejected")

    settings = make_settings(BILLING_ENABLE_STARS=True, TELEGRAM_STARS_RUB_VALUE="0.8")
    require_runtime_settings(settings)
