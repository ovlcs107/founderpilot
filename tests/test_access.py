import asyncio

from app.db import Database


def test_free_trial_blocks_after_limit(tmp_path):
    async def scenario():
        db = Database(str(tmp_path / "access.sqlite3"))
        await db.init()
        await db.upsert_user(10, "seller", "Test", "User")
        for index in range(2):
            await db.save_request(10, "swot", f"request {index}", "answer")

        access = await db.get_access_state(10, free_limit_default=2, monthly_limit_default=300)

        assert access["plan"] == "free"
        assert access["remaining"] == 0
        assert access["can_request"] is False

    asyncio.run(scenario())


def test_unlimited_access_has_no_limit(tmp_path):
    async def scenario():
        db = Database(str(tmp_path / "access.sqlite3"))
        await db.init()
        await db.set_unlimited_access(10, admin_id=1, enabled=True, note="test")

        access = await db.get_access_state(10, free_limit_default=1, monthly_limit_default=300)

        assert access["plan"] == "unlimited"
        assert access["current_limit"] is None
        assert access["remaining"] is None
        assert access["can_request"] is True

    asyncio.run(scenario())


def test_chat_messages_count_as_usage(tmp_path):
    async def scenario():
        db = Database(str(tmp_path / "chat.sqlite3"))
        await db.init()
        conversation_id = await db.create_conversation(20, "Маржа товара")
        await db.add_chat_message(conversation_id, "user", "Посчитай маржу")
        await db.add_chat_message(conversation_id, "assistant", "Расчет готов")

        access = await db.get_access_state(20, free_limit_default=15, monthly_limit_default=300)
        messages = await db.list_chat_messages(conversation_id)
        conversations = await db.list_conversations(20)

        assert access["used_total"] == 1
        assert len(messages) == 2
        assert conversations[0]["id"] == conversation_id

    asyncio.run(scenario())
