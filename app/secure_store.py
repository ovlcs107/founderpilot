from __future__ import annotations

import base64
import hashlib
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


def _key(secret: str) -> bytes:
    raw = hashlib.sha256((secret or "change-this-secret").encode("utf-8")).digest()
    return base64.urlsafe_b64encode(raw)


def encrypt_text(value: str | None, secret: str) -> str | None:
    if value is None:
        return None
    text = str(value)
    if not text:
        return None
    return Fernet(_key(secret)).encrypt(text.encode("utf-8")).decode("utf-8")


def decrypt_text(token: str | None, secret: str) -> str | None:
    if not token:
        return None
    try:
        return Fernet(_key(secret)).decrypt(str(token).encode("utf-8")).decode("utf-8")
    except (InvalidToken, ValueError):
        return None


def only_digits(value: str | None) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def mask_account(value: str | None) -> str:
    digits = only_digits(value)
    if len(digits) < 8:
        return "••••"
    return f"{digits[:5]}•••••••••••{digits[-4:]}"


def mask_token(value: str | None) -> str:
    text = str(value or "")
    if len(text) <= 8:
        return "••••"
    return f"{text[:4]}••••{text[-4:]}"
