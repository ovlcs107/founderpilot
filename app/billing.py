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
from urllib.parse import quote
from uuid import uuid4

import httpx
from aiogram import Bot
from aiogram.types import LabeledPrice

from app.config import Settings
from app.db import Database

logger = logging.getLogger(__name__)

PLAN_DAYS = 30

PLAN_DESCRIPTIONS = {
    "free": "Базовые инструменты и лимиты",
    "go": "Для первых регулярных задач",
    "plus": "Оптимум для активной работы",
    "pro": "Полный доступ ко всем функциям",
    "business": "Команды, роли и совместная работа",
}



@dataclass(frozen=True)
class Plan:
    key: str
    title: str
    daily_limit: int
    monthly_limit: int
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


def normalize_plan_key(value: str | None) -> str:
    return str(value or "").strip().lower().replace(" ", "_")


def normalize_provider_key(value: str | None) -> str:
    provider = str(value or "").strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "": "auto",
        "default": "auto",
        "auto_detect": "auto",
        "autodetect": "auto",
        "automatic": "auto",
        "stars": "telegram_stars",
        "xtr": "telegram_stars",
        "card": "yookassa",
        "cards": "yookassa",
        "bank_card": "yookassa",
        "bank_cards": "yookassa",
        "sbp": "yookassa",
        "yoomoney": "yookassa",
        "youkassa": "yookassa",
        "btc": "btcpay_btc",
        "bitcoin": "btcpay_btc",
        "btcpay": "btcpay_btc",
    }
    return aliases.get(provider, provider)


def plan_catalog(settings: Settings) -> dict[str, Plan]:
    return {
        "free": Plan(
            key="free",
            title="Free",
            daily_limit=settings.free_daily_credits,
            monthly_limit=settings.free_monthly_credits,
            price_rub=Decimal("0"),
            price_stars=0,
            price_ton=Decimal("0"),
            price_btc=Decimal("0"),
        ),
        "go": Plan(
            key="go",
            title="Go",
            daily_limit=settings.go_daily_credits,
            monthly_limit=settings.go_monthly_credits,
            price_rub=Decimal(str(settings.go_price_rub)),
            price_stars=settings.go_price_stars,
            price_ton=Decimal(str(settings.go_price_ton)),
            price_btc=Decimal(str(settings.go_price_btc)),
        ),
        "plus": Plan(
            key="plus",
            title="Plus",
            daily_limit=settings.plus_daily_credits,
            monthly_limit=settings.plus_monthly_credits,
            price_rub=Decimal(str(settings.plus_price_rub)),
            price_stars=settings.plus_price_stars,
            price_ton=Decimal(str(settings.plus_price_ton)),
            price_btc=Decimal(str(settings.plus_price_btc)),
        ),
        "pro": Plan(
            key="pro",
            title="Pro",
            daily_limit=settings.pro_daily_credits,
            monthly_limit=settings.pro_monthly_credits,
            price_rub=Decimal(str(settings.pro_price_rub)),
            price_stars=settings.pro_price_stars,
            price_ton=Decimal(str(settings.pro_price_ton)),
            price_btc=Decimal(str(settings.pro_price_btc)),
        ),
        "business": Plan(
            key="business",
            title="Business",
            daily_limit=settings.business_daily_credits,
            monthly_limit=settings.business_monthly_credits,
            price_rub=Decimal(str(settings.business_price_rub)),
            price_stars=settings.business_price_stars,
            price_ton=Decimal(str(settings.business_price_ton)),
            price_btc=Decimal(str(settings.business_price_btc)),
        ),
    }

def public_plan_catalog(settings: Settings) -> dict[str, Plan]:
    catalog = plan_catalog(settings)
    return {key: catalog[key] for key in settings.public_plan_keys if key in catalog}


def _positive_decimal(value: Any) -> bool:
    try:
        return Decimal(str(value or "0")) > 0
    except Exception:
        return False


