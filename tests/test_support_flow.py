import asyncio

from app.features import FeatureStore, init_features


def test_support_ticket_reply_bridge(tmp_path):
    async def scenario():
        db_path = str(tmp_path / "support.sqlite3")
        await init_features(db_path)
        store = FeatureStore(db_path)

        ticket = await store.create_support_ticket(
            123,
            subject="Не обновилась подписка",
            message="Оплатил Pro, но в профиле Free",
            category="payment",
            user_name="Максим",
            username="max_example",
            plan="free",
        )
        await store.update_support_ticket_bridge(ticket["id"], -100777, 55)

        found = await store.find_support_ticket_by_group_message(-100777, 55)
        assert found["id"] == ticket["id"]

        await store.add_support_message(
            ticket["id"],
            author_type="support",
            author_telegram_id=999,
            author_name="Support",
            content="Проверили оплату, тариф активирован.",
            source="telegram_group",
            status="answered",
        )

        messages = await store.list_support_messages_for_user(123, ticket["id"])
        assert len(messages) == 2
        assert messages[-1]["author_type"] == "support"
        assert "тариф активирован" in messages[-1]["content"]
        updated = await store.get_support_ticket_for_user(123, ticket["id"])
        assert updated["status"] == "answered"

    asyncio.run(scenario())
