from __future__ import annotations

import re
from html import escape

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, PreCheckoutQuery, WebAppInfo

from app.billing import activate_subscription, plan_catalog
from app.credits import estimate_credits, estimate_output_tokens
from app.config import Settings
from app.db import Database
from app.openrouter_client import AIClientError, OpenRouterClient
from app.rate_limit import RateLimitError, RateLimiter
from app.features import FeatureStore, init_features


TG_MESSAGE_LIMIT = 4096
TELEGRAM_PARSE_MODE = "HTML"


def split_for_telegram(text: str, limit: int = 3900) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    current = text
    while len(current) > limit:
        cut = current.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = current.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(current[:cut].strip())
        current = current[cut:].strip()
    if current:
        chunks.append(current)
    return chunks


def build_main_keyboard(settings: Settings) -> InlineKeyboardMarkup:
    keyboard: list[list[InlineKeyboardButton]] = []
    if settings.telegram_webapp_enabled:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Открыть FounderPilot AI",
                    web_app=WebAppInfo(url=settings.webapp_url),
                )
            ]
        )
    keyboard.append([InlineKeyboardButton(text="Как получить сильный разбор", callback_data="help")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def html(value: object) -> str:
    return escape(str(value), quote=False)


def format_limit(value: object) -> str:
    return "без лимита" if value is None else str(value)


def format_user_title(user: dict) -> str:
    username = user.get("username")
    name = " ".join(str(user.get(key) or "").strip() for key in ("first_name", "last_name")).strip()
    if username:
        return f"@{username}"
    return name or str(user.get("telegram_id"))


def build_dispatcher(
    settings: Settings,
    db: Database,
    ai_client: OpenRouterClient,
    rate_limiter: RateLimiter,
) -> Dispatcher:
    router = Router()
    support_store = FeatureStore(settings.database_path)

    @router.pre_checkout_query()
    async def pre_checkout(query: PreCheckoutQuery) -> None:
        payload = query.invoice_payload or ""
        order = await db.get_billing_order(payload) if payload.startswith("ord_") else None
        if not order or order.get("status") not in {"pending", "failed"}:
            await query.answer(ok=False, error_message="Заказ не найден или уже обработан.")
            return
        plan = plan_catalog(settings).get(str(order.get("plan")))
        if order.get("provider") != "telegram_stars" or not plan or query.currency != "XTR" or int(query.total_amount or 0) != int(plan.price_stars):
            await db.update_billing_order(payload, status="failed")
            await query.answer(ok=False, error_message="Order payment data mismatch.")
            return
        await query.answer(ok=True)

    @router.message(F.successful_payment)
    async def successful_payment(message: Message) -> None:
        payment = message.successful_payment
        if not payment or not message.from_user:
            return
        order_id = payment.invoice_payload
        order = await db.get_billing_order(order_id) if order_id else None
        if not order:
            await message.answer("Платёж получен, но заказ не найден. Напишите администратору.")
            return
        plans = plan_catalog(settings)
        plan = plans.get(str(order.get("plan")))
        if not plan:
            await message.answer("Платёж получен, но тариф не найден. Напишите администратору.")
            return
        expected_amount = int(plan.price_stars)
        actual_amount = int(getattr(payment, "total_amount", 0) or 0)
        if order.get("provider") != "telegram_stars" or payment.currency != "XTR" or actual_amount != expected_amount:
            await db.update_billing_order(order_id, status="failed")
            await db.log_error(
                "telegram_stars_payment_mismatch",
                f"order={order_id} provider={order.get('provider')} currency={payment.currency} amount={actual_amount} expected={expected_amount}",
                message.from_user.id,
            )
            await message.answer("Payment received, but order data mismatch. Contact support.")
            return
        order_user_id = int(order.get("telegram_user_id") or message.from_user.id)
        if order_user_id != message.from_user.id:
            await db.log_error("telegram_stars_payer_mismatch", f"order={order_id} payer={message.from_user.id} owner={order_user_id}", order_user_id)
        result = await activate_subscription(
            db,
            order_user_id,
            plan.key,
            "telegram_stars",
            order_id,
            plan.daily_limit,
            plan.monthly_limit,
        )
        await db.record_payment(
            order_id=order_id,
            telegram_id=order_user_id,
            provider="telegram_stars",
            plan=plan.key,
            amount=float(order.get("amount") or 0),
            currency="XTR",
            status="paid",
            external_payment_id=getattr(payment, "telegram_payment_charge_id", None),
            external_charge_id=getattr(payment, "provider_payment_charge_id", None),
            payload=order_id,
            raw_event=payment.model_dump() if hasattr(payment, "model_dump") else {},
        )
        await message.answer(
            f"<b>Подписка активирована</b>\n"
            f"Тариф: <b>{html(plan.title)}</b>\n"
            f"Лимит: <b>{plan.daily_limit}</b> кредитов в день.\n"
            f"Действует до: <code>{html(result['expires_at'])}</code>",
            parse_mode=TELEGRAM_PARSE_MODE,
            reply_markup=build_main_keyboard(settings),
        )

    @router.message(Command("start"))
    async def start(message: Message, command: CommandObject) -> None:
        user = message.from_user
        if user:
            await db.upsert_user(user.id, user.username, user.first_name, user.last_name)
            if command.args:
                await db.set_referrer(user.id, command.args.strip())

        action_hint = "Откройте Mini App или отправьте задачу прямо в чат."
        if not settings.telegram_webapp_enabled:
            action_hint = (
                "Mini App будет доступен после подключения публичного HTTPS-адреса. "
                "Сейчас можно отправить задачу прямо в чат."
            )
        text = (
            "<b>FounderPilot AI</b>\n"
            "FounderPilot AI - помощник для предпринимателей и селлеров WB/Ozon. "
            "Поможет собрать оффер, карточку товара, рекламу, SWOT, план продаж, контент и расчет маржи.\n\n"
            "<b>Примеры задач:</b>\n"
            "- улучшить карточку товара для WB/Ozon;\n"
            "- посчитать маржу и риски цены;\n"
            "- написать ответ на отзыв или рекламный оффер.\n\n"
            "<b>Как начать:</b>\n"
            f"{action_hint} Чем точнее вводные, тем практичнее результат."
        )
        await message.answer(text, parse_mode=TELEGRAM_PARSE_MODE, reply_markup=build_main_keyboard(settings))

    @router.message(Command("app"))
    async def app_command(message: Message) -> None:
        await message.answer(
            "<b>FounderPilot AI Mini App</b>\n\n"
            "Основной интерфейс находится в Mini App: AI Chat, инструменты, история, профиль бизнеса и сохраненные результаты.",
            parse_mode=TELEGRAM_PARSE_MODE,
            reply_markup=build_main_keyboard(settings),
        )

    @router.message(Command("help"))
    async def help_command(message: Message) -> None:
        webapp_step = (
            "Откройте Mini App через /start или /app. Также можно отправить запрос прямо в чат.\n"
            if settings.telegram_webapp_enabled
            else "Для Mini App укажите публичный HTTPS <code>WEBAPP_PUBLIC_URL</code>. До этого можно отправлять запросы прямо в чат.\n"
        )
        await message.answer(
            "<b>Что умеет FounderPilot AI</b>\n\n"
            f"{webapp_step}"
            "\n<b>Основные задачи:</b>\n"
            "- AI Chat для бизнес-вопросов;\n"
            "- карточки WB/Ozon, офферы, реклама и ответы на отзывы;\n"
            "- расчет маржи, SWOT, контент-план и план продаж;\n"
            "- история, сохраненные результаты и профиль бизнеса.\n\n"
            "<b>Шаблон запроса:</b>\n"
            "<pre>Ниша:\nКлиент:\nПродукт:\nЦена:\nЦель:\nОграничения:</pre>",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    @router.message(Command("stats"))
    async def stats_command(message: Message) -> None:
        if not message.from_user:
            await message.answer("Не удалось определить Telegram user id. Откройте бота из обычного Telegram-аккаунта.")
            return
        access = await db.get_access_state(
            message.from_user.id,
            free_limit_default=settings.free_trial_requests,
            monthly_limit_default=settings.subscriber_monthly_limit,
        )
        await message.answer(
            "<b>Доступ FounderPilot AI</b>\n"
            f"Статус: <b>{html(access['status_label'])}</b>\n"
            f"Кредитов сегодня: <b>{access['used_today']}</b>\n"
            f"Кредитов за период: <b>{access['used_period']}/{format_limit(access['current_limit'])}</b>\n"
            f"Осталось: <b>{format_limit(access['remaining'])}</b>\n"
            f"Антиспам: <b>{settings.per_minute_limit}</b> запросов в минуту.",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    def is_admin_message(message: Message) -> bool:
        return bool(message.from_user and settings.is_admin(message.from_user.id))

    async def deny_non_admin(message: Message) -> bool:
        if is_admin_message(message):
            return False
        await message.answer("Команда доступна только администратору.")
        return True

    @router.message(Command("admin"))
    async def admin_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        await message.answer(
            "<b>Администрирование FounderPilot AI</b>\n\n"
            "<code>/users [limit]</code> — список пользователей\n"
            "<code>/user &lt;telegram_id&gt;</code> — карточка пользователя\n"
            "<code>/setplan &lt;id&gt; &lt;free|go|plus|pro|business&gt; [days] [note]</code> — выдать тариф\n"
            "<code>/addcredits &lt;id&gt; &lt;amount&gt; [note]</code> — начислить кредиты\n"
            "<code>/takecredits &lt;id&gt; &lt;amount&gt; [note]</code> — списать кредиты\n"
            "<code>/credits &lt;id&gt; [limit]</code> — операции по кредитам\n"
            "<code>/grant &lt;id&gt; &lt;days&gt; [monthly_limit] [note]</code> — ручная подписка\n"
            "<code>/unlimited &lt;id&gt; [note]</code> — выдать unlimited\n"
            "<code>/revoke &lt;id&gt; [note]</code> — вернуть на Free\n"
            "<code>/free_limit &lt;id&gt; &lt;count&gt; [note]</code> — изменить Free-кредиты\n"
            "<code>/block &lt;id&gt; [note]</code> / <code>/unblock &lt;id&gt;</code> — блокировка\n"
            "<code>/orders [limit] [status]</code> — заказы\n"
            "<code>/payments [limit]</code> — платежи\n"
            "<code>/errors [limit]</code> — ошибки\n"
            "<code>/admin_stats</code> — сводка проекта\n"
            "<code>/user_history &lt;id&gt; [limit]</code> — диалоги пользователя\n"
            "<code>/clear_history &lt;id&gt; [note]</code> — архивировать диалоги",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    @router.message(Command("users"))
    async def users_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=1)
        limit = 20
        if len(parts) > 1:
            try:
                limit = max(1, min(int(parts[1]), 50))
            except ValueError:
                limit = 20
        users = await db.list_users(limit=limit)
        if not users:
            await message.answer("Пользователей пока нет.")
            return
        lines = ["<b>Пользователи</b>"]
        for item in users:
            title = html(format_user_title(item))
            plan = html(item.get("plan") or "free")
            total = int(item.get("requests_total") or 0)
            purchased = int(item.get("purchased_credits") or 0)
            lines.append(f"<code>{item['telegram_id']}</code> — {title} — {plan} — +{purchased} — {total} запросов")
        await message.answer("\n".join(lines), parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("user"))
    async def user_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("Формат: <code>/user &lt;telegram_id&gt;</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
        except ValueError:
            await message.answer("Telegram id должен быть числом.")
            return
        profile = await db.get_user_profile(telegram_id)
        if not profile:
            await message.answer("Пользователь не найден.")
            return
        access = await db.get_access_state(
            telegram_id,
            free_limit_default=settings.free_trial_requests,
            monthly_limit_default=settings.subscriber_monthly_limit,
        )
        await message.answer(
            "<b>Пользователь</b>\n"
            f"ID: <code>{telegram_id}</code>\n"
            f"Имя: <b>{html(format_user_title(profile))}</b>\n"
            f"Статус: <b>{html(access['status_label'])}</b>\n"
            f"План: <code>{html(access['plan'])}</code>\n"
            f"Кредитов за период: <b>{access['used_period']}/{format_limit(access['current_limit'])}</b>\n"
            f"Купленные/ручные кредиты: <b>{int(profile.get('purchased_credits') or 0)}</b>\n"
            f"Всего списано: <b>{access['used_total']}</b>\n"
            f"Подписка до: <code>{html(access['subscription_until'] or '—')}</code>\n"
            f"Заметка: {html(access['admin_note'] or '—')}",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    @router.message(Command("grant"))
    async def grant_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=4)
        if len(parts) < 3:
            await message.answer(
                "Формат: <code>/grant &lt;id&gt; &lt;days&gt; [monthly_limit] [note]</code>",
                parse_mode=TELEGRAM_PARSE_MODE,
            )
            return
        try:
            telegram_id = int(parts[1])
            days = int(parts[2])
            monthly_limit: int | None = None
            note: str | None = None
            if len(parts) >= 4:
                try:
                    monthly_limit = int(parts[3])
                    note = parts[4] if len(parts) >= 5 else None
                except ValueError:
                    note = " ".join(parts[3:])
        except ValueError:
            await message.answer("ID, days и monthly_limit должны быть числами.")
            return
        await db.set_subscription(telegram_id, message.from_user.id, days, monthly_limit, note)
        await message.answer(f"Подписка выдана пользователю <code>{telegram_id}</code> на {days} дней.", parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("unlimited"))
    async def unlimited_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Формат: <code>/unlimited &lt;id&gt; [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
        except ValueError:
            await message.answer("Telegram id должен быть числом.")
            return
        await db.set_unlimited_access(telegram_id, message.from_user.id, True, parts[2] if len(parts) > 2 else None)
        await message.answer(f"Unlimited-доступ выдан пользователю <code>{telegram_id}</code>.", parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("revoke"))
    async def revoke_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Формат: <code>/revoke &lt;id&gt; [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
        except ValueError:
            await message.answer("Telegram id должен быть числом.")
            return
        await db.revoke_paid_access(telegram_id, message.from_user.id, parts[2] if len(parts) > 2 else None)
        await message.answer(f"Платный доступ отозван у пользователя <code>{telegram_id}</code>.", parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("free_limit"))
    async def free_limit_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=3)
        if len(parts) < 3:
            await message.answer("Формат: <code>/free_limit &lt;id&gt; &lt;count&gt; [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
            free_limit = max(0, int(parts[2]))
        except ValueError:
            await message.answer("ID и count должны быть числами.")
            return
        await db.set_free_limit(telegram_id, message.from_user.id, free_limit, parts[3] if len(parts) > 3 else None)
        await message.answer(f"Free-кредиты пользователя <code>{telegram_id}</code> изменен на {free_limit}.", parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("block"))
    async def block_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Формат: <code>/block &lt;id&gt; [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
        except ValueError:
            await message.answer("Telegram id должен быть числом.")
            return
        await db.set_blocked(telegram_id, message.from_user.id, True, parts[2] if len(parts) > 2 else None)
        await message.answer(f"Пользователь <code>{telegram_id}</code> заблокирован.", parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("unblock"))
    async def unblock_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Формат: <code>/unblock &lt;id&gt; [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
        except ValueError:
            await message.answer("Telegram id должен быть числом.")
            return
        await db.set_blocked(telegram_id, message.from_user.id, False, parts[2] if len(parts) > 2 else None)
        await message.answer(f"Пользователь <code>{telegram_id}</code> разблокирован.", parse_mode=TELEGRAM_PARSE_MODE)


    @router.message(Command("addcredits"))
    async def addcredits_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=3)
        if len(parts) < 3:
            await message.answer("Формат: <code>/addcredits &lt;id&gt; &lt;amount&gt; [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
            amount = max(1, int(parts[2]))
        except ValueError:
            await message.answer("ID и amount должны быть числами.")
            return
        result = await db.adjust_purchased_credits(telegram_id, message.from_user.id, amount, parts[3] if len(parts) > 3 else None)
        await message.answer(
            f"Кредиты начислены ✅\nПользователь: <code>{telegram_id}</code>\n"
            f"Начислено: <b>{result['delta']}</b>\nБаланс ручных кредитов: <b>{result['purchased_credits']}</b>",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    @router.message(Command("takecredits"))
    async def takecredits_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=3)
        if len(parts) < 3:
            await message.answer("Формат: <code>/takecredits &lt;id&gt; &lt;amount&gt; [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
            amount = max(1, int(parts[2]))
        except ValueError:
            await message.answer("ID и amount должны быть числами.")
            return
        result = await db.adjust_purchased_credits(telegram_id, message.from_user.id, -amount, parts[3] if len(parts) > 3 else None)
        await message.answer(
            f"Кредиты списаны ✅\nПользователь: <code>{telegram_id}</code>\n"
            f"Изменение: <b>{result['delta']}</b>\nБаланс ручных кредитов: <b>{result['purchased_credits']}</b>",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    @router.message(Command("credits"))
    async def credits_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Формат: <code>/credits &lt;id&gt; [limit]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
            limit = max(1, min(int(parts[2]) if len(parts) > 2 else 10, 30))
        except ValueError:
            await message.answer("ID и limit должны быть числами.")
            return
        rows = await db.list_credit_transactions(telegram_id, limit)
        if not rows:
            await message.answer("Операций по кредитам нет.")
            return
        lines = [f"<b>Кредиты пользователя <code>{telegram_id}</code></b>"]
        for r in rows:
            lines.append(f"{html(r['created_at'])} — <code>{html(r['transaction_type'])}</code> — {r['amount']} — {html(r.get('reason') or '')}")
        await message.answer("\n".join(lines), parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("setplan"))
    async def setplan_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=4)
        if len(parts) < 3:
            await message.answer("Формат: <code>/setplan &lt;id&gt; &lt;free|go|plus|pro|business&gt; [days] [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
        except ValueError:
            await message.answer("Telegram id должен быть числом.")
            return
        plan_key = str(parts[2]).strip().lower()
        if plan_key == "free":
            note = parts[4] if len(parts) > 4 else (parts[3] if len(parts) > 3 else "admin setplan free")
            await db.revoke_paid_access(telegram_id, message.from_user.id, note)
            await message.answer(f"Пользователь <code>{telegram_id}</code> переведён на Free.", parse_mode=TELEGRAM_PARSE_MODE)
            return
        plans = plan_catalog(settings)
        plan = plans.get(plan_key)
        if not plan:
            await message.answer("Тариф не найден. Доступно: <code>free, go, plus, pro, business</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        days = 30
        note = None
        if len(parts) >= 4:
            try:
                days = max(1, int(parts[3]))
                note = parts[4] if len(parts) >= 5 else None
            except ValueError:
                note = " ".join(parts[3:])
        order_id = f"admin_{message.from_user.id}_{telegram_id}_{message.message_id}"
        result = await db.activate_paid_subscription(telegram_id, plan.key, "admin", order_id, plan.daily_limit, plan.monthly_limit, days=days)
        await db.record_access_event(telegram_id, message.from_user.id, "plan_set_by_admin", {"plan": plan.key, "days": days, "note": note, "order_id": order_id})
        await message.answer(
            f"Тариф выдан ✅\nПользователь: <code>{telegram_id}</code>\n"
            f"Тариф: <b>{html(plan.title)}</b>\nДо: <code>{html(result['expires_at'])}</code>",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    @router.message(Command("orders"))
    async def orders_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=2)
        try:
            limit = max(1, min(int(parts[1]) if len(parts) > 1 else 10, 30))
        except ValueError:
            limit = 10
        status = parts[2].strip().lower() if len(parts) > 2 else None
        rows = await db.list_billing_orders(limit=limit, status=status)
        if not rows:
            await message.answer("Заказов не найдено.")
            return
        lines = ["<b>Заказы</b>"]
        for r in rows:
            lines.append(f"<code>{html(r['id'])}</code> — user <code>{html(r['telegram_user_id'])}</code> — {html(r['plan'])} — {html(r['provider'])} — {html(r['status'])} — {r['amount']} {html(r['currency'])}")
        await message.answer("\n".join(lines), parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("payments"))
    async def payments_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=1)
        try:
            limit = max(1, min(int(parts[1]) if len(parts) > 1 else 10, 30))
        except ValueError:
            limit = 10
        rows = await db.list_payments(limit=limit)
        if not rows:
            await message.answer("Платежей пока нет.")
            return
        lines = ["<b>Платежи</b>"]
        for r in rows:
            lines.append(f"#{r['id']} — user <code>{html(r['telegram_user_id'])}</code> — {html(r.get('plan') or '')} — {html(r.get('provider') or '')} — {html(r.get('status') or '')} — {r.get('amount')} {html(r.get('currency') or '')}")
        await message.answer("\n".join(lines), parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("errors"))
    async def errors_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=1)
        try:
            limit = max(1, min(int(parts[1]) if len(parts) > 1 else 10, 20))
        except ValueError:
            limit = 10
        rows = await db.list_error_logs(limit=limit)
        if not rows:
            await message.answer("Ошибок нет.")
            return
        lines = ["<b>Последние ошибки</b>"]
        for r in rows:
            err = str(r.get('error_text') or '')[:220]
            lines.append(f"#{r['id']} — {html(r['created_at'])} — <code>{html(r['source'])}</code> — {html(err)}")
        await message.answer("\n".join(lines), parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("admin_stats"))
    async def admin_stats_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        stats = await db.admin_stats()
        await message.answer(
            "<b>Сводка проекта</b>\n"
            f"Пользователей: <b>{stats.get('users_total', 0)}</b>\n"
            f"Активных сегодня: <b>{stats.get('active_users_today', 0)}</b>\n"
            f"Запросов сегодня: <b>{stats.get('requests_today', 0)}</b>\n"
            f"Списано кредитов сегодня: <b>{stats.get('credits_charged_today', 0)}</b>\n"
            f"Платежей сегодня: <b>{stats.get('payments_today', 0)}</b>\n"
            f"Выручка RUB всего: <b>{stats.get('revenue_rub_total', 0)}</b>\n"
            f"Активных подписок: <b>{stats.get('active_subscriptions', 0)}</b>\n"
            f"Pending orders: <b>{stats.get('pending_orders', 0)}</b>\n"
            f"Ошибок сегодня: <b>{stats.get('errors_today', 0)}</b>",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    @router.message(Command("user_history"))
    async def user_history_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Формат: <code>/user_history &lt;id&gt; [limit]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
            limit = max(1, min(int(parts[2]) if len(parts) > 2 else 10, 20))
        except ValueError:
            await message.answer("ID и limit должны быть числами.")
            return
        rows = await db.list_conversations(telegram_id, limit=limit)
        if not rows:
            await message.answer("Диалогов нет.")
            return
        lines = [f"<b>Диалоги пользователя <code>{telegram_id}</code></b>"]
        for r in rows:
            lines.append(f"<code>{html(r['id'])}</code> — {html(r.get('title') or 'Диалог')} — {r.get('messages_count') or 0} сообщений — {html(r.get('updated_at') or '')}")
        await message.answer("\n".join(lines), parse_mode=TELEGRAM_PARSE_MODE)

    @router.message(Command("clear_history"))
    async def clear_history_command(message: Message) -> None:
        if await deny_non_admin(message):
            return
        parts = (message.text or "").split(maxsplit=2)
        if len(parts) < 2:
            await message.answer("Формат: <code>/clear_history &lt;id&gt; [note]</code>", parse_mode=TELEGRAM_PARSE_MODE)
            return
        try:
            telegram_id = int(parts[1])
        except ValueError:
            await message.answer("Telegram id должен быть числом.")
            return
        result = await db.reset_user_history(telegram_id, message.from_user.id, parts[2] if len(parts) > 2 else None)
        await message.answer(f"История архивирована ✅\nПользователь: <code>{telegram_id}</code>\nДиалогов: <b>{result['archived']}</b>", parse_mode=TELEGRAM_PARSE_MODE)

    @router.callback_query(F.data == "help")
    async def help_callback(callback) -> None:  # type: ignore[no-untyped-def]
        await callback.answer()
        await callback.message.answer(
            "<b>Шаблон управленческого запроса</b>\n\n"
            "<pre>Ниша: B2B-сервис для малого бизнеса\n"
            "Клиент: собственники компаний 5–50 сотрудников\n"
            "Продукт: подписка на автоматизацию заявок\n"
            "Цена: 49€ в месяц\n"
            "Цель: получить первые 20 платящих клиентов\n"
            "Ограничения: бюджет 500€, команда 2 человека</pre>\n\n"
            "<b>Чем точнее вводные, тем выше качество плана:</b> сегменты, экономика, текущие метрики, сроки и доступные ресурсы.",
            parse_mode=TELEGRAM_PARSE_MODE,
        )

    @router.message(F.text & F.reply_to_message)
    async def support_group_reply(message: Message) -> None:
        """Bridge support group replies back into the Mini App support chat.

        Flow: Mini App -> bot posts a ticket to support group -> support agent replies
        to the bot message -> this handler stores the answer in SQLite. The user sees
        it through /api/support/tickets/{id}; we also try to notify them in Telegram.
        """
        if not settings.support_group_chat_id or str(message.chat.id) != str(settings.support_group_chat_id):
            return
        if not message.text or not message.reply_to_message:
            return
        replied_id = int(message.reply_to_message.message_id)
        ticket = await support_store.find_support_ticket_by_group_message(message.chat.id, replied_id)
        if not ticket:
            # Fallback for copied/forwarded bot messages: parse sup_xxx from the text.
            source_text = message.reply_to_message.text or message.reply_to_message.caption or ""
            match = re.search(r"sup_[0-9a-fA-F]{8,32}", source_text)
            if match:
                ticket = await support_store.get_support_ticket(match.group(0))
        if not ticket:
            await message.reply("Не нашёл тикет для этого reply. Ответьте на исходное сообщение бота с ID тикета sup_...")
            return
        author_name = " ".join(part for part in [getattr(message.from_user, "first_name", None), getattr(message.from_user, "last_name", None)] if part).strip()
        if not author_name and message.from_user and message.from_user.username:
            author_name = f"@{message.from_user.username}"
        saved = await support_store.add_support_message(
            ticket["id"],
            author_type="support",
            author_telegram_id=message.from_user.id if message.from_user else None,
            author_name=author_name or settings.support_public_name,
            content=message.text,
            source="telegram_group",
            status="answered",
        )
        await support_store.update_support_ticket_bridge(ticket["id"], message.chat.id, message.message_id)
        try:
            user_id_for_notification = int(ticket.get("telegram_user_id") or 0)
            if user_id_for_notification:
                await support_store.create_notification(
                    user_id_for_notification,
                    title="Поддержка ответила",
                    body=message.text[:500],
                    type="support",
                    action_url="profile:support",
                    metadata={"ticket_id": ticket["id"], "support_message_id": saved.get("id")},
                )
        except Exception:  # noqa: BLE001
            pass
        # Best-effort notification to the user. The Mini App remains the source of truth.
        try:
            user_id = int(ticket.get("telegram_user_id") or 0)
            if user_id:
                await message.bot.send_message(
                    user_id,
                    "<b>Поддержка ответила</b>\n\n"
                    f"Тикет: <code>{html(ticket['id'])}</code>\n"
                    f"{html(message.text[:1200])}\n\n"
                    "Откройте Mini App → Профиль → Поддержка, чтобы продолжить диалог.",
                    parse_mode=TELEGRAM_PARSE_MODE,
                    reply_markup=build_main_keyboard(settings),
                )
        except Exception:  # noqa: BLE001
            pass
        await message.reply(f"Ответ доставлен пользователю ✅\nТикет: {ticket['id']}")

    @router.message(F.text)
    async def text_ai(message: Message) -> None:
        if getattr(message.chat, "type", "private") != "private":
            return
        if not message.from_user or not message.text:
            return

        user = message.from_user
        await db.upsert_user(user.id, user.username, user.first_name, user.last_name)

        estimate = estimate_credits("strategy", message.text, model=settings.openrouter_model)
        try:
            await rate_limiter.check(user.id, estimate.credits)
            await db.reserve_credits(
                user.id,
                estimate.request_id,
                estimate.tool_id,
                estimate.credits,
                free_limit_default=settings.free_trial_requests,
                monthly_limit_default=settings.subscriber_monthly_limit,
                metadata={"source": "telegram_bot", "reason": estimate.reason},
            )
        except RateLimitError as exc:
            await message.answer(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            await message.answer(str(exc))
            return

        status = await message.answer("Запрос принят. Готовлю структурированный разбор: выводы, риски и следующие шаги.")
        try:
            answer = await ai_client.ask_business_ai("strategy", message.text)
            await db.finalize_credit_charge(
                user.id,
                estimate.request_id,
                estimate.tool_id,
                estimate.credits,
                estimate.credits,
                model=settings.openrouter_model,
                input_tokens=estimate.input_tokens_estimated,
                output_tokens=estimate_output_tokens(answer),
            )
            await db.save_request(user.id, "strategy", message.text, answer)
        except AIClientError as exc:
            await db.refund_reserved_credits(user.id, estimate.request_id, str(exc), tool_id=estimate.tool_id, estimated_credits=estimate.credits, model=settings.openrouter_model)
            await status.edit_text(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            await db.refund_reserved_credits(user.id, estimate.request_id, str(exc), tool_id=estimate.tool_id, estimated_credits=estimate.credits, model=settings.openrouter_model)
            await status.edit_text(f"Непредвиденная ошибка: {exc}")
            return

        chunks = split_for_telegram(answer)
        await status.edit_text(chunks[0])
        for chunk in chunks[1:]:
            await message.answer(chunk)

    dp = Dispatcher()
    dp.include_router(router)
    return dp
