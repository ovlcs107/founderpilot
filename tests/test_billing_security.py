import hashlib
import hmac

import pytest

from app.billing import (
    build_ton_payment_link,
    enabled_providers,
    plan_catalog,
    public_plan_catalog,
    provider_enabled,
    resolve_payment_provider,
    verify_btcpay_signature,
)
from app.config import Settings, require_runtime_settings
from app.main import create_app


def make_settings(**overrides):
    base = {
        "BOT_TOKEN": "123:token",
        "OPENROUTER_API_KEY": "openrouter-key",
        "APP_SECRET": "x" * 32,
    }
    base.update(overrides)
    return Settings(_env_file=None, **base)


def test_btcpay_provider_requires_webhook_secret():
    settings = make_settings(
        BILLING_ENABLE_BTCPAY=True,
        BTCPAY_URL="https://pay.example.test",
        BTCPAY_STORE_ID="store",
        BTCPAY_API_KEY="api-key",
        BTCPAY_WEBHOOK_SECRET="",
    )

    assert not provider_enabled(settings, "btcpay_btc")
    assert "btcpay_btc" not in {provider["id"] for provider in enabled_providers(settings)}
    with pytest.raises(RuntimeError, match="BTCPAY_WEBHOOK_SECRET"):
        require_runtime_settings(settings)


def test_btcpay_signature_requires_secret_and_uses_hmac():
    raw_body = b'{"type":"InvoiceSettled","invoiceId":"inv_1"}'
    unsigned_settings = make_settings(BTCPAY_WEBHOOK_SECRET="")
    signed_settings = make_settings(BTCPAY_WEBHOOK_SECRET="webhook-secret")

    signature = "sha256=" + hmac.new(b"webhook-secret", raw_body, hashlib.sha256).hexdigest()

    assert verify_btcpay_signature(unsigned_settings, raw_body, signature) is False
    assert verify_btcpay_signature(signed_settings, raw_body, signature) is True
    assert verify_btcpay_signature(signed_settings, raw_body, "sha256=bad") is False


def test_ton_payment_link_points_to_tonkeeper_transfer():
    settings = make_settings(BILLING_ENABLE_TON=True, TON_RECEIVER_ADDRESS="EQD_founderpilot_wallet")
    order = {"id": "order 42", "amount": "1.5"}

    link = build_ton_payment_link(settings, order)

    assert link.startswith("https://app.tonkeeper.com/transfer/EQD_founderpilot_wallet?")
    assert "amount=1500000000" in link
    assert "text=order%2042" in link
    assert "exp=" in link


def test_public_runtime_rejects_dev_auth_and_weak_secret():
    settings = make_settings(
        WEBAPP_PUBLIC_URL="https://founderpilot.example",
        DEV_SKIP_TELEGRAM_AUTH=True,
        APP_SECRET="change-this-super-secret-string",
    )

    with pytest.raises(RuntimeError) as exc:
        require_runtime_settings(settings)

    message = str(exc.value)
    assert "DEV_MODE/DEV_SKIP_TELEGRAM_AUTH" in message
    assert "APP_SECRET" in message


def test_billing_checkout_alias_is_registered():
    app = create_app(make_settings())
    paths = {route.path for route in app.routes}

    assert "/api/billing/create-order" in paths
    assert "/api/billing/checkout" in paths



def test_public_plans_match_mockup_prices_by_default():
    settings = make_settings()

    public_keys = list(public_plan_catalog(settings))
    catalog = plan_catalog(settings)

    assert public_keys == ["free", "go", "plus", "pro", "business"]
    assert catalog["pro"].price_rub == 2490
    assert catalog["business"].price_rub == 7990


def test_auto_provider_never_picks_unconfigured_yookassa():
    settings = make_settings(BILLING_ENABLE_STARS=True, TELEGRAM_STARS_RUB_VALUE="0.8", BILLING_ENABLE_YOOKASSA=True)

    assert "yookassa" not in {provider["id"] for provider in enabled_providers(settings)}
    assert resolve_payment_provider(settings, "auto") == "telegram_stars"


def test_payment_provider_aliases_are_normalized():
    settings = make_settings(
        YOOKASSA_SHOP_ID="shop",
        YOOKASSA_SECRET_KEY="secret",
        BILLING_ENABLE_STARS=True,
        TELEGRAM_STARS_RUB_VALUE="0.8",
    )

    assert resolve_payment_provider(settings, "card") == "yookassa"
    assert resolve_payment_provider(settings, "stars") == "telegram_stars"


def test_yookassa_recurring_is_disabled_by_default_in_provider_metadata():
    settings = make_settings(YOOKASSA_SHOP_ID="shop", YOOKASSA_SECRET_KEY="secret")
    yookassa = next(provider for provider in enabled_providers(settings) if provider["id"] == "yookassa")

    assert settings.yookassa_enable_saved_payment_method is False
    assert yookassa["recurring_available"] is False


@pytest.mark.asyncio
async def test_yookassa_recurring_forbidden_falls_back_to_one_time_payment(monkeypatch):
    from app import billing as billing_module
    from app.billing import create_yookassa_payment

    settings = make_settings(
        YOOKASSA_SHOP_ID="shop",
        YOOKASSA_SECRET_KEY="secret",
        YOOKASSA_ENABLE_SAVED_PAYMENT_METHOD=True,
    )
    plan = plan_catalog(settings)["go"]
    order = {"id": "ord_test", "amount": "399", "telegram_user_id": 123}
    calls = []

    class FakeResponse:
        def __init__(self, status_code, payload):
            self.status_code = status_code
            self._payload = payload
            import json
            self.text = json.dumps(payload)

        def json(self):
            return self._payload

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json, auth, headers):  # noqa: A002
            calls.append({"json": json, "headers": headers})
            if len(calls) == 1:
                return FakeResponse(403, {
                    "type": "error",
                    "id": "019e74f-45b701bb-56b1590ed4b",
                    "description": "This store can't make recurring payments. Contact the YooMoney manager to learn more",
                    "code": "forbidden",
                })
            return FakeResponse(200, {
                "id": "pay_1",
                "confirmation": {"confirmation_url": "https://pay.example.test/checkout"},
            })

    monkeypatch.setattr(billing_module.httpx, "AsyncClient", FakeAsyncClient)

    external_id, url = await create_yookassa_payment(settings, order, plan, save_payment_method=True)

    assert external_id == "pay_1"
    assert url == "https://pay.example.test/checkout"
    assert calls[0]["json"]["save_payment_method"] is True
    assert "save_payment_method" not in calls[1]["json"]
    assert calls[1]["json"]["metadata"]["auto_renew"] == "0"
