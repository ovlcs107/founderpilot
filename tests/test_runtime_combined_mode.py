from app.config import Settings
from app.openrouter_client import OpenRouterClient


def test_combined_mode_runs_web_and_bot_even_with_legacy_flag_false():
    settings = Settings(
        _env_file=None,
        BOT_TOKEN="123:token",
        BOT_SERVICE_MODE="combined",
        RUN_BOT_POLLING=False,
    )
    assert settings.should_run_web is True
    assert settings.should_run_bot is True


def test_web_mode_disables_polling_without_killing_web():
    settings = Settings(
        _env_file=None,
        BOT_TOKEN="123:token",
        BOT_SERVICE_MODE="web",
        RUN_BOT_POLLING=False,
    )
    assert settings.should_run_web is True
    assert settings.should_run_bot is False


def test_openrouter_candidate_models_preserve_primary_and_unique_fallbacks():
    settings = Settings(
        _env_file=None,
        OPENROUTER_MODEL="primary/model",
        OPENROUTER_FALLBACK_MODELS="fallback/one, fallback/two, fallback/one",
    )
    client = OpenRouterClient(settings)
    assert client.candidate_models("primary/model") == ["primary/model", "fallback/one", "fallback/two"]
