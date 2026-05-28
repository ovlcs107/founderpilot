from __future__ import annotations

import base64
import hmac
import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Any
from uuid import uuid4

import httpx
from aiogram import Bot
from aiogram.types import LabeledPrice

from app.config import Settings
from app.db import Database

logger = logging.getLogger(__name__)

PLAN_DAYS = 30


@dataclass(frozen=True)
class Plan:
    key: str
    title: str
    daily_limit: int
    price_rub: Decimal
    price_stars: int
    price_ton: Decimal
    price_btc: Decimal


class BillingError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def plan_catalog(settings: Settings) -> dict[str, Plan]:
    return {
        "free": Plan(
            key="free",
            title="Free",
            daily_limit=settings.daily_free_limit,
            price_rub=Decimal("0"),
            price_stars=0,
            price_ton=Decimal("0"),
            price_btc=Decimal("0"),
        ),
        "pro": Plan(
            key="pro",
            title="Pro",
            daily_limit=settings.pro_daily_limit,
            price_rub=Decimal(str(settings.pro_price_rub)),
            price_stars=settings.pro_price_stars,
            price_ton=Decimal(str(settings.pro_price_ton)),
            price_btc=Decimal(str(settings.pro_price_btc)),
        ),
        "business": Plan(
            key="business",
            title="Business",
            daily_limit=settings.business_daily_limit,
            price_rub=Decimal(str(settings.business_price_rub)),
            price_stars=settings.business_price_stars,
            price_ton=Decimal(str(settings.business_price_ton)),
            price_btc=Decimal(str(settings.business_price_btc)),
        ),
    }


def enabled_providers(settings: Settings) -> list[dict[str, Any]]:
    providers: list[dict[str, Any]] = []
    if settings.billing_enable_stars:
        providers.append({"id": "telegram_stars", "title": "Telegram Stars", "currency": "XTR"})
    if settings.billing_enable_yookassa:
        providers.append({"id": "yookassa", "title": "ЮKassa / ЮMoney", "currency": "RUB"})
    if settings.billing_enable_ton:
        providers.append({"id": "ton", "title": "TON / Tonkeeper", "currency": "TON"})
    if settings.billing_enable_btcpay:
        providers.append({"id": "btcpay_btc", "title": "BTC", "currency": "BTC"})
    return providers


def provider_enabled(settings: Settings, provider: str) -> bool:
    return provider in {item["id"] for item in enabled_providers(settings)}


def price_for_provider(plan: Plan, provider: str) -> tuple[Decimal, str]:
    if provider == "telegram_stars":
        return Decimal(plan.price_stars), "XTR"
    if provider == "yookassa":
        return plan.price_rub, "RUB"
    if provider == "ton":
        return plan.price_ton, "TON"
    if provider == "btcpay_btc":
        return plan.price_btc, "BTC"
    raise BillingError("Неизвестный способ оплаты.")


