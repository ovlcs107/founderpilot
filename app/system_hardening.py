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



def compact_status_message(results: dict[str, Any]) -> str:
    """Human-readable, short owner-facing maintenance summary."""
    stale = int((results.get("stale_ai_reservations") or {}).get("released") or 0)
    expired_orders = int((results.get("expired_orders") or {}).get("expired") or 0)
    expired_subs = int((results.get("expired_subscriptions") or {}).get("expired") or 0)
    parts = []
    if stale:
        parts.append(f"AI reservations: {stale}")
    if expired_orders:
        parts.append(f"orders: {expired_orders}")
    if expired_subs:
        parts.append(f"subscriptions: {expired_subs}")
    return "; ".join(parts) if parts else "No maintenance changes"


async def run_maintenance_cycle(db: Any, settings: Settings) -> dict[str, Any]:
    """Run safe, idempotent backend cleanup tasks once.

    The function is intentionally dependency-light so it can be called manually
    from admin API or by a background loop. It does not call external providers.
    """
    results: dict[str, Any] = {"ok": True}
    results["stale_ai_reservations"] = await db.cleanup_stale_ai_reservations(
        max_age_minutes=settings.system_tasks_stale_ai_minutes,
    )
    results["expired_orders"] = await db.expire_stale_billing_orders()
    results["expired_subscriptions"] = await db.expire_due_subscriptions()
    results["message"] = compact_status_message(results)
    await db.log_system_event(
        "maintenance_cycle_finished",
        source="system_tasks",
        severity="info",
        message=results["message"],
        metadata={
            "stale_ai_reservations": results["stale_ai_reservations"],
            "expired_orders": results["expired_orders"],
            "expired_subscriptions": results["expired_subscriptions"],
        },
    )
    return results


async def system_task_loop(db: Any, settings: Settings, *, stop_event: Any | None = None) -> None:
    """Tiny cron-like loop for one-process deployments.

    Railway can run this in the same combined service. For larger production use,
    keep the function and move it to a dedicated worker/cron service.
    """
    import asyncio

    interval = max(60, int(settings.system_tasks_interval_seconds or 300))
    while True:
        try:
            await run_maintenance_cycle(db, settings)
        except Exception as exc:  # noqa: BLE001
            try:
                await db.log_error("system_task_loop", str(exc), None)
            except Exception:
                pass
        if stop_event is not None and getattr(stop_event, "is_set", lambda: False)():
            return
        await asyncio.sleep(interval)
