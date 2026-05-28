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
    daily_free_limit: int = Field(default=20, alias="DAILY_FREE_LIMIT")
    free_trial_requests: int = Field(default=20, alias="FREE_TRIAL_REQUESTS")
    subscriber_monthly_limit: int = Field(default=300, alias="SUBSCRIBER_MONTHLY_LIMIT")
    per_minute_limit: int = Field(default=6, alias="PER_MINUTE_LIMIT")
    admin_telegram_ids_raw: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

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
