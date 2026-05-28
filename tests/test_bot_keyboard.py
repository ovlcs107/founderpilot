from app.bot import build_main_keyboard
from app.config import Settings


def test_main_keyboard_skips_webapp_button_for_local_http_url():
    keyboard = build_main_keyboard(Settings(WEBAPP_PUBLIC_URL="http://127.0.0.1:8000"))

    buttons = [button for row in keyboard.inline_keyboard for button in row]

    assert len(buttons) == 1
    assert buttons[0].callback_data == "help"
    assert buttons[0].web_app is None


def test_main_keyboard_uses_webapp_button_for_https_url():
    keyboard = build_main_keyboard(Settings(WEBAPP_PUBLIC_URL="https://example.com"))

    first_button = keyboard.inline_keyboard[0][0]

    assert first_button.web_app is not None
    assert first_button.web_app.url == "https://example.com/app"
