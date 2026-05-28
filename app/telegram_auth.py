from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl


@dataclass(frozen=True)
class TelegramUser:
    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class TelegramAuthError(RuntimeError):
    pass


def _secret_key(bot_token: str) -> bytes:
    return hmac.new(b"WebAppData", bot_token.encode("utf-8"), hashlib.sha256).digest()


def validate_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86400) -> TelegramUser:
    """Validate Telegram Mini App initData according to Telegram WebApp HMAC rules."""
    if not init_data:
        raise TelegramAuthError("Пустой initData от Telegram.")

    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise TelegramAuthError("В initData нет hash.")

    data_check_string = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    calculated_hash = hmac.new(_secret_key(bot_token), data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise TelegramAuthError("Неверная подпись Telegram initData.")

    auth_date_raw = parsed.get("auth_date")
    if not auth_date_raw:
        raise TelegramAuthError("В initData нет auth_date.")

    try:
        auth_date = int(auth_date_raw)
    except ValueError as exc:
        raise TelegramAuthError("Некорректный auth_date.") from exc

    if time.time() - auth_date > max_age_seconds:
        raise TelegramAuthError("Сессия Telegram Mini App устарела. Открой приложение заново.")

    user_raw = parsed.get("user")
    if not user_raw:
        raise TelegramAuthError("В initData нет user.")

    try:
        user_data = json.loads(user_raw)
    except json.JSONDecodeError as exc:
        raise TelegramAuthError("Некорректный JSON пользователя Telegram.") from exc

    telegram_id = user_data.get("id")
    if not isinstance(telegram_id, int):
        raise TelegramAuthError("В user нет корректного id.")

    return TelegramUser(
        id=telegram_id,
        username=user_data.get("username"),
        first_name=user_data.get("first_name"),
        last_name=user_data.get("last_name"),
    )


def dev_user() -> TelegramUser:
    return TelegramUser(id=1, username="dev", first_name="Local", last_name="Tester")
