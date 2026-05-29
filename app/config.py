from __future__ import annotations

import os
from functools import lru_cache
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(default="", alias="BOT_TOKEN")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openrouter/free", alias="OPENROUTER_MODEL")
    webapp_public_url: str = Field(default="http://127.0.0.1:8000", alias="WEBAPP_PUBLIC_URL")
    app_secret: str = Field(default="change-this-super-secret-string", alias="APP_SECRET")
    admin_secret: str = Field(default="", alias="ADMIN_SECRET")
    database_path: str = Field(default="founderpilot.sqlite3", alias="DATABASE_PATH")
    dev_mode: bool = Field(default=False, alias="DEV_MODE")
    dev_skip_telegram_auth: bool = Field(default=False, alias="DEV_SKIP_TELEGRAM_AUTH")
    cors_allowed_origins_raw: str = Field(default="", alias="CORS_ALLOWED_ORIGINS")
    trust_proxy_headers: bool = Field(default=True, alias="TRUST_PROXY_HEADERS")
    run_bot_polling: bool = Field(default=False, alias="RUN_BOT_POLLING")
    bot_polling_strict: bool = Field(default=False, alias="BOT_POLLING_STRICT")
    max_request_body_bytes: int = Field(default=262_144, alias="MAX_REQUEST_BODY_BYTES")
    daily_free_limit: int = Field(default=20, alias="DAILY_FREE_LIMIT")
    free_trial_requests: int = Field(default=20, alias="FREE_TRIAL_REQUESTS")
    subscriber_monthly_limit: int = Field(default=10000, alias="SUBSCRIBER_MONTHLY_LIMIT")
    free_monthly_credits: int = Field(default=100, alias="FREE_MONTHLY_CREDITS")
    public_plan_keys_raw: str = Field(default="free,go,plus,pro,business", alias="PUBLIC_PLAN_KEYS")
    payment_auto_provider_order_raw: str = Field(default="yookassa,telegram_stars,ton,btcpay_btc", alias="PAYMENT_AUTO_PROVIDER_ORDER")
    free_daily_credits: int = Field(default=20, alias="FREE_DAILY_CREDITS")
    go_daily_credits: int = Field(default=300, alias="GO_DAILY_CREDITS")
    go_monthly_credits: int = Field(default=3000, alias="GO_MONTHLY_CREDITS")
    plus_daily_credits: int = Field(default=800, alias="PLUS_DAILY_CREDITS")
    plus_monthly_credits: int = Field(default=10000, alias="PLUS_MONTHLY_CREDITS")
    pro_daily_credits: int = Field(default=2500, alias="PRO_DAILY_CREDITS")
    pro_monthly_credits: int = Field(default=30000, alias="PRO_MONTHLY_CREDITS")
    business_daily_credits: int = Field(default=10000, alias="BUSINESS_DAILY_CREDITS")
    business_monthly_credits: int = Field(default=100000, alias="BUSINESS_MONTHLY_CREDITS")
    per_minute_limit: int = Field(default=6, alias="PER_MINUTE_LIMIT")
    admin_telegram_ids_raw: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    strict_runtime_validation: bool = Field(default=False, alias="STRICT_RUNTIME_VALIDATION")

    billing_enable_stars: bool = Field(default=False, alias="BILLING_ENABLE_STARS")
    billing_enable_yookassa: bool = Field(default=False, alias="BILLING_ENABLE_YOOKASSA")
    billing_enable_ton: bool = Field(default=False, alias="BILLING_ENABLE_TON")
    billing_enable_btcpay: bool = Field(default=False, alias="BILLING_ENABLE_BTCPAY")

    go_price_rub: str = Field(default="399", alias="GO_PRICE_RUB")
    plus_price_rub: str = Field(default="990", alias="PLUS_PRICE_RUB")
    pro_price_rub: str = Field(default="2490", alias="PRO_PRICE_RUB")
    business_price_rub: str = Field(default="7990", alias="BUSINESS_PRICE_RUB")
    go_price_stars: int = Field(default=399, alias="GO_PRICE_STARS")
    plus_price_stars: int = Field(default=990, alias="PLUS_PRICE_STARS")
    pro_price_stars: int = Field(default=2490, alias="PRO_PRICE_STARS")
    business_price_stars: int = Field(default=7990, alias="BUSINESS_PRICE_STARS")
    go_price_ton: str = Field(default="1.8", alias="GO_PRICE_TON")
    plus_price_ton: str = Field(default="4.5", alias="PLUS_PRICE_TON")
    pro_price_ton: str = Field(default="11.3", alias="PRO_PRICE_TON")
    business_price_ton: str = Field(default="36.3", alias="BUSINESS_PRICE_TON")
    go_price_btc: str = Field(default="0.00004", alias="GO_PRICE_BTC")
    plus_price_btc: str = Field(default="0.00009", alias="PLUS_PRICE_BTC")
    pro_price_btc: str = Field(default="0.00023", alias="PRO_PRICE_BTC")
    business_price_btc: str = Field(default="0.00073", alias="BUSINESS_PRICE_BTC")

    # Unit economics guard. All numbers are deliberately configurable because model
    # prices, acquiring commissions, exchange rates and taxes can change. Defaults are
    # conservative for an MVP: requests are charged in credits by estimated token cost,
    # then credits are limited by each plan's monthly budget.
    profit_guard_enabled: bool = Field(default=True, alias="PROFIT_GUARD_ENABLED")
    yookassa_fee_rate: str = Field(default="0.035", alias="YOOKASSA_FEE_RATE")
    telegram_stars_fee_rate: str = Field(default="0.30", alias="TELEGRAM_STARS_FEE_RATE")
    ton_fee_rate: str = Field(default="0.02", alias="TON_FEE_RATE")
    btcpay_fee_rate: str = Field(default="0.02", alias="BTCPAY_FEE_RATE")
    tax_rate: str = Field(default="0.06", alias="TAX_RATE")
    refund_risk_rate: str = Field(default="0.03", alias="REFUND_RISK_RATE")
    max_ai_cost_share: str = Field(default="0.40", alias="MAX_AI_COST_SHARE")
    max_ai_cost_share_by_plan_raw: str = Field(default="free:0,go:0.35,plus:0.38,pro:0.42,business:0.35,default:0.40", alias="MAX_AI_COST_SHARE_BY_PLAN")
    free_ai_monthly_budget_rub: str = Field(default="0", alias="FREE_AI_MONTHLY_BUDGET_RUB")
    minimum_credit_value_rub: str = Field(default="0.01", alias="MINIMUM_CREDIT_VALUE_RUB")
    ai_input_cost_usd_per_m_tokens: str = Field(default="1.0", alias="AI_INPUT_COST_USD_PER_M_TOKENS")
    ai_output_cost_usd_per_m_tokens: str = Field(default="4.0", alias="AI_OUTPUT_COST_USD_PER_M_TOKENS")
    openrouter_fee_rate: str = Field(default="0.055", alias="OPENROUTER_FEE_RATE")
    usd_rub_rate: str = Field(default="100", alias="USD_RUB_RATE")
    ai_cost_safety_multiplier: str = Field(default="2.0", alias="AI_COST_SAFETY_MULTIPLIER")
    estimate_free_model_cost: bool = Field(default=False, alias="ESTIMATE_FREE_MODEL_COST")
    telegram_stars_rub_value: str = Field(default="0", alias="TELEGRAM_STARS_RUB_VALUE")
    ton_rub_rate: str = Field(default="0", alias="TON_RUB_RATE")
    btc_rub_rate: str = Field(default="0", alias="BTC_RUB_RATE")
    billing_allow_unpriced_stars: bool = Field(default=False, alias="BILLING_ALLOW_UNPRICED_STARS")

    yookassa_shop_id: str = Field(default="", alias="YOOKASSA_SHOP_ID")
    yookassa_secret_key: str = Field(default="", alias="YOOKASSA_SECRET_KEY")
    yookassa_return_url: str = Field(default="", alias="YOOKASSA_RETURN_URL")
    yookassa_enable_saved_payment_method: bool = Field(default=True, alias="YOOKASSA_ENABLE_SAVED_PAYMENT_METHOD")

    ton_receiver_address: str = Field(default="", alias="TON_RECEIVER_ADDRESS")
    ton_manifest_url: str = Field(default="", alias="TON_MANIFEST_URL")
    ton_api_key: str = Field(default="", alias="TON_API_KEY")
    ton_network: str = Field(default="mainnet", alias="TON_NETWORK")

    btcpay_url: str = Field(default="", alias="BTCPAY_URL")
    btcpay_store_id: str = Field(default="", alias="BTCPAY_STORE_ID")
    btcpay_api_key: str = Field(default="", alias="BTCPAY_API_KEY")
    btcpay_webhook_secret: str = Field(default="", alias="BTCPAY_WEBHOOK_SECRET")


    @property
    def is_railway_runtime(self) -> bool:
        return bool(
            os.getenv("RAILWAY_ENVIRONMENT")
            or os.getenv("RAILWAY_PROJECT_ID")
            or os.getenv("RAILWAY_SERVICE_ID")
            or os.getenv("RAILWAY_PUBLIC_DOMAIN")
        )

    @property
    def bind_host(self) -> str:
        # Railway healthchecks reach the container through its internal network.
        # If an old env has HOST=127.0.0.1/localhost, the app starts but Railway
        # sees "service unavailable" forever. On Railway we always bind publicly
        # inside the container; locally the HOST env is still respected.
        if self.is_railway_runtime:
            return "0.0.0.0"
        return self.host or "0.0.0.0"

    @field_validator("webapp_public_url")
    @classmethod
    def strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @property
    def webapp_url(self) -> str:
        return f"{self.webapp_public_url}/app"

    @property
    def telegram_webapp_enabled(self) -> bool:
        parsed = urlparse(self.webapp_url)
        return parsed.scheme.lower() == "https" and bool(parsed.netloc)

    @property
    def admin_telegram_ids(self) -> set[int]:
        ids: set[int] = set()
        for raw_id in self.admin_telegram_ids_raw.replace(",", " ").split():
            try:
                ids.add(int(raw_id))
            except ValueError:
                continue
        return ids

    @property
    def public_plan_keys(self) -> list[str]:
        raw_items = [
            item.strip().lower()
            for item in self.public_plan_keys_raw.replace(";", ",").replace(" ", ",").split(",")
            if item.strip()
        ]
        allowed = {"free", "go", "plus", "pro", "business"}
        result: list[str] = []
        for key in raw_items:
            if key in allowed and key not in result:
                result.append(key)
        if not result:
            result = ["free", "pro", "business"]
        if "free" in result:
            result.remove("free")
        return ["free", *result]

    @property
    def payment_auto_provider_order(self) -> list[str]:
        aliases = {"stars": "telegram_stars", "card": "yookassa", "sbp": "yookassa", "btc": "btcpay_btc"}
        allowed = {"telegram_stars", "yookassa", "ton", "btcpay_btc"}
        result: list[str] = []
        for raw in self.payment_auto_provider_order_raw.replace(";", ",").replace(" ", ",").split(","):
            key = aliases.get(raw.strip().lower(), raw.strip().lower())
            if key in allowed and key not in result:
                result.append(key)
        return result or ["yookassa", "telegram_stars", "ton", "btcpay_btc"]


    def is_admin(self, telegram_id: int) -> bool:
        return telegram_id in self.admin_telegram_ids

    @property
    def allow_dev_auth(self) -> bool:
        return self.dev_mode or self.dev_skip_telegram_auth

    @property
    def public_origin(self) -> str:
        parsed = urlparse(self.webapp_public_url)
        if not parsed.scheme or not parsed.netloc:
            return ""
        return f"{parsed.scheme}://{parsed.netloc}"

    @property
    def is_public_deployment(self) -> bool:
        parsed = urlparse(self.webapp_public_url)
        hostname = (parsed.hostname or "").lower()
        if parsed.scheme.lower() != "https":
            return False
        return hostname not in {"localhost", "127.0.0.1", "::1"}

    @property
    def cors_allowed_origins(self) -> list[str]:
        origins = [
            item.strip().rstrip("/")
            for item in self.cors_allowed_origins_raw.replace("\n", ",").split(",")
            if item.strip()
        ]
        if not origins and self.public_origin:
            origins.append(self.public_origin)

        parsed = urlparse(self.webapp_public_url)
        if self.allow_dev_auth or (parsed.hostname or "").lower() in {"localhost", "127.0.0.1"}:
            origins.extend(
                [
                    "http://127.0.0.1:8000",
                    "http://localhost:8000",
                    "http://127.0.0.1:5173",
                    "http://localhost:5173",
                ]
            )
        return sorted(set(origins))


