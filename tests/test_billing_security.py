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
    settings = make_settings(BILLING_ENABLE_STARS=True, BILLING_ENABLE_YOOKASSA=True)

    assert "yookassa" not in {provider["id"] for provider in enabled_providers(settings)}
    assert resolve_payment_provider(settings, "auto") == "telegram_stars"


def test_payment_provider_aliases_are_normalized():
    settings = make_settings(YOOKASSA_SHOP_ID="shop", YOOKASSA_SECRET_KEY="secret")

    assert resolve_payment_provider(settings, "card") == "yookassa"
    assert resolve_payment_provider(settings, "stars") == "telegram_stars"
