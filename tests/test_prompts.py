from app.prompts import MODES, build_user_prompt, get_mini_app_tools, get_mode


def test_modes_exist():
    assert "strategy" in MODES
    assert "offer" in MODES
    assert "unit" in MODES
    assert "wb_ozon_card" in MODES
    assert "margin_calc" in MODES
    assert "review_reply" in MODES


def test_unknown_mode_falls_back_to_strategy():
    assert get_mode("unknown").key == "strategy"


def test_user_prompt_contains_text():
    prompt = build_user_prompt("swot", "Мой бизнес: кофейня")
    assert "SWOT" in prompt
    assert "кофейня" in prompt


def test_mini_app_tools_are_exposed():
    tools = get_mini_app_tools()
    assert len(tools) == 11
    assert tools[0].key == "wb_ozon_card"
