from __future__ import annotations

from decimal import Decimal
from time import perf_counter
from typing import Any

from app.config import Settings


class Stopwatch:
    """Tiny helper used to store AI latency without pulling in observability deps."""

    def __init__(self) -> None:
        self.started_at = perf_counter()

    def ms(self) -> int:
        return max(0, int((perf_counter() - self.started_at) * 1000))


def _decimal(value: Any, default: str = "0") -> Decimal:
    try:
        return Decimal(str(value if value is not None else default))
    except Exception:
        return Decimal(default)


def estimate_ai_cost_rub(settings: Settings, *, model: str | None, input_tokens: int, output_tokens: int) -> float:
    """Approximate provider cost in rubles for analytics / profit monitoring.

    This is intentionally conservative and env-driven. It does not bill the user;
    user billing remains credit-based. The goal is owner visibility: which models
    are burning money and when margins are getting unsafe.
    """
    name = (model or "").lower()
    if "free" in name and not settings.estimate_free_model_cost:
        return 0.0
    input_cost_usd = (_decimal(input_tokens) / Decimal("1000000")) * _decimal(settings.ai_input_cost_usd_per_m_tokens)
    output_cost_usd = (_decimal(output_tokens) / Decimal("1000000")) * _decimal(settings.ai_output_cost_usd_per_m_tokens)
    subtotal_usd = input_cost_usd + output_cost_usd
    fee_rate = _decimal(settings.openrouter_fee_rate)
    rub = subtotal_usd * (Decimal("1") + fee_rate) * _decimal(settings.usd_rub_rate) * _decimal(settings.ai_cost_safety_multiplier, "1")
    return float(rub.quantize(Decimal("0.0001")))