def enabled_providers(settings: Settings) -> list[dict[str, Any]]:
    providers: list[dict[str, Any]] = []
    stars_economically_configured = bool(settings.billing_allow_unpriced_stars) or _positive_decimal(settings.telegram_stars_rub_value)
    if settings.billing_enable_stars and stars_economically_configured:
        providers.append({"id": "telegram_stars", "title": "Telegram Stars", "description": "Оплата внутри Telegram", "currency": "XTR"})

    # YooKassa must never be shown as an enabled payment method without credentials.
    # Otherwise the UI lets the user click a dead provider and gets “Not found”/setup errors.
    yookassa_ready = bool(settings.yookassa_shop_id and settings.yookassa_secret_key)
    if yookassa_ready:
        providers.append({
            "id": "yookassa",
            "title": "Карта / СБП",
            "description": "Безопасная разовая оплата через ЮKassa",
            "currency": "RUB",
            # Saved payment methods / recurring charges are a separate YooKassa permission.
            # Many shops can accept normal payments, but get 403 forbidden for recurring.
            # The frontend uses this flag to keep the autopay switch disabled instead of
            # sending users into a broken checkout.
            "recurring_available": bool(settings.yookassa_enable_saved_payment_method),
        })

    if settings.billing_enable_ton and settings.ton_receiver_address:
        providers.append({"id": "ton", "title": "TON", "description": "Tonkeeper / TON", "currency": "TON"})
    if (
        settings.billing_enable_btcpay
        and settings.btcpay_url
        and settings.btcpay_store_id
        and settings.btcpay_api_key
        and settings.btcpay_webhook_secret
    ):
        providers.append({"id": "btcpay_btc", "title": "BTC", "description": "Bitcoin invoice", "currency": "BTC"})
    return providers


def provider_enabled(settings: Settings, provider: str) -> bool:
    provider = normalize_provider_key(provider)
    return provider in {item["id"] for item in enabled_providers(settings)}


def resolve_payment_provider(settings: Settings, requested_provider: str | None, *, telegram_webapp: bool = False) -> str:
    provider = normalize_provider_key(requested_provider)
    enabled = {item["id"] for item in enabled_providers(settings)}
    if provider != "auto":
        if provider in enabled:
            return provider
        raise BillingError("Этот способ оплаты сейчас отключён или не настроен.")

    order = list(settings.payment_auto_provider_order)
    if telegram_webapp and "telegram_stars" in order:
        order.remove("telegram_stars")
        order.insert(0, "telegram_stars")
    for candidate in order:
        candidate = normalize_provider_key(candidate)
        if candidate in enabled:
            return candidate
    raise BillingError("Ни один способ оплаты пока не настроен. Подключите ЮKassa или задайте TELEGRAM_STARS_RUB_VALUE для Stars в .env.")


def price_for_provider(plan: Plan, provider: str) -> tuple[Decimal, str]:
    provider = normalize_provider_key(provider)
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


def build_payment_return_url(settings: Settings, order_id: str) -> str:
    """Return URL that always carries enough context for the Mini App to poll order status.

    Operators often set YOOKASSA_RETURN_URL to just /app. That is valid, but then the
    frontend cannot know which order should be refreshed after the user comes back from
    YooKassa. We append payment_return/order_id safely even when the configured URL
    already has query parameters.
    """
    base = settings.yookassa_return_url or settings.webapp_url
    if not base:
        base = settings.webapp_url
    separator = "&" if "?" in base else "?"
    return f"{base}{separator}payment_return=1&order_id={order_id}"


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


def _friendly_yookassa_error(response_text: str, status_code: int) -> str:
    """Convert raw YooKassa JSON into a user-safe Russian message."""
    try:
        data = json.loads(response_text)
    except Exception:
        data = {}
    code = str(data.get("code") or "").lower()
    description = str(data.get("description") or response_text or "").strip()
    if code == "forbidden" and "recurring" in description.lower():
        return (
            "ЮKassa не разрешила автопродление для этого магазина. "
            "Разовая оплата доступна, а автосписания нужно отдельно подключить в ЮKassa."
        )
    if description:
        return f"ЮKassa вернула ошибку {status_code}: {description[:220]}"
    return f"ЮKassa вернула ошибку {status_code}."


def _is_yookassa_recurring_forbidden(response_text: str, status_code: int) -> bool:
    if status_code != 403:
        return False
    try:
        data = json.loads(response_text)
    except Exception:
        data = {}
    description = str(data.get("description") or response_text or "").lower()
    return str(data.get("code") or "").lower() == "forbidden" and "recurring" in description


