from __future__ import annotations

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

    billing_enable_stars: bool = Field(default=True, alias="BILLING_ENABLE_STARS")
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


def require_runtime_settings(settings: Settings) -> None:
    missing: list[str] = []
    if not settings.bot_token or settings.bot_token == "PASTE_TELEGRAM_BOT_TOKEN_HERE":
        missing.append("BOT_TOKEN")
    if not settings.openrouter_api_key or settings.openrouter_api_key == "PASTE_OPENROUTER_API_KEY_HERE":
        missing.append("OPENROUTER_API_KEY")
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required .env value(s): {joined}. Edit .env first.")

    unsafe: list[str] = []
    if settings.is_public_deployment and settings.allow_dev_auth:
        unsafe.append("DEV_MODE/DEV_SKIP_TELEGRAM_AUTH must be false for a public HTTPS deployment")
    if settings.is_public_deployment and _is_default_or_weak_secret(
        settings.app_secret,
        {"change-this-super-secret-string", "change-this-secret"},
    ):
        unsafe.append("APP_SECRET must be a unique random value of at least 24 characters")
    if settings.admin_secret and _is_default_or_weak_secret(
        settings.admin_secret,
        {"change-this-admin-secret", "admin", "password"},
    ):
        unsafe.append("ADMIN_SECRET must be a unique random value of at least 24 characters")
    if settings.billing_enable_btcpay and not settings.btcpay_webhook_secret:
        unsafe.append("BTCPAY_WEBHOOK_SECRET is required when BILLING_ENABLE_BTCPAY=true")
    if unsafe:
        raise RuntimeError("Unsafe runtime settings: " + "; ".join(unsafe))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
