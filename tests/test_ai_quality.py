from app.ai_quality import detect_chat_intent, plan_answer_budget, safe_ai_error, sanitize_ai_output
from app.config import Settings
from app.openrouter_client import OpenRouterClient


def test_detect_casual_greeting_does_not_become_business():
    intent = detect_chat_intent("привет")
    assert intent.key == "casual"
    assert intent.max_tokens <= 700


def test_detect_business_and_code_intents():
    assert detect_chat_intent("посчитай маржу товара на Ozon").key in {"business", "calculation"}
    assert detect_chat_intent("пофикси python traceback").key == "code"


def test_plan_answer_budget_caps_free_and_allows_pro_more_depth():
    assert plan_answer_budget("free", 5000) <= 900
    assert plan_answer_budget("pro", 5000) > plan_answer_budget("free", 5000)


def test_safe_ai_error_hides_provider_json():
    msg = safe_ai_error(403, '{"error":{"message":"API key invalid","code":"forbidden"}}')
    assert "API key" not in msg
    assert "AI" in msg


def test_sanitize_ai_output_removes_markdown_wrapper():
    assert sanitize_ai_output("```markdown\n# Заголовок\n```") == "# Заголовок"


def test_plan_model_routing_falls_back_to_default():
    settings = Settings(
        OPENROUTER_MODEL="openrouter/default",
        OPENROUTER_MODEL_PRO="openrouter/pro-model",
    )
    client = OpenRouterClient(settings)
    assert client.model_for_plan("pro") == "openrouter/pro-model"
    assert client.model_for_plan("free") == "openrouter/default"

from fastapi.testclient import TestClient
from app.main import create_app


def test_ai_status_endpoint_uses_plan_model(tmp_path):
    settings = Settings(
        _env_file=None,
        BOT_TOKEN="123:token",
        OPENROUTER_API_KEY="openrouter-key",
        APP_SECRET="x" * 32,
        DEV_MODE=True,
        DEV_SKIP_TELEGRAM_AUTH=True,
        DATABASE_PATH=str(tmp_path / "app.sqlite3"),
        OPENROUTER_MODEL="openrouter/default",
    )
    app = create_app(settings)
    with TestClient(app) as client:
        response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["plan"] == "free"
    assert data["model"] == "openrouter/default"