def rub_value(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def ton_to_nanotons(value: Decimal) -> int:
    return int((value * Decimal("1000000000")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def make_order_id() -> str:
    return f"ord_{uuid4().hex}"


async def create_telegram_stars_invoice(settings: Settings, bot: Bot, order: dict[str, Any], plan: Plan) -> str:
    # Telegram Stars invoices use XTR and do not need an external provider token.
    try:
        return await bot.create_invoice_link(
            title=f"FounderPilot AI {plan.title}",
            description=f"Подписка FounderPilot AI {plan.title} на {PLAN_DAYS} дней",
            payload=order["id"],
            currency="XTR",
            prices=[LabeledPrice(label=f"FounderPilot AI {plan.title}", amount=int(plan.price_stars))],
            subscription_period=PLAN_DAYS * 24 * 60 * 60,
        )
    except TypeError:
        # Older aiogram versions may not know subscription_period yet.
        return await bot.create_invoice_link(
            title=f"FounderPilot AI {plan.title}",
            description=f"Доступ FounderPilot AI {plan.title} на {PLAN_DAYS} дней",
            payload=order["id"],
            currency="XTR",
            prices=[LabeledPrice(label=f"FounderPilot AI {plan.title}", amount=int(plan.price_stars))],
        )


async def create_yookassa_payment(settings: Settings, order: dict[str, Any], plan: Plan) -> tuple[str, str]:
    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise BillingError("ЮKassa не настроена: заполните YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY.")

    auth = (settings.yookassa_shop_id, settings.yookassa_secret_key)
    return_url = settings.yookassa_return_url or f"{settings.webapp_url}?payment_return=1&order_id={order['id']}"
    body = {
        "amount": {"value": rub_value(Decimal(str(order["amount"]))), "currency": "RUB"},
        "capture": True,
        "confirmation": {"type": "redirect", "return_url": return_url},
        "description": f"FounderPilot AI {plan.title} на {PLAN_DAYS} дней",
        "metadata": {
            "order_id": order["id"],
            "telegram_user_id": order["telegram_user_id"],
            "plan": plan.key,
        },
    }
    headers = {"Idempotence-Key": order["id"]}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://api.yookassa.ru/v3/payments", json=body, auth=auth, headers=headers)
        if response.status_code >= 400:
            raise BillingError(f"ЮKassa вернула ошибку: {response.status_code} {response.text[:300]}")
        data = response.json()
    payment_url = data.get("confirmation", {}).get("confirmation_url")
    external_id = data.get("id")
    if not payment_url or not external_id:
        raise BillingError("ЮKassa не вернула ссылку оплаты.")
    return external_id, payment_url


async def create_btcpay_invoice(settings: Settings, order: dict[str, Any], plan: Plan) -> tuple[str, str]:
    if not settings.btcpay_url or not settings.btcpay_store_id or not settings.btcpay_api_key:
        raise BillingError("BTCPay не настроен: заполните BTCPAY_URL, BTCPAY_STORE_ID и BTCPAY_API_KEY.")

    base = settings.btcpay_url.rstrip("/")
    url = f"{base}/api/v1/stores/{settings.btcpay_store_id}/invoices"
    redirect_url = f"{settings.webapp_url}?payment_return=1&order_id={order['id']}"
    body = {
        "amount": str(order["amount"]),
        "currency": "BTC",
        "checkout": {"redirectURL": redirect_url, "redirectAutomatically": False},
        "metadata": {
            "orderId": order["id"],
            "telegram_user_id": order["telegram_user_id"],
            "plan": plan.key,
            "buyerName": f"Telegram {order['telegram_user_id']}",
        },
    }
    headers = {"Authorization": f"token {settings.btcpay_api_key}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=body, headers=headers)
        if response.status_code >= 400:
            raise BillingError(f"BTCPay вернул ошибку: {response.status_code} {response.text[:300]}")
        data = response.json()
    invoice_id = data.get("id")
    checkout_link = data.get("checkoutLink") or data.get("url")
    if not invoice_id or not checkout_link:
        raise BillingError("BTCPay не вернул checkout link.")
    return invoice_id, checkout_link


def build_ton_transaction(settings: Settings, order: dict[str, Any]) -> dict[str, Any]:
    if not settings.ton_receiver_address:
        raise BillingError("TON не настроен: заполните TON_RECEIVER_ADDRESS.")
    amount = ton_to_nanotons(Decimal(str(order["amount"])))
    valid_until = int((utc_now() + timedelta(minutes=20)).timestamp())
    return {
        "validUntil": valid_until,
        "messages": [
            {
                "address": settings.ton_receiver_address,
                "amount": str(amount),
                "payload": order["id"],
            }
        ],
        "comment": order["id"],
    }


def verify_btcpay_signature(settings: Settings, raw_body: bytes, signature_header: str | None) -> bool:
    if not settings.btcpay_webhook_secret:
        return True
    if not signature_header:
        return False
    expected = hmac.new(settings.btcpay_webhook_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    supplied = signature_header
    if supplied.startswith("sha256="):
        supplied = supplied.split("=", 1)[1]
    return hmac.compare_digest(expected, supplied)


async def best_effort_ton_verify(settings: Settings, order: dict[str, Any], tx_hash: str | None = None) -> tuple[bool, str]:
    if not settings.ton_api_key:
        return False, "TON verification is not configured: заполните TON_API_KEY или проверьте транзакцию вручную."
    if not settings.ton_receiver_address:
        return False, "TON_RECEIVER_ADDRESS не настроен."

    # Универсальная безопасная проверка через TonAPI events. API может отличаться по тарифу/сети,
    # поэтому при любой неоднозначности подписка не активируется автоматически.
    headers = {"Authorization": f"Bearer {settings.ton_api_key}"}
    base = "https://testnet.tonapi.io" if settings.ton_network.lower() == "testnet" else "https://tonapi.io"
    url = f"{base}/v2/blockchain/accounts/{settings.ton_receiver_address}/transactions"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(url, headers=headers, params={"limit": 20})
            if response.status_code >= 400:
                return False, f"TON API вернул ошибку {response.status_code}."
            data = response.json()
    except httpx.HTTPError as exc:
        return False, f"Не удалось проверить TON транзакцию: {exc}"

    required_amount = ton_to_nanotons(Decimal(str(order["amount"])))
    transactions = data.get("transactions") or []
    needle = tx_hash or order["id"]
    for tx in transactions:
        raw = json.dumps(tx, ensure_ascii=False)
        if needle and needle not in raw and order["id"] not in raw:
            continue
        if str(required_amount) not in raw:
            continue
        return True, "TON транзакция подтверждена."
    return False, "Платёж TON пока не найден. Подождите подтверждения сети и повторите проверку."


async def activate_subscription(db: Database, telegram_user_id: int | str, plan_key: str, provider: str, order_id: str, daily_limit: int) -> dict[str, Any]:
    return await db.activate_paid_subscription(
        telegram_id=int(telegram_user_id),
        plan=plan_key,
        provider=provider,
        order_id=order_id,
        daily_limit=daily_limit,
        days=PLAN_DAYS,
    )