async def create_yookassa_payment(settings: Settings, order: dict[str, Any], plan: Plan, *, save_payment_method: bool = False) -> tuple[str, str]:
    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise BillingError("ЮKassa не настроена: заполните YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY.")

    auth = (settings.yookassa_shop_id, settings.yookassa_secret_key)
    return_url = build_payment_return_url(settings, order["id"])

    # Important: YooKassa recurring payments are not enabled for every store.
    # A normal shop can accept card/SBP payments and still reject save_payment_method
    # with: "This store can't make recurring payments". Therefore recurring is opt-in
    # via YOOKASSA_ENABLE_SAVED_PAYMENT_METHOD=false by default, and even if an old
    # env enables it, we gracefully retry as a one-time payment instead of killing the sale.
    def build_body(should_save_method: bool) -> dict[str, Any]:
        body: dict[str, Any] = {
            "amount": {"value": rub_value(Decimal(str(order["amount"]))), "currency": "RUB"},
            "capture": True,
            "confirmation": {"type": "redirect", "return_url": return_url},
            "description": f"FounderPilot AI {plan.title} на {PLAN_DAYS} дней",
            "metadata": {
                "order_id": order["id"],
                "telegram_user_id": order["telegram_user_id"],
                "plan": plan.key,
                "auto_renew": "1" if should_save_method else "0",
            },
        }
        if should_save_method:
            body["save_payment_method"] = True
        return body

    effective_save_method = bool(save_payment_method and settings.yookassa_enable_saved_payment_method)
    attempts = [(effective_save_method, order["id"])]
    if effective_save_method:
        attempts.append((False, f"{order['id']}_once"))

    last_response_text = ""
    last_status_code = 0
    data: dict[str, Any] | None = None
    for should_save_method, idempotence_key in attempts:
        body = build_body(should_save_method)
        headers = {"Idempotence-Key": idempotence_key}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("https://api.yookassa.ru/v3/payments", json=body, auth=auth, headers=headers)
        if response.status_code < 400:
            data = response.json()
            if effective_save_method and not should_save_method:
                logger.warning("YooKassa recurring rejected for order %s; one-time payment fallback was created.", order["id"])
            break
        last_response_text = response.text
        last_status_code = response.status_code
        if should_save_method and _is_yookassa_recurring_forbidden(response.text, response.status_code):
            continue
        raise BillingError(_friendly_yookassa_error(response.text, response.status_code))

    if data is None:
        raise BillingError(_friendly_yookassa_error(last_response_text, last_status_code or 400))

    payment_url = data.get("confirmation", {}).get("confirmation_url")
    external_id = data.get("id")
    if not payment_url or not external_id:
        raise BillingError("ЮKassa не вернула ссылку оплаты.")
    return external_id, payment_url


async def create_yookassa_credit_pack_payment(settings: Settings, order: dict[str, Any], pack: dict[str, Any]) -> tuple[str, str]:
    """Create a YooKassa payment for one-time credit packs.

    Subscription payments use billing_orders, but credit packs are stored in
    credit_pack_orders. Metadata marks the kind explicitly so the webhook can
    route the payment safely without activating a subscription by accident.
    """
    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise BillingError("ЮKassa не настроена: заполните YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY.")

    base = settings.yookassa_return_url or settings.webapp_url
    separator = "&" if "?" in base else "?"
    return_url = f"{base}{separator}payment_return=1&credit_pack_return=1&credit_pack_order_id={order['id']}"
    amount_value = rub_value(Decimal(str(order.get("amount") or pack.get("amount") or 0)))
    body = {
        "amount": {"value": amount_value, "currency": "RUB"},
        "capture": True,
        "confirmation": {"type": "redirect", "return_url": return_url},
        "description": f"FounderPilot AI: {pack.get('title') or 'пакет кредитов'}",
        "metadata": {
            "kind": "credit_pack",
            "order_id": order["id"],
            "credit_pack_order_id": order["id"],
            "telegram_user_id": order["telegram_user_id"],
            "pack_key": order.get("pack_key") or pack.get("key"),
        },
    }
    auth = (settings.yookassa_shop_id, settings.yookassa_secret_key)
    headers = {"Idempotence-Key": order["id"]}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://api.yookassa.ru/v3/payments", json=body, auth=auth, headers=headers)
        if response.status_code >= 400:
            raise BillingError(_friendly_yookassa_error(response.text, response.status_code))
        data = response.json()
    payment_url = data.get("confirmation", {}).get("confirmation_url")
    external_id = data.get("id")
    if not payment_url or not external_id:
        raise BillingError("ЮKassa не вернула ссылку оплаты.")
    return external_id, payment_url


