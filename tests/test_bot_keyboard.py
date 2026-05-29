from app.bot import build_main_keyboard
from app.config import Settings


def test_main_keyboard_shows_only_telegram_channel_button():
    keyboard = build_main_keyboard(Settings(TELEGRAM_CHANNEL_URL="https://t.me/founderpilot_news"))

    buttons = [button for row in keyboard.inline_keyboard for button in row]

    assert len(buttons) == 1
    assert buttons[0].text == "📣 Telegram канал"
    assert buttons[0].url == "https://t.me/founderpilot_news"
    assert buttons[0].callback_data is None
    assert buttons[0].web_app is None


def test_main_keyboard_skips_invalid_channel_url():
    keyboard = build_main_keyboard(Settings(TELEGRAM_CHANNEL_URL=""))

    assert keyboard.inline_keyboard == []
