from __future__ import annotations

from html import escape

from aiogram import Dispatcher, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, PreCheckoutQuery, WebAppInfo

from app.billing import activate_subscription, plan_catalog
from app.config import Settings
from app.db import Database
from app.openrouter_client import AIClientError, OpenRouterClient
from app.rate_limit import RateLimitError, RateLimiter


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

    @router.pre_checkout_query()
    async def pre_checkout(query: PreCheckoutQuery) -> None:
        payload = query.invoice_payload or ""
        order = await db.get_billing_order(payload) if payload.startswith("ord_") else None
        if not order or order.get("status") not in {"pending", "failed"}:
            await query.answer(ok=False, error_message="Заказ не найден или уже обработан.")
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
        result = await activate_subscription(
            db,
            message.from_user.id,
            plan.key,
            "telegram_stars",
            order_id,
            plan.daily_limit,
        )
        await db.record_payment(
            order_id=order_id,
            telegram_id=message.from_user.id,
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
            f"Лимит: <b>{plan.daily_limit}</b> запросов в день.\n"
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
            f"Использовано сегодня: <b>{access['used_today']}</b>\n"
            f"Использовано всего/за период: <b>{access['used_period']}/{format_limit(access['current_limit'])}</b>\n"
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
            "<code>/grant &lt;id&gt; &lt;days&gt; [monthly_limit] [note]</code> — выдать подписку\n"
            "<code>/unlimited &lt;id&gt; [note]</code> — выдать unlimited\n"
            "<code>/revoke &lt;id&gt; [note]</code> — вернуть на Free\n"
            "<code>/free_limit &lt;id&gt; &lt;count&gt; [note]</code> — изменить trial\n"
            "<code>/block &lt;id&gt; [note]</code> — отключить доступ\n"
            "<code>/unblock &lt;id&gt; [note]</code> — разблокировать",
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
            lines.append(f"<code>{item['telegram_id']}</code> — {title} — {plan} — {total} запросов")
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
            f"Использовано: <b>{access['used_period']}/{format_limit(access['current_limit'])}</b>\n"
            f"Всего запросов: <b>{access['used_total']}</b>\n"
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
        await message.answer(f"Trial-лимит пользователя <code>{telegram_id}</code> изменен на {free_limit}.", parse_mode=TELEGRAM_PARSE_MODE)

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

    @router.message(F.text)
    async def text_ai(message: Message) -> None:
        if not message.from_user or not message.text:
            return

        user = message.from_user
        await db.upsert_user(user.id, user.username, user.first_name, user.last_name)

        try:
            await rate_limiter.check(user.id)
        except RateLimitError as exc:
            await message.answer(str(exc))
            return

        status = await message.answer("Запрос принят. Готовлю структурированный разбор: выводы, риски и следующие шаги.")
        try:
            answer = await ai_client.ask_business_ai("strategy", message.text)
            await db.save_request(user.id, "strategy", message.text, answer)
        except AIClientError as exc:
            await status.edit_text(str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            await status.edit_text(f"Непредвиденная ошибка: {exc}")
            return

        chunks = split_for_telegram(answer)
        await status.edit_text(chunks[0])
        for chunk in chunks[1:]:
            await message.answer(chunk)

    dp = Dispatcher()
    dp.include_router(router)
    return dp