def _is_default_or_weak_secret(value: str, defaults: set[str]) -> bool:
    clean = (value or "").strip()
    if not clean:
        return True
    if clean in defaults:
        return True
    return len(clean) < 24


def runtime_setting_issues(settings: Settings) -> list[str]:
    """Return deploy/runtime configuration problems without killing /health.

    Railway marks a deployment as failed when the process cannot answer /health.
    Therefore non-critical product settings (AI key, bot token, payment options)
    are reported as warnings and the exact feature is blocked later at request time.
    Set STRICT_RUNTIME_VALIDATION=true when you intentionally want such warnings
    to fail startup in staging/CI.
    """
    issues: list[str] = []
    if not settings.bot_token or settings.bot_token == "PASTE_TELEGRAM_BOT_TOKEN_HERE":
        issues.append("BOT_TOKEN is empty: Telegram Mini App auth and bot messages will not work")
    if not settings.openrouter_api_key or settings.openrouter_api_key == "PASTE_OPENROUTER_API_KEY_HERE":
        issues.append("OPENROUTER_API_KEY is empty: AI generation requests will be disabled")
    if settings.is_public_deployment and settings.allow_dev_auth:
        issues.append("DEV_MODE/DEV_SKIP_TELEGRAM_AUTH must be false for a public HTTPS deployment")
    if settings.is_public_deployment and _is_default_or_weak_secret(
        settings.app_secret,
        {"change-this-super-secret-string", "change-this-secret"},
    ):
        issues.append("APP_SECRET must be a unique random value of at least 24 characters")
    if settings.admin_secret and _is_default_or_weak_secret(
        settings.admin_secret,
        {"change-this-admin-secret", "admin", "password"},
    ):
        issues.append("ADMIN_SECRET must be a unique random value of at least 24 characters")
    if settings.billing_enable_btcpay and not settings.btcpay_webhook_secret:
        issues.append("BTCPAY_WEBHOOK_SECRET is required when BILLING_ENABLE_BTCPAY=true")
    if settings.billing_enable_stars and not settings.billing_allow_unpriced_stars:
        try:
            stars_value = float(settings.telegram_stars_rub_value or 0)
        except ValueError:
            stars_value = 0
        if stars_value <= 0:
            issues.append("TELEGRAM_STARS_RUB_VALUE must be set or BILLING_ALLOW_UNPRICED_STARS=true when BILLING_ENABLE_STARS=true")
    return issues


def require_runtime_settings(settings: Settings) -> None:
    issues = runtime_setting_issues(settings)
    if issues:
        raise RuntimeError("Runtime settings validation failed: " + "; ".join(issues))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
