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
    daily_free_limit: int = Field(default=100, alias="DAILY_FREE_LIMIT")
    free_trial_requests: int = Field(default=100, alias="FREE_TRIAL_REQUESTS")
    subscriber_monthly_limit: int = Field(default=10000, alias="SUBSCRIBER_MONTHLY_LIMIT")
    free_daily_credits: int = Field(default=100, alias="FREE_DAILY_CREDITS")
    go_daily_credits: int = Field(default=250, alias="GO_DAILY_CREDITS")
    go_monthly_credits: int = Field(default=5000, alias="GO_MONTHLY_CREDITS")
    plus_daily_credits: int = Field(default=800, alias="PLUS_DAILY_CREDITS")
    plus_monthly_credits: int = Field(default=20000, alias="PLUS_MONTHLY_CREDITS")
    pro_daily_credits: int = Field(default=2000, alias="PRO_DAILY_CREDITS")
    pro_monthly_credits: int = Field(default=80000, alias="PRO_MONTHLY_CREDITS")
    business_daily_credits: int = Field(default=10000, alias="BUSINESS_DAILY_CREDITS")
    business_monthly_credits: int = Field(default=300000, alias="BUSINESS_MONTHLY_CREDITS")
    per_minute_limit: int = Field(default=6, alias="PER_MINUTE_LIMIT")
    admin_telegram_ids_raw: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    billing_enable_stars: bool = Field(default=True, alias="BILLING_ENABLE_STARS")
    billing_enable_yookassa: bool = Field(default=False, alias="BILLING_ENABLE_YOOKASSA")
    billing_enable_ton: bool = Field(default=False, alias="BILLING_ENABLE_TON")
    billing_enable_btcpay: bool = Field(default=False, alias="BILLING_ENABLE_BTCPAY")

    go_price_rub: str = Field(default="299", alias="GO_PRICE_RUB")
    plus_price_rub: str = Field(default="699", alias="PLUS_PRICE_RUB")
    pro_price_rub: str = Field(default="1490", alias="PRO_PRICE_RUB")
    business_price_rub: str = Field(default="3990", alias="BUSINESS_PRICE_RUB")
    go_price_stars: int = Field(default=299, alias="GO_PRICE_STARS")
    plus_price_stars: int = Field(default=699, alias="PLUS_PRICE_STARS")
    pro_price_stars: int = Field(default=1490, alias="PRO_PRICE_STARS")
    business_price_stars: int = Field(default=3990, alias="BUSINESS_PRICE_STARS")
    go_price_ton: str = Field(default="1.5", alias="GO_PRICE_TON")
    plus_price_ton: str = Field(default="3", alias="PLUS_PRICE_TON")
    pro_price_ton: str = Field(default="6", alias="PRO_PRICE_TON")
    business_price_ton: str = Field(default="15", alias="BUSINESS_PRICE_TON")
    go_price_btc: str = Field(default="0.00002", alias="GO_PRICE_BTC")
    plus_price_btc: str = Field(default="0.00004", alias="PLUS_PRICE_BTC")
    pro_price_btc: str = Field(default="0.00008", alias="PRO_PRICE_BTC")
    business_price_btc: str = Field(default="0.00020", alias="BUSINESS_PRICE_BTC")

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

    def is_admin(self, telegram_id: int) -> bool:
        return telegram_id in self.admin_telegram_ids

    @property
    def allow_dev_auth(self) -> bool:
        return self.dev_mode or self.dev_skip_telegram_auth


def require_runtime_settings(settings: Settings) -> None:
    missing: list[str] = []
    if not settings.bot_token or settings.bot_token == "PASTE_TELEGRAM_BOT_TOKEN_HERE":
        missing.append("BOT_TOKEN")
    if not settings.openrouter_api_key or settings.openrouter_api_key == "PASTE_OPENROUTER_API_KEY_HERE":
        missing.append("OPENROUTER_API_KEY")
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing required .env value(s): {joined}. Edit .env first.")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