async def fetch_yookassa_payment(settings: Settings, payment_id: str) -> dict[str, Any]:
    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise BillingError("ЮKassa не настроена.")
    auth = (settings.yookassa_shop_id, settings.yookassa_secret_key)
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(f"https://api.yookassa.ru/v3/payments/{payment_id}", auth=auth)
        if response.status_code >= 400:
            raise BillingError(_friendly_yookassa_error(response.text, response.status_code))
        return response.json()


async def verify_yookassa_payment(settings: Settings, order: dict[str, Any], payment_id: str) -> dict[str, Any]:
    data = await fetch_yookassa_payment(settings, payment_id)
    metadata = data.get("metadata") or {}
    amount = data.get("amount") or {}
    expected_value = rub_value(Decimal(str(order["amount"])))
    if str(metadata.get("order_id") or "") != str(order["id"]):
        raise BillingError("ЮKassa: metadata.order_id не совпадает с заказом.")
    if str(amount.get("currency") or "").upper() != "RUB":
        raise BillingError("ЮKassa: валюта платежа не совпадает.")
    if str(amount.get("value") or "") != expected_value:
        raise BillingError("ЮKassa: сумма платежа не совпадает.")
    if data.get("status") != "succeeded":
        raise BillingError("ЮKassa: платёж ещё не подтверждён.")
    return data


async def create_yookassa_autopayment(settings: Settings, *, payment_method_id: str, order: dict[str, Any], plan: Plan) -> tuple[str, str, dict[str, Any]]:
    if not settings.yookassa_enable_saved_payment_method:
        raise BillingError("Автосписания ЮKassa выключены: включите YOOKASSA_ENABLE_SAVED_PAYMENT_METHOD только после подключения recurring-платежей у ЮKassa.")
    if not settings.yookassa_shop_id or not settings.yookassa_secret_key:
        raise BillingError("ЮKassa не настроена: заполните YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY.")
    auth = (settings.yookassa_shop_id, settings.yookassa_secret_key)
    body = {
        "amount": {"value": rub_value(Decimal(str(order["amount"]))), "currency": "RUB"},
        "capture": True,
        "payment_method_id": payment_method_id,
        "description": f"Автопродление FounderPilot AI {plan.title} на {PLAN_DAYS} дней",
        "metadata": {
            "order_id": order["id"],
            "telegram_user_id": order["telegram_user_id"],
            "plan": plan.key,
            "auto_renewal_charge": "1",
        },
    }
    headers = {"Idempotence-Key": order["id"]}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post("https://api.yookassa.ru/v3/payments", json=body, auth=auth, headers=headers)
        if response.status_code >= 400:
            raise BillingError(_friendly_yookassa_error(response.text, response.status_code))
        data = response.json()
    external_id = data.get("id")
    status = str(data.get("status") or "pending")
    if not external_id:
        raise BillingError("ЮKassa не вернула id автоплатежа.")
    return external_id, status, data


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


def build_ton_payment_link(settings: Settings, order: dict[str, Any]) -> str:
    transaction = build_ton_transaction(settings, order)
    message = transaction["messages"][0]
    address = quote(str(message["address"]), safe="")
    amount = quote(str(message["amount"]), safe="")
    text = quote(str(order["id"]), safe="")
    exp = quote(str(transaction["validUntil"]), safe="")
    return f"https://app.tonkeeper.com/transfer/{address}?amount={amount}&text={text}&exp={exp}"


def verify_btcpay_signature(settings: Settings, raw_body: bytes, signature_header: str | None) -> bool:
    if not settings.btcpay_webhook_secret:
        return False
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


async def activate_subscription(
    db: Database,
    telegram_user_id: int | str,
    plan_key: str,
    provider: str,
    order_id: str,
    daily_limit: int,
    monthly_limit: int | None = None,
) -> dict[str, Any]:
    return await db.activate_paid_subscription(
        telegram_id=int(telegram_user_id),
        plan=plan_key,
        provider=provider,
        order_id=order_id,
        daily_limit=daily_limit,
        monthly_limit=monthly_limit,
        days=PLAN_DAYS,
    )
