import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.db import Database
from app.main import create_app
from app.openrouter_client import AIClientError, OpenRouterClient


def make_settings(tmp_path):
    return Settings(
        _env_file=None,
        BOT_TOKEN="123:token",
        OPENROUTER_API_KEY="openrouter-key",
        APP_SECRET="x" * 32,
        DEV_MODE=True,
        DEV_SKIP_TELEGRAM_AUTH=True,
        DATABASE_PATH=str(tmp_path / "app.sqlite3"),
        OPENROUTER_MODEL="openrouter/default",
        FREE_MONTHLY_CREDITS=2_000_000_000,
        FREE_DAILY_CREDITS=2_000_000_000,
        FREE_TRIAL_REQUESTS=2_000_000_000,
    )


def test_chat_user_message_is_saved_even_if_ai_provider_fails(tmp_path, monkeypatch):
    async def fail_chat(*args, **kwargs):
        raise AIClientError("provider down")

    monkeypatch.setattr(OpenRouterClient, "ask_chat", fail_chat)
    app = create_app(make_settings(tmp_path))

    with TestClient(app) as client:
        response = client.post("/api/chat", json={"message": "запомни этот диалог"})
        assert response.status_code == 200
        body = response.json()
        assert body["ok"] is False
        conversation_id = body["conversation_id"]

        history = client.get(f"/api/conversations/{conversation_id}").json()

    assert history["conversation"]["id"] == conversation_id
    assert [m["role"] for m in history["messages"]] == ["user"]
    assert history["messages"][0]["content"] == "запомни этот диалог"


@pytest.mark.anyio
async def test_admin_adjust_purchased_credits_records_transaction(tmp_path):
    db = Database(str(tmp_path / "app.sqlite3"))
    await db.init()

    result = await db.adjust_purchased_credits(12345, 999, 500, "manual bonus")
    assert result["purchased_credits"] == 500

    result = await db.adjust_purchased_credits(12345, 999, -200, "correction")
    assert result["purchased_credits"] == 300

    rows = await db.list_credit_transactions(12345, limit=10)
    assert rows[0]["transaction_type"] == "admin_revoke"
    assert rows[0]["balance_after"] == 300
    assert rows[1]["transaction_type"] == "admin_grant"
    assert rows[1]["balance_after"] == 500
