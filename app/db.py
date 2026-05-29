from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from . import db_adapter as aiosqlite


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT UNIQUE NOT NULL,
    telegram_id BIGINT UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT,
    photo_url TEXT,
    plan TEXT DEFAULT 'free',
    daily_limit INTEGER DEFAULT 20,
    bonus_requests INTEGER DEFAULT 0,
    purchased_credits INTEGER DEFAULT 0,
    referral_code TEXT UNIQUE,
    referred_by TEXT,
    onboarding_completed INTEGER DEFAULT 0,
    free_limit INTEGER NOT NULL DEFAULT 15,
    monthly_limit INTEGER,
    subscription_started_at TEXT,
    subscription_until TEXT,
    unlimited_access INTEGER NOT NULL DEFAULT 0,
    blocked INTEGER NOT NULL DEFAULT 0,
    admin_note TEXT,
    access_updated_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_seen_at TEXT,
    login_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS ai_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT NOT NULL,
    mode TEXT NOT NULL,
    user_text TEXT NOT NULL,
    ai_answer TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS access_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id BIGINT NOT NULL,
    admin_id BIGINT,
    action TEXT NOT NULL,
    details TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    telegram_user_id TEXT NOT NULL,
    title TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    is_archived INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    model TEXT,
    tokens_used INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tool_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    input_json TEXT NOT NULL,
    result_text TEXT,
    model TEXT,
    tokens_used INTEGER DEFAULT 0,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost_estimate REAL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS saved_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    source_type TEXT,
    source_id TEXT,
    rating INTEGER NOT NULL,
    message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS business_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT UNIQUE NOT NULL,
    user_type TEXT,
    main_goal TEXT,
    business_name TEXT,
    niche TEXT,
    marketplace TEXT,
    target_audience TEXT,
    average_price TEXT,
    description TEXT,
    main_problem TEXT,
    inn TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_telegram_user_id TEXT NOT NULL,
    invited_telegram_user_id TEXT NOT NULL,
    bonus_given INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    plan TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT,
    expires_at TEXT,
    daily_limit INTEGER,
    monthly_limit INTEGER,
    provider TEXT,
    order_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    telegram_user_id TEXT NOT NULL,
    provider TEXT,
    plan TEXT,
    amount REAL,
    currency TEXT,
    status TEXT,
    external_payment_id TEXT,
    external_charge_id TEXT,
    payload TEXT,
    raw_event_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS billing_orders (
    id TEXT PRIMARY KEY,
    telegram_user_id TEXT NOT NULL,
    plan TEXT NOT NULL,
    provider TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    payment_url TEXT,
    external_payment_id TEXT,
    payload TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT
);

CREATE TABLE IF NOT EXISTS payment_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    event_type TEXT,
    order_id TEXT,
    external_payment_id TEXT,
    raw_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS payout_methods (
    telegram_user_id TEXT PRIMARY KEY,
    bik TEXT NOT NULL,
    bank_name TEXT,
    account_number_encrypted TEXT,
    account_last4 TEXT,
    account_mask TEXT,
    holder_name TEXT,
    status TEXT NOT NULL DEFAULT 'saved',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS autopay_settings (
    telegram_user_id TEXT PRIMARY KEY,
    enabled INTEGER NOT NULL DEFAULT 0,
    provider TEXT NOT NULL DEFAULT 'yookassa',
    plan TEXT,
    payment_method_id_encrypted TEXT,
    payment_method_mask TEXT,
    status TEXT NOT NULL DEFAULT 'disabled',
    consent_at TEXT,
    last_charge_at TEXT,
    next_charge_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT,
    source TEXT NOT NULL,
    error_text TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS credit_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    request_id TEXT,
    transaction_type TEXT NOT NULL,
    amount INTEGER NOT NULL,
    balance_after INTEGER,
    reason TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ai_usage_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    tool_id TEXT,
    model TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    credits_estimated INTEGER DEFAULT 0,
    credits_charged INTEGER DEFAULT 0,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS active_ai_requests (
    request_id TEXT PRIMARY KEY,
    telegram_user_id TEXT NOT NULL,
    tool_id TEXT,
    reserved_credits INTEGER NOT NULL,
    started_at TEXT NOT NULL
);
"""


INDEXES = """
CREATE INDEX IF NOT EXISTS idx_ai_requests_user_created
ON ai_requests(telegram_id, created_at);

CREATE INDEX IF NOT EXISTS idx_access_events_user_created
ON access_events(telegram_id, created_at);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_id
ON users(telegram_id);

CREATE INDEX IF NOT EXISTS idx_users_telegram_user_id
ON users(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id
ON chat_messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_created
ON chat_messages(conversation_id, created_at);

CREATE INDEX IF NOT EXISTS idx_tool_runs_telegram_user_id
ON tool_runs(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_usage_logs_telegram_user_id_created_at
ON usage_logs(telegram_user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_saved_results_telegram_user_id
ON saved_results(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_conversations_telegram_user_id
ON conversations(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_conversations_user_updated
ON conversations(telegram_user_id, updated_at);

CREATE INDEX IF NOT EXISTS idx_feedback_telegram_user_id
ON feedback(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer
ON referrals(referrer_telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_error_logs_created_at
ON error_logs(created_at);

CREATE INDEX IF NOT EXISTS idx_billing_orders_user
ON billing_orders(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_billing_orders_status
ON billing_orders(status);

CREATE INDEX IF NOT EXISTS idx_billing_orders_provider
ON billing_orders(provider);

CREATE INDEX IF NOT EXISTS idx_billing_orders_external_payment_id
ON billing_orders(external_payment_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_user
ON subscriptions(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_status
ON subscriptions(status);

CREATE INDEX IF NOT EXISTS idx_payments_user
ON payments(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_payments_order
ON payments(order_id);

CREATE INDEX IF NOT EXISTS idx_payment_events_order
ON payment_events(order_id);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_created
ON credit_transactions(telegram_user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_request_id
ON credit_transactions(request_id);

CREATE INDEX IF NOT EXISTS idx_ai_usage_events_user_created
ON ai_usage_events(telegram_user_id, created_at);

CREATE INDEX IF NOT EXISTS idx_active_ai_requests_user
ON active_ai_requests(telegram_user_id);

CREATE INDEX IF NOT EXISTS idx_autopay_enabled_next
ON autopay_settings(enabled, next_charge_at);

"""


USER_ADD_COLUMNS = {
    "telegram_id": "ALTER TABLE users ADD COLUMN telegram_id BIGINT",
    "username": "ALTER TABLE users ADD COLUMN username TEXT",
    "first_name": "ALTER TABLE users ADD COLUMN first_name TEXT",
    "last_name": "ALTER TABLE users ADD COLUMN last_name TEXT",
    "language_code": "ALTER TABLE users ADD COLUMN language_code TEXT",
    "photo_url": "ALTER TABLE users ADD COLUMN photo_url TEXT",
    "plan": "ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free'",
    "daily_limit": "ALTER TABLE users ADD COLUMN daily_limit INTEGER DEFAULT 20",
    "bonus_requests": "ALTER TABLE users ADD COLUMN bonus_requests INTEGER DEFAULT 0",
    "purchased_credits": "ALTER TABLE users ADD COLUMN purchased_credits INTEGER DEFAULT 0",
    "referral_code": "ALTER TABLE users ADD COLUMN referral_code TEXT",
    "referred_by": "ALTER TABLE users ADD COLUMN referred_by TEXT",
    "onboarding_completed": "ALTER TABLE users ADD COLUMN onboarding_completed INTEGER DEFAULT 0",
    "free_limit": "ALTER TABLE users ADD COLUMN free_limit INTEGER NOT NULL DEFAULT 15",
    "monthly_limit": "ALTER TABLE users ADD COLUMN monthly_limit INTEGER",
    "subscription_started_at": "ALTER TABLE users ADD COLUMN subscription_started_at TEXT",
    "subscription_until": "ALTER TABLE users ADD COLUMN subscription_until TEXT",
    "subscription_expires_at": "ALTER TABLE users ADD COLUMN subscription_expires_at TEXT",
    "unlimited_access": "ALTER TABLE users ADD COLUMN unlimited_access INTEGER NOT NULL DEFAULT 0",
    "blocked": "ALTER TABLE users ADD COLUMN blocked INTEGER NOT NULL DEFAULT 0",
    "admin_note": "ALTER TABLE users ADD COLUMN admin_note TEXT",
    "access_updated_at": "ALTER TABLE users ADD COLUMN access_updated_at TEXT",
    "updated_at": "ALTER TABLE users ADD COLUMN updated_at TEXT",
    "last_seen_at": "ALTER TABLE users ADD COLUMN last_seen_at TEXT",
    "login_count": "ALTER TABLE users ADD COLUMN login_count INTEGER NOT NULL DEFAULT 0",
}

BUSINESS_PROFILE_ADD_COLUMNS = {
    "user_type": "ALTER TABLE business_profiles ADD COLUMN user_type TEXT",
    "main_goal": "ALTER TABLE business_profiles ADD COLUMN main_goal TEXT",
    "business_name": "ALTER TABLE business_profiles ADD COLUMN business_name TEXT",
    "niche": "ALTER TABLE business_profiles ADD COLUMN niche TEXT",
    "marketplace": "ALTER TABLE business_profiles ADD COLUMN marketplace TEXT",
    "target_audience": "ALTER TABLE business_profiles ADD COLUMN target_audience TEXT",
    "average_price": "ALTER TABLE business_profiles ADD COLUMN average_price TEXT",
    "description": "ALTER TABLE business_profiles ADD COLUMN description TEXT",
    "main_problem": "ALTER TABLE business_profiles ADD COLUMN main_problem TEXT",
    "inn": "ALTER TABLE business_profiles ADD COLUMN inn TEXT",
    "updated_at": "ALTER TABLE business_profiles ADD COLUMN updated_at TEXT",
}

FEEDBACK_ADD_COLUMNS = {
    "source_type": "ALTER TABLE feedback ADD COLUMN source_type TEXT",
    "source_id": "ALTER TABLE feedback ADD COLUMN source_id TEXT",
}

USER_BILLING_ADD_COLUMNS = {
    "subscription_expires_at": "ALTER TABLE users ADD COLUMN subscription_expires_at TEXT",
}

SUBSCRIPTION_ADD_COLUMNS = {
    "provider": "ALTER TABLE subscriptions ADD COLUMN provider TEXT",
    "order_id": "ALTER TABLE subscriptions ADD COLUMN order_id TEXT",
    "updated_at": "ALTER TABLE subscriptions ADD COLUMN updated_at TEXT",
}

PAYMENT_ADD_COLUMNS = {
    "order_id": "ALTER TABLE payments ADD COLUMN order_id TEXT",
    "plan": "ALTER TABLE payments ADD COLUMN plan TEXT",
    "external_charge_id": "ALTER TABLE payments ADD COLUMN external_charge_id TEXT",
    "payload": "ALTER TABLE payments ADD COLUMN payload TEXT",
    "raw_event_json": "ALTER TABLE payments ADD COLUMN raw_event_json TEXT",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def tg_text_id(telegram_id: int | str) -> str:
    return str(telegram_id)


def referral_code_for(telegram_id: int | str) -> str:
    return f"fp{telegram_id}"


class CreditLimitError(RuntimeError):
    pass


class Database:
    def __init__(self, path: str) -> None:
        self.path = path

    async def init(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA foreign_keys=OFF")
            await db.executescript(SCHEMA)
            await self._migrate_postgres_bigint_columns(db)
            await self._migrate_users_table(db)
            await self._migrate_conversations_table(db)
            await self._migrate_chat_messages_table(db)
            await self._migrate_simple_add_columns(db, "business_profiles", BUSINESS_PROFILE_ADD_COLUMNS)
            await self._migrate_simple_add_columns(db, "feedback", FEEDBACK_ADD_COLUMNS)
            await self._migrate_simple_add_columns(db, "users", USER_BILLING_ADD_COLUMNS)
            await self._migrate_simple_add_columns(db, "subscriptions", SUBSCRIPTION_ADD_COLUMNS)
            await self._migrate_simple_add_columns(db, "payments", PAYMENT_ADD_COLUMNS)
            await self._migrate_payout_tables(db)
            await db.executescript(INDEXES)
            await db.commit()
            await db.execute("PRAGMA foreign_keys=ON")

    async def _migrate_postgres_bigint_columns(self, db: aiosqlite.Connection) -> None:
        """Keep Telegram ids safe after moving from SQLite to PostgreSQL.

        Telegram user identifiers are already larger than signed int32 for many
        accounts. PostgreSQL INTEGER is int32, so /api/me can crash before the
        user is even created. SQLite tolerated this silently; production
        PostgreSQL must use BIGINT for every numeric Telegram id column.
        """
        if not aiosqlite.is_postgres_dsn(self.path):
            return
        statements = [
            # Existing deployments may already have FK constraints created with
            # int4 columns. Drop them before widening the columns. The app still
            # keeps logical integrity through telegram_user_id and service code.
            "ALTER TABLE IF EXISTS ai_requests DROP CONSTRAINT IF EXISTS ai_requests_telegram_id_fkey",
            "ALTER TABLE IF EXISTS access_events DROP CONSTRAINT IF EXISTS access_events_telegram_id_fkey",
            "ALTER TABLE IF EXISTS users ALTER COLUMN telegram_id TYPE BIGINT USING telegram_id::BIGINT",
            "ALTER TABLE IF EXISTS ai_requests ALTER COLUMN telegram_id TYPE BIGINT USING telegram_id::BIGINT",
            "ALTER TABLE IF EXISTS access_events ALTER COLUMN telegram_id TYPE BIGINT USING telegram_id::BIGINT",
            "ALTER TABLE IF EXISTS access_events ALTER COLUMN admin_id TYPE BIGINT USING admin_id::BIGINT",
        ]
        for statement in statements:
            try:
                await db.execute(statement)
            except Exception:
                # Do not block startup for legacy tables that are absent in tests
                # or for already-correct schemas. The next explicit query will
                # surface a real DB problem if one remains.
                pass

    async def _table_columns(self, db: aiosqlite.Connection, table: str) -> dict[str, Any]:
        cursor = await db.execute(f"PRAGMA table_info({table})")
        rows = await cursor.fetchall()
        return {str(row[1]): row for row in rows}

    def _coalesce_existing(self, columns: dict[str, Any], candidates: list[str], fallback: str) -> str:
        existing = [candidate for candidate in candidates if candidate in columns]
        if not existing:
            return fallback
        return f"COALESCE({', '.join(existing)}, {fallback})"

    async def _migrate_simple_add_columns(
        self,
        db: aiosqlite.Connection,
        table: str,
        migrations: dict[str, str],
    ) -> None:
        columns = await self._table_columns(db, table)
        for column, sql in migrations.items():
            if column not in columns:
                await db.execute(sql)

    async def _migrate_users_table(self, db: aiosqlite.Connection) -> None:
        columns = await self._table_columns(db, "users")
        needs_rebuild = "id" not in columns or "telegram_user_id" not in columns
        if needs_rebuild:
            await db.execute("DROP TABLE IF EXISTS users_new")
            await db.execute(
                """
                CREATE TABLE users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_user_id TEXT UNIQUE NOT NULL,
                    telegram_id BIGINT UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    photo_url TEXT,
                    plan TEXT DEFAULT 'free',
                    daily_limit INTEGER DEFAULT 20,
                    bonus_requests INTEGER DEFAULT 0,
                    purchased_credits INTEGER DEFAULT 0,
                    referral_code TEXT UNIQUE,
                    referred_by TEXT,
                    onboarding_completed INTEGER DEFAULT 0,
                    free_limit INTEGER NOT NULL DEFAULT 15,
                    monthly_limit INTEGER,
                    subscription_started_at TEXT,
                    subscription_until TEXT,
                    subscription_expires_at TEXT,
                    unlimited_access INTEGER NOT NULL DEFAULT 0,
                    blocked INTEGER NOT NULL DEFAULT 0,
                    admin_note TEXT,
                    access_updated_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_seen_at TEXT,
                    login_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )

            telegram_user_parts: list[str] = []
            if "telegram_user_id" in columns:
                telegram_user_parts.append("NULLIF(CAST(telegram_user_id AS TEXT), '')")
            if "telegram_id" in columns:
                telegram_user_parts.append("NULLIF(CAST(telegram_id AS TEXT), '')")
            if "id" in columns:
                telegram_user_parts.append("NULLIF(CAST(id AS TEXT), '')")
            telegram_user_expr = f"COALESCE({', '.join(telegram_user_parts)}, lower(hex(randomblob(8))))"

            telegram_id_expr = "NULL"
            if "telegram_id" in columns:
                telegram_id_expr = "telegram_id"
            elif "telegram_user_id" in columns:
                telegram_id_expr = "CAST(telegram_user_id AS INTEGER)"

            def expr(name: str, fallback: str = "NULL") -> str:
                return name if name in columns else fallback

            now = utc_now_iso()
            await db.execute(
                f"""
                INSERT OR IGNORE INTO users_new (
                    telegram_user_id, telegram_id, username, first_name, last_name, language_code, photo_url,
                    plan, daily_limit, bonus_requests, purchased_credits, referral_code, referred_by, onboarding_completed,
                    free_limit, monthly_limit, subscription_started_at,
                    subscription_until, subscription_expires_at, unlimited_access, blocked, admin_note, access_updated_at,
                    created_at, updated_at, last_seen_at, login_count
                )
                SELECT
                    {telegram_user_expr},
                    {telegram_id_expr},
                    {expr("username")},
                    {expr("first_name")},
                    {expr("last_name")},
                    {expr("language_code")},
                    {expr("photo_url")},
                    {expr("plan", "'free'")},
                    {expr("daily_limit", "20")},
                    {expr("bonus_requests", "0")},
                    {expr("purchased_credits", "0")},
                    {expr("referral_code")},
                    {expr("referred_by")},
                    {expr("onboarding_completed", "0")},
                    {expr("free_limit", "15")},
                    {expr("monthly_limit")},
                    {expr("subscription_started_at")},
                    {expr("subscription_until")},
                    {expr("subscription_expires_at")},
                    {expr("unlimited_access", "0")},
                    {expr("blocked", "0")},
                    {expr("admin_note")},
                    {expr("access_updated_at")},
                    {expr("created_at", repr(now))},
                    {expr("updated_at", expr("created_at", repr(now)))},
                    {expr("last_seen_at", expr("updated_at", expr("created_at", repr(now))))},
                    {expr("login_count", "0")}
                FROM users
                """
            )
            await db.execute("DROP TABLE users")
            await db.execute("ALTER TABLE users_new RENAME TO users")
            return

        for column, sql in USER_ADD_COLUMNS.items():
            if column not in columns:
                await db.execute(sql)

    async def _migrate_conversations_table(self, db: aiosqlite.Connection) -> None:
        columns = await self._table_columns(db, "conversations")
        id_type = str(columns.get("id", ["", "", ""])[2]).upper() if "id" in columns else ""
        needs_rebuild = id_type != "TEXT" or "is_archived" not in columns
        if not needs_rebuild:
            return

        await db.execute("DROP TABLE IF EXISTS conversations_new")
        await db.execute(
            """
            CREATE TABLE conversations_new (
                id TEXT PRIMARY KEY,
                telegram_user_id TEXT NOT NULL,
                title TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_archived INTEGER DEFAULT 0
            )
            """
        )

        def expr(name: str, fallback: str = "NULL") -> str:
            return name if name in columns else fallback

        id_expr = "CAST(id AS TEXT)" if "id" in columns else "lower(hex(randomblob(16)))"
        telegram_user_expr = "CAST(telegram_user_id AS TEXT)" if "telegram_user_id" in columns else "'0'"
        now = utc_now_iso()
        await db.execute(
            f"""
            INSERT OR IGNORE INTO conversations_new (
                id, telegram_user_id, title, created_at, updated_at, is_archived
            )
            SELECT
                {id_expr},
                {telegram_user_expr},
                {expr("title", "'Новый диалог'")},
                {expr("created_at", repr(now))},
                {expr("updated_at", expr("created_at", repr(now)))},
                {expr("is_archived", "0")}
            FROM conversations
            """
        )
        await db.execute("DROP TABLE conversations")
        await db.execute("ALTER TABLE conversations_new RENAME TO conversations")

    async def _migrate_chat_messages_table(self, db: aiosqlite.Connection) -> None:
        columns = await self._table_columns(db, "chat_messages")
        conversation_id_type = str(columns.get("conversation_id", ["", "", ""])[2]).upper() if "conversation_id" in columns else ""
        needs_rebuild = conversation_id_type != "TEXT" or "model" not in columns or "tokens_used" not in columns
        if not needs_rebuild:
            return

        await db.execute("DROP TABLE IF EXISTS chat_messages_new")
        await db.execute(
            """
            CREATE TABLE chat_messages_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                model TEXT,
                tokens_used INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )

        def expr(name: str, fallback: str = "NULL") -> str:
            return name if name in columns else fallback

        now = utc_now_iso()
        await db.execute(
            f"""
            INSERT OR IGNORE INTO chat_messages_new (
                id, conversation_id, role, content, model, tokens_used, created_at
            )
            SELECT
                {expr("id")},
                CAST({expr("conversation_id", "'0'")} AS TEXT),
                {expr("role", "'user'")},
                {expr("content", "''")},
                {expr("model")},
                {expr("tokens_used", "0")},
                {expr("created_at", repr(now))}
            FROM chat_messages
            """
        )
        await db.execute("DROP TABLE chat_messages")
        await db.execute("ALTER TABLE chat_messages_new RENAME TO chat_messages")

    async def _migrate_payout_tables(self, db: aiosqlite.Connection) -> None:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS payout_methods (
            telegram_user_id TEXT PRIMARY KEY,
            bik TEXT NOT NULL,
            bank_name TEXT,
            account_number_encrypted TEXT,
            account_last4 TEXT,
            account_mask TEXT,
            holder_name TEXT,
            status TEXT NOT NULL DEFAULT 'saved',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS autopay_settings (
            telegram_user_id TEXT PRIMARY KEY,
            enabled INTEGER NOT NULL DEFAULT 0,
            provider TEXT NOT NULL DEFAULT 'yookassa',
            plan TEXT,
            payment_method_id_encrypted TEXT,
            payment_method_mask TEXT,
            status TEXT NOT NULL DEFAULT 'disabled',
            consent_at TEXT,
            last_charge_at TEXT,
            next_charge_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        await self._migrate_simple_add_columns(db, "payout_methods", {
            "bank_name": "ALTER TABLE payout_methods ADD COLUMN bank_name TEXT",
            "account_number_encrypted": "ALTER TABLE payout_methods ADD COLUMN account_number_encrypted TEXT",
            "account_last4": "ALTER TABLE payout_methods ADD COLUMN account_last4 TEXT",
            "account_mask": "ALTER TABLE payout_methods ADD COLUMN account_mask TEXT",
            "holder_name": "ALTER TABLE payout_methods ADD COLUMN holder_name TEXT",
            "status": "ALTER TABLE payout_methods ADD COLUMN status TEXT NOT NULL DEFAULT 'saved'",
            "created_at": "ALTER TABLE payout_methods ADD COLUMN created_at TEXT",
            "updated_at": "ALTER TABLE payout_methods ADD COLUMN updated_at TEXT",
        })
        await self._migrate_simple_add_columns(db, "autopay_settings", {
            "provider": "ALTER TABLE autopay_settings ADD COLUMN provider TEXT NOT NULL DEFAULT 'yookassa'",
            "plan": "ALTER TABLE autopay_settings ADD COLUMN plan TEXT",
            "payment_method_id_encrypted": "ALTER TABLE autopay_settings ADD COLUMN payment_method_id_encrypted TEXT",
            "payment_method_mask": "ALTER TABLE autopay_settings ADD COLUMN payment_method_mask TEXT",
            "status": "ALTER TABLE autopay_settings ADD COLUMN status TEXT NOT NULL DEFAULT 'disabled'",
            "consent_at": "ALTER TABLE autopay_settings ADD COLUMN consent_at TEXT",
            "last_charge_at": "ALTER TABLE autopay_settings ADD COLUMN last_charge_at TEXT",
            "next_charge_at": "ALTER TABLE autopay_settings ADD COLUMN next_charge_at TEXT",
            "created_at": "ALTER TABLE autopay_settings ADD COLUMN created_at TEXT",
            "updated_at": "ALTER TABLE autopay_settings ADD COLUMN updated_at TEXT",
        })

    async def ensure_user(self, telegram_id: int) -> None:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO users (telegram_user_id, telegram_id, referral_code, created_at, updated_at, last_seen_at, login_count)
                VALUES (?, ?, ?, ?, ?, ?, 0)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    telegram_id=COALESCE(users.telegram_id, excluded.telegram_id),
                    referral_code=COALESCE(users.referral_code, excluded.referral_code),
                    updated_at=excluded.updated_at,
                    last_seen_at=excluded.last_seen_at
                """,
                (tg_text_id(telegram_id), telegram_id, referral_code_for(telegram_id), now, now, now),
            )
            await db.commit()

    async def upsert_user(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
        photo_url: str | None = None,
        track_visit: bool = False,
    ) -> None:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO users (
                    telegram_user_id, telegram_id, username, first_name, last_name,
                    language_code, photo_url, referral_code, created_at, updated_at, last_seen_at, login_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    telegram_id=excluded.telegram_id,
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    language_code=COALESCE(excluded.language_code, users.language_code),
                    photo_url=COALESCE(excluded.photo_url, users.photo_url),
                    referral_code=COALESCE(users.referral_code, excluded.referral_code),
                    updated_at=excluded.updated_at,
                    last_seen_at=excluded.last_seen_at,
                    login_count=COALESCE(users.login_count, 0) + COALESCE(excluded.login_count, 0)
                """,
                (
                    tg_text_id(telegram_id),
                    telegram_id,
                    username,
                    first_name,
                    last_name,
                    language_code,
                    photo_url,
                    referral_code_for(telegram_id),
                    now,
                    now,
                    now,
                    1 if track_visit else 0,
                ),
            )
            await db.commit()

    async def save_request(self, telegram_id: int, mode: str, user_text: str, ai_answer: str) -> int:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                INSERT INTO ai_requests (telegram_id, mode, user_text, ai_answer, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (telegram_id, mode, user_text, ai_answer, now),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def count_requests_since(self, telegram_id: int, since_iso: str) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM ai_requests WHERE telegram_id = ? AND created_at >= ?)
                    +
                    (
                        SELECT COUNT(*)
                        FROM chat_messages m
                        JOIN conversations c ON c.id = m.conversation_id
                        WHERE c.telegram_user_id = ?
                          AND m.role = 'assistant'
                          AND m.created_at >= ?
                    )
                """,
                (telegram_id, since_iso, tg_text_id(telegram_id), since_iso),
            )
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def count_requests_total(self, telegram_id: int) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM ai_requests WHERE telegram_id = ?)
                    +
                    (
                        SELECT COUNT(*)
                        FROM chat_messages m
                        JOIN conversations c ON c.id = m.conversation_id
                        WHERE c.telegram_user_id = ?
                          AND m.role = 'assistant'
                    )
                """,
                (telegram_id, tg_text_id(telegram_id)),
            )
            row = await cursor.fetchone()
            return int(row[0]) if row else 0

    async def sum_credits_since(self, telegram_id: int, since_iso: str) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                SELECT COALESCE(SUM(
                    CASE
                        WHEN transaction_type = 'charge' THEN amount
                        WHEN transaction_type = 'refund' THEN -amount
                        ELSE 0
                    END
                ), 0)
                FROM credit_transactions
                WHERE telegram_user_id = ? AND created_at >= ?
                """,
                (tg_text_id(telegram_id), since_iso),
            )
            row = await cursor.fetchone()
            return max(0, int(row[0] or 0)) if row else 0

    async def sum_credits_total(self, telegram_id: int) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                SELECT COALESCE(SUM(
                    CASE
                        WHEN transaction_type = 'charge' THEN amount
                        WHEN transaction_type = 'refund' THEN -amount
                        ELSE 0
                    END
                ), 0)
                FROM credit_transactions
                WHERE telegram_user_id = ?
                """,
                (tg_text_id(telegram_id),),
            )
            row = await cursor.fetchone()
            return max(0, int(row[0] or 0)) if row else 0

    async def get_reserved_credits(self, telegram_id: int) -> int:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                SELECT COALESCE(SUM(reserved_credits), 0)
                FROM active_ai_requests
                WHERE telegram_user_id = ?
                """,
                (tg_text_id(telegram_id),),
            )
            row = await cursor.fetchone()
            return int(row[0] or 0) if row else 0

    async def reserve_credits(
        self,
        telegram_id: int,
        request_id: str,
        tool_id: str,
        credits: int,
        *,
        free_limit_default: int,
        monthly_limit_default: int,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        credits = max(1, int(credits))
        access = await self.get_access_state(telegram_id, free_limit_default, monthly_limit_default)
        if not access["can_request"]:
            raise CreditLimitError(str(access["denial_reason"]))
        remaining = access.get("remaining")
        if remaining is not None and credits > int(remaining):
            raise CreditLimitError(
                f"Недостаточно кредитов для этого запроса. Нужно примерно {credits}, осталось {remaining}."
            )
        if access.get("unlimited"):
            return access
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO active_ai_requests (
                    request_id, telegram_user_id, tool_id, reserved_credits, started_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    telegram_user_id=excluded.telegram_user_id,
                    tool_id=excluded.tool_id,
                    reserved_credits=excluded.reserved_credits,
                    started_at=excluded.started_at
                """,
                (request_id, tg_text_id(telegram_id), tool_id, credits, now),
            )
            await db.execute(
                """
                INSERT INTO credit_transactions (
                    telegram_user_id, request_id, transaction_type, amount, reason, metadata_json, created_at
                ) VALUES (?, ?, 'reserve', ?, ?, ?, ?)
                """,
                (
                    tg_text_id(telegram_id),
                    request_id,
                    credits,
                    f"reserve:{tool_id}",
                    json.dumps(metadata or {}, ensure_ascii=False, separators=(",", ":")),
                    now,
                ),
            )
            await db.commit()
        return access

    async def finalize_credit_charge(
        self,
        telegram_id: int,
        request_id: str,
        tool_id: str,
        estimated_credits: int,
        charged_credits: int,
        *,
        model: str | None,
        input_tokens: int,
        output_tokens: int,
        status: str = "success",
        error_message: str | None = None,
    ) -> None:
        now = utc_now_iso()
        charged_credits = max(0, int(charged_credits))
        total_tokens = max(0, int(input_tokens or 0)) + max(0, int(output_tokens or 0))
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM active_ai_requests WHERE request_id = ?", (request_id,))
            if charged_credits:
                await db.execute(
                    """
                    INSERT INTO credit_transactions (
                        telegram_user_id, request_id, transaction_type, amount, reason, metadata_json, created_at
                    ) VALUES (?, ?, 'charge', ?, ?, ?, ?)
                    """,
                    (
                        tg_text_id(telegram_id),
                        request_id,
                        charged_credits,
                        f"charge:{tool_id}",
                        json.dumps({"estimated": estimated_credits, "model": model}, ensure_ascii=False, separators=(",", ":")),
                        now,
                    ),
                )
            await db.execute(
                """
                INSERT INTO ai_usage_events (
                    telegram_user_id, request_id, tool_id, model, input_tokens, output_tokens,
                    total_tokens, credits_estimated, credits_charged, status, error_message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tg_text_id(telegram_id),
                    request_id,
                    tool_id,
                    model,
                    int(input_tokens or 0),
                    int(output_tokens or 0),
                    total_tokens,
                    int(estimated_credits or 0),
                    charged_credits,
                    status,
                    error_message,
                    now,
                ),
            )
            await db.commit()

    async def refund_reserved_credits(
        self,
        telegram_id: int,
        request_id: str,
        reason: str,
        *,
        tool_id: str | None = None,
        estimated_credits: int = 0,
        model: str | None = None,
    ) -> None:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT reserved_credits, tool_id FROM active_ai_requests WHERE request_id = ?",
                (request_id,),
            )
            row = await cursor.fetchone()
            reserved = int(row[0]) if row else int(estimated_credits or 0)
            effective_tool = tool_id or (str(row[1]) if row else None) or "unknown"
            await db.execute("DELETE FROM active_ai_requests WHERE request_id = ?", (request_id,))
            await db.execute(
                """
                INSERT INTO credit_transactions (
                    telegram_user_id, request_id, transaction_type, amount, reason, metadata_json, created_at
                ) VALUES (?, ?, 'refund', ?, ?, ?, ?)
                """,
                (
                    tg_text_id(telegram_id),
                    request_id,
                    reserved,
                    reason,
                    json.dumps({"tool_id": effective_tool}, ensure_ascii=False, separators=(",", ":")),
                    now,
                ),
            )
            await db.execute(
                """
                INSERT INTO ai_usage_events (
                    telegram_user_id, request_id, tool_id, model, input_tokens, output_tokens,
                    total_tokens, credits_estimated, credits_charged, status, error_message, created_at
                ) VALUES (?, ?, ?, ?, 0, 0, 0, ?, 0, 'error', ?, ?)
                """,
                (tg_text_id(telegram_id), request_id, effective_tool, model, int(estimated_credits or 0), reason, now),
            )
            await db.commit()

    async def get_user_profile(self, telegram_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT *
                FROM users
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (telegram_id, tg_text_id(telegram_id)),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None


    async def get_organization_member_access(self, telegram_id: int, now: datetime | None = None) -> dict[str, Any] | None:
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        try:
            async with aiosqlite.connect(self.path) as db:
                db.row_factory = aiosqlite.Row
                cur = await db.execute(
                    """
                    SELECT
                        o.id AS organization_id,
                        o.title AS organization_title,
                        o.owner_telegram_user_id,
                        om.role,
                        om.limited_access,
                        u.plan AS owner_plan,
                        u.subscription_until AS owner_subscription_until,
                        u.subscription_expires_at AS owner_subscription_expires_at,
                        u.unlimited_access AS owner_unlimited_access
                    FROM organization_members om
                    JOIN organizations o ON o.id = om.organization_id
                    LEFT JOIN users u ON u.telegram_user_id = o.owner_telegram_user_id OR CAST(u.telegram_id AS TEXT) = o.owner_telegram_user_id
                    WHERE om.telegram_user_id = ? AND om.status = 'active'
                    ORDER BY om.joined_at DESC
                    LIMIT 1
                    """,
                    (tg_text_id(telegram_id),),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                item = dict(row)
                owner_until = parse_iso_datetime(item.get("owner_subscription_until") or item.get("owner_subscription_expires_at"))
                owner_active = bool(item.get("owner_unlimited_access")) or (str(item.get("owner_plan") or "").lower() == "business" and bool(owner_until and owner_until >= now))
                if not owner_active:
                    return None
                return item
        except Exception:
            return None

    async def get_access_state(
        self,
        telegram_id: int,
        free_limit_default: int,
        monthly_limit_default: int,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        await self.ensure_user(telegram_id)
        now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        profile = await self.get_user_profile(telegram_id)
        if not profile:
            raise RuntimeError(f"User {telegram_id} was not created")

        raw_plan = str(profile.get("plan") or "free")
        profile_daily_limit = profile.get("daily_limit")
        daily_limit = int(profile_daily_limit) if profile_daily_limit not in (None, 20) else int(free_limit_default)
        bonus_requests = int(profile.get("bonus_requests") or 0)
        purchased_credits = int(profile.get("purchased_credits") or 0)
        free_limit = daily_limit + bonus_requests + purchased_credits
        monthly_limit = profile.get("monthly_limit")
        monthly_limit = int(monthly_limit) if monthly_limit is not None else int(monthly_limit_default)
        if purchased_credits > 0:
            monthly_limit += purchased_credits

        subscription_started_at = parse_iso_datetime(profile.get("subscription_started_at"))
        subscription_until = parse_iso_datetime(profile.get("subscription_until") or profile.get("subscription_expires_at"))
        subscription_active = bool(subscription_until and subscription_until >= now)
        organization_access = await self.get_organization_member_access(telegram_id, now)

        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        paid_period_start = month_start
        if subscription_started_at and subscription_started_at > paid_period_start:
            paid_period_start = subscription_started_at
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        used_total = await self.sum_credits_total(telegram_id)
        used_today = await self.sum_credits_since(telegram_id, day_start.isoformat())
        used_period = await self.sum_credits_since(telegram_id, paid_period_start.isoformat())
        reserved_credits = await self.get_reserved_credits(telegram_id)

        blocked = bool(profile.get("blocked")) or raw_plan == "blocked"
        unlimited = bool(profile.get("unlimited_access")) or raw_plan == "unlimited"

        current_limit: int | None
        used_for_limit: int
        remaining: int | None
        plan = "free"
        status = "free_trial"
        status_label = "Free"
        denial_reason = ""
        daily_remaining: int | None = None
        monthly_remaining: int | None = None

        if blocked:
            plan = "blocked"
            status = "blocked"
            status_label = "Доступ отключен"
            current_limit = 0
            used_for_limit = used_total
            remaining = 0
            daily_remaining = 0
            monthly_remaining = 0
            can_request = False
            denial_reason = "Доступ к боту отключен администратором."
        elif unlimited:
            plan = "unlimited"
            status = "active"
            status_label = "Unlimited"
            current_limit = None
            used_for_limit = used_period
            remaining = None
            daily_remaining = None
            monthly_remaining = None
            can_request = True
        elif subscription_active:
            plan = raw_plan if raw_plan not in {"subscriber"} else "subscriber"
            status = "active"
            status_label = "Подписка активна"
            current_limit = None if monthly_limit <= 0 else monthly_limit
            used_for_limit = used_period
            monthly_remaining = None if current_limit is None else max(current_limit - used_period - reserved_credits, 0)
            daily_remaining = max(daily_limit - used_today - reserved_credits, 0)
            if current_limit is None:
                remaining = daily_remaining
                can_request = daily_remaining > 0
            else:
                remaining = min(daily_remaining, monthly_remaining)
                can_request = remaining > 0
            if not can_request:
                denial_reason = (
                    "Лимит кредитов подписки исчерпан. "
                    "Дождитесь обновления лимита или перейдите на более высокий тариф."
                )
        elif organization_access:
            plan = "business_member"
            status = "organization_active"
            status_label = f"Участник: {organization_access.get('organization_title') or 'Business'}"
            # Ограниченный доступ участника организации: полезно для команды, но не полный Business владельца.
            org_daily_limit = max(int(free_limit_default), 300)
            org_monthly_limit = max(int(monthly_limit_default), 10000)
            current_limit = org_monthly_limit
            used_for_limit = used_period
            monthly_remaining = max(org_monthly_limit - used_period - reserved_credits, 0)
            daily_remaining = max(org_daily_limit - used_today - reserved_credits, 0)
            remaining = min(daily_remaining, monthly_remaining)
            can_request = remaining > 0
            daily_limit = org_daily_limit
            monthly_limit = org_monthly_limit
            if not can_request:
                denial_reason = "Лимит участника организации исчерпан. Попросите владельца выдать больший доступ или купите личный тариф."
        else:
            status = "expired" if subscription_until else "free_trial"
            status_label = "Free" if not subscription_until else "Подписка истекла"
            # Free has both a daily anti-abuse limit and a small monthly budget.
            # Purchased credits are added to the monthly budget, but not to the daily anti-spam cap.
            current_limit = monthly_limit
            used_for_limit = used_period
            daily_remaining = max(free_limit - used_today - reserved_credits, 0)
            monthly_remaining = max(monthly_limit - used_period - reserved_credits, 0)
            remaining = min(daily_remaining, monthly_remaining)
            can_request = remaining > 0
            if not can_request:
                denial_reason = (
                    f"Лимит Free исчерпан: {free_limit} кредитов в день, {monthly_limit} кредитов в месяц. "
                    "Попробуйте позже или перейдите на платный тариф."
                )

        return {
            "telegram_id": telegram_id,
            "telegram_user_id": tg_text_id(telegram_id),
            "plan": plan,
            "raw_plan": raw_plan,
            "status": status,
            "status_label": status_label,
            "can_request": can_request,
            "denial_reason": denial_reason,
            "free_limit": free_limit,
            "daily_limit": daily_limit,
            "bonus_requests": bonus_requests,
            "purchased_credits": purchased_credits,
            "monthly_limit": monthly_limit,
            "current_limit": current_limit,
            "remaining": remaining,
            "daily_remaining": daily_remaining,
            "monthly_remaining": monthly_remaining,
            "used_today": used_today,
            "used_total": used_total,
            "used_period": used_for_limit,
            "credits_used_today": used_today,
            "credits_used_period": used_for_limit,
            "credits_used_total": used_total,
            "credits_reserved": reserved_credits,
            "subscription_started_at": profile.get("subscription_started_at"),
            "subscription_until": profile.get("subscription_until") or profile.get("subscription_expires_at"),
            "unlimited": unlimited,
            "blocked": blocked,
            "admin_note": profile.get("admin_note"),
            "unit_name": "кредиты",
            "organization": organization_access,
        }

    async def list_recent_requests(self, telegram_id: int, limit: int = 10) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, mode, user_text, ai_answer, created_at
                FROM ai_requests
                WHERE telegram_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (telegram_id, limit),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def create_conversation(self, telegram_id: int, title: str) -> str:
        await self.ensure_user(telegram_id)
        now = utc_now_iso()
        conversation_id = uuid4().hex
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO conversations (id, telegram_user_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (conversation_id, tg_text_id(telegram_id), title[:120] or "Новый диалог", now, now),
            )
            await db.commit()
            return conversation_id

    async def get_conversation(self, telegram_id: int, conversation_id: str | int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, telegram_user_id, title, created_at, updated_at, is_archived
                FROM conversations
                WHERE id = ? AND telegram_user_id = ? AND is_archived = 0
                """,
                (str(conversation_id), tg_text_id(telegram_id)),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_or_create_conversation(
        self,
        telegram_id: int,
        conversation_id: str | int | None,
        first_message: str,
    ) -> str:
        if conversation_id is not None:
            existing = await self.get_conversation(telegram_id, conversation_id)
            if existing:
                return str(existing["id"])
        title = " ".join(first_message.strip().split())[:60] or "Новый диалог"
        return await self.create_conversation(telegram_id, title)

    async def add_chat_message(
        self,
        conversation_id: str | int,
        role: str,
        content: str,
        model: str | None = None,
        tokens_used: int = 0,
    ) -> int:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                INSERT INTO chat_messages (conversation_id, role, content, model, tokens_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (str(conversation_id), role, content, model, tokens_used, now),
            )
            await db.execute(
                """
                UPDATE conversations
                SET updated_at = ?
                WHERE id = ?
                """,
                (now, str(conversation_id)),
            )
            if role == "user":
                auto_title = " ".join(str(content or "").replace("\n", " ").split()).strip()
                if auto_title:
                    auto_title = auto_title[:57].rstrip() + ("…" if len(auto_title) > 57 else "")
                    await db.execute(
                        """
                        UPDATE conversations
                        SET title = ?, updated_at = ?
                        WHERE id = ?
                          AND (title IS NULL OR title = '' OR title = 'Новый диалог' OR title = 'Новый чат' OR title = 'Диалог')
                        """,
                        (auto_title, now, str(conversation_id)),
                    )
            if role == "assistant":
                cursor_user = await db.execute(
                    "SELECT telegram_user_id FROM conversations WHERE id = ?",
                    (str(conversation_id),),
                )
                row = await cursor_user.fetchone()
                if row:
                    await db.execute(
                        """
                        INSERT INTO usage_logs (telegram_user_id, action_type, tokens_used, created_at)
                        VALUES (?, 'chat_message', ?, ?)
                        """,
                        (str(row[0]), tokens_used, now),
                    )
            await db.commit()
            return int(cursor.lastrowid)

    async def list_chat_messages(self, conversation_id: str | int, limit: int = 20) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, conversation_id, role, content, model, tokens_used, created_at
                FROM (
                    SELECT id, conversation_id, role, content, model, tokens_used, created_at
                    FROM chat_messages
                    WHERE conversation_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                )
                ORDER BY id ASC
                """,
                (str(conversation_id), limit),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def list_conversations(self, telegram_id: int, limit: int = 20) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT
                    c.id,
                    c.title,
                    c.created_at,
                    c.updated_at,
                    c.is_archived,
                    (
                        SELECT content
                        FROM chat_messages
                        WHERE conversation_id = c.id
                        ORDER BY id DESC
                        LIMIT 1
                    ) AS preview,
                    (
                        SELECT COUNT(*)
                        FROM chat_messages
                        WHERE conversation_id = c.id
                    ) AS messages_count
                FROM conversations c
                WHERE c.telegram_user_id = ? AND c.is_archived = 0
                ORDER BY c.updated_at DESC
                LIMIT ?
                """,
                (tg_text_id(telegram_id), limit),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def list_users(self, limit: int = 30) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT
                    u.telegram_id,
                    u.telegram_user_id,
                    u.username,
                    u.first_name,
                    u.last_name,
                    u.language_code,
                    u.plan,
                    u.daily_limit,
                    u.free_limit,
                    u.purchased_credits,
                    u.monthly_limit,
                    u.subscription_until,
                    u.unlimited_access,
                    u.blocked,
                    u.admin_note,
                    u.created_at,
                    u.updated_at,
                    u.last_seen_at,
                    COUNT(r.id) AS requests_total,
                    MAX(r.created_at) AS last_request_at
                FROM users u
                LEFT JOIN ai_requests r ON r.telegram_id = u.telegram_id
                GROUP BY u.id
                ORDER BY u.updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


    async def adjust_purchased_credits(
        self,
        telegram_id: int,
        admin_id: int | None,
        delta: int,
        note: str | None = None,
    ) -> dict[str, Any]:
        await self.ensure_user(telegram_id)
        now = utc_now_iso()
        delta = int(delta)
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT purchased_credits
                FROM users
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (telegram_id, tg_text_id(telegram_id)),
            )
            row = await cursor.fetchone()
            current = int((row["purchased_credits"] if row else 0) or 0)
            new_value = max(0, current + delta)
            actual_delta = new_value - current
            await db.execute(
                """
                UPDATE users
                SET purchased_credits = ?,
                    access_updated_at = ?,
                    updated_at = ?,
                    last_seen_at = ?
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (new_value, now, now, now, telegram_id, tg_text_id(telegram_id)),
            )
            await db.execute(
                """
                INSERT INTO credit_transactions (
                    telegram_user_id, request_id, transaction_type, amount, balance_after, reason, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tg_text_id(telegram_id),
                    f"admin_{now}",
                    "admin_grant" if actual_delta >= 0 else "admin_revoke",
                    abs(actual_delta),
                    new_value,
                    note or "admin_manual_adjustment",
                    json.dumps({"admin_id": admin_id, "delta": actual_delta}, ensure_ascii=False, separators=(",", ":")),
                    now,
                ),
            )
            await db.commit()
        await self.record_access_event(
            telegram_id,
            admin_id,
            "credits_adjusted",
            {"delta": actual_delta, "balance_after": new_value, "note": note},
        )
        return {"telegram_id": telegram_id, "previous": current, "delta": actual_delta, "purchased_credits": new_value}

    async def list_credit_transactions(self, telegram_id: int | None = None, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 100))
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            if telegram_id is None:
                cursor = await db.execute(
                    """
                    SELECT id, telegram_user_id, request_id, transaction_type, amount, balance_after, reason, created_at
                    FROM credit_transactions
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT id, telegram_user_id, request_id, transaction_type, amount, balance_after, reason, created_at
                    FROM credit_transactions
                    WHERE telegram_user_id = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (tg_text_id(telegram_id), limit),
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def list_billing_orders(self, limit: int = 20, status: str | None = None) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 100))
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            if status:
                cursor = await db.execute(
                    """
                    SELECT id, telegram_user_id, plan, provider, amount, currency, status, external_payment_id, created_at, updated_at
                    FROM billing_orders
                    WHERE status = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (status, limit),
                )
            else:
                cursor = await db.execute(
                    """
                    SELECT id, telegram_user_id, plan, provider, amount, currency, status, external_payment_id, created_at, updated_at
                    FROM billing_orders
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def list_payments(self, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 100))
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, order_id, telegram_user_id, provider, plan, amount, currency, status, external_payment_id, created_at
                FROM payments
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def list_error_logs(self, limit: int = 20) -> list[dict[str, Any]]:
        limit = max(1, min(int(limit), 100))
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, telegram_user_id, source, error_text, created_at
                FROM error_logs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def reset_user_history(self, telegram_id: int, admin_id: int | None, note: str | None = None) -> dict[str, Any]:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                UPDATE conversations
                SET is_archived = 1, updated_at = ?
                WHERE telegram_user_id = ? AND is_archived = 0
                """,
                (now, tg_text_id(telegram_id)),
            )
            archived = int(cursor.rowcount or 0)
            await db.commit()
        await self.record_access_event(telegram_id, admin_id, "history_reset", {"archived": archived, "note": note})
        return {"telegram_id": telegram_id, "archived": archived}

    async def get_business_profile(self, telegram_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT *
                FROM business_profiles
                WHERE telegram_user_id = ?
                """,
                (tg_text_id(telegram_id),),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def upsert_business_profile(self, telegram_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        await self.ensure_user(telegram_id)
        now = utc_now_iso()
        allowed = {
            "user_type",
            "main_goal",
            "business_name",
            "niche",
            "marketplace",
            "target_audience",
            "average_price",
            "description",
            "main_problem",
            "inn",
        }
        data = {key: (str(payload.get(key)).strip() if payload.get(key) is not None else None) for key in allowed}
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO business_profiles (
                    telegram_user_id, user_type, main_goal, business_name, niche, marketplace,
                    target_audience, average_price, description, main_problem, inn, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    user_type=excluded.user_type,
                    main_goal=excluded.main_goal,
                    business_name=excluded.business_name,
                    niche=excluded.niche,
                    marketplace=excluded.marketplace,
                    target_audience=excluded.target_audience,
                    average_price=excluded.average_price,
                    description=excluded.description,
                    main_problem=excluded.main_problem,
                    inn=excluded.inn,
                    updated_at=excluded.updated_at
                """,
                (
                    tg_text_id(telegram_id),
                    data["user_type"],
                    data["main_goal"],
                    data["business_name"],
                    data["niche"],
                    data["marketplace"],
                    data["target_audience"],
                    data["average_price"],
                    data["description"],
                    data["main_problem"],
                    data["inn"],
                    now,
                    now,
                ),
            )
            await db.commit()
        profile = await self.get_business_profile(telegram_id)
        return profile or {}

    async def clear_business_profile(self, telegram_id: int) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute("DELETE FROM business_profiles WHERE telegram_user_id = ?", (tg_text_id(telegram_id),))
            await db.commit()

    async def complete_onboarding(self, telegram_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        profile = await self.upsert_business_profile(telegram_id, payload)
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET onboarding_completed = 1,
                    updated_at = ?,
                    last_seen_at = ?
                WHERE telegram_user_id = ?
                """,
                (now, now, tg_text_id(telegram_id)),
            )
            await db.commit()
        return profile

    async def create_tool_run(
        self,
        telegram_id: int,
        tool_id: str,
        input_data: dict[str, Any],
        result_text: str | None = None,
        model: str | None = None,
        status: str = "success",
        error_message: str | None = None,
        tokens_used: int = 0,
    ) -> int:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                INSERT INTO tool_runs (
                    telegram_user_id, tool_id, input_json, result_text, model,
                    tokens_used, status, error_message, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tg_text_id(telegram_id),
                    tool_id,
                    json.dumps(input_data, ensure_ascii=False),
                    result_text,
                    model,
                    tokens_used,
                    status,
                    error_message,
                    now,
                ),
            )
            await db.execute(
                """
                INSERT INTO usage_logs (telegram_user_id, action_type, tokens_used, created_at)
                VALUES (?, 'tool_run', ?, ?)
                """,
                (tg_text_id(telegram_id), tokens_used, now),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def list_tool_runs(self, telegram_id: int, limit: int = 20) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, telegram_user_id, tool_id, input_json, result_text, model, tokens_used, status, error_message, created_at
                FROM tool_runs
                WHERE telegram_user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (tg_text_id(telegram_id), limit),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def save_result(
        self,
        telegram_id: int,
        source_type: str,
        source_id: str,
        title: str | None,
        content: str,
    ) -> int:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                INSERT INTO saved_results (telegram_user_id, source_type, source_id, title, content, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (tg_text_id(telegram_id), source_type, source_id, title, content, now),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def list_saved_results(self, telegram_id: int, limit: int = 50) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id, source_type, source_id, title, content, created_at
                FROM saved_results
                WHERE telegram_user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (tg_text_id(telegram_id), limit),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def delete_saved_result(self, telegram_id: int, saved_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "DELETE FROM saved_results WHERE id = ? AND telegram_user_id = ?",
                (saved_id, tg_text_id(telegram_id)),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def save_feedback(
        self,
        telegram_id: int,
        rating: int,
        message: str | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
    ) -> int:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                INSERT INTO feedback (telegram_user_id, source_type, source_id, rating, message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (tg_text_id(telegram_id), source_type, source_id, rating, message or "", now),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def set_referrer(self, telegram_id: int, referral_code: str) -> None:
        invited_id = tg_text_id(telegram_id)
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT telegram_user_id FROM users WHERE referral_code = ?",
                (referral_code,),
            )
            referrer = await cursor.fetchone()
            if not referrer or str(referrer["telegram_user_id"]) == invited_id:
                return
            referrer_id = str(referrer["telegram_user_id"])
            existing = await db.execute(
                """
                SELECT id FROM referrals
                WHERE invited_telegram_user_id = ?
                """,
                (invited_id,),
            )
            if await existing.fetchone():
                return
            now = utc_now_iso()
            await db.execute(
                """
                INSERT INTO referrals (referrer_telegram_user_id, invited_telegram_user_id, bonus_given, created_at)
                VALUES (?, ?, 1, ?)
                """,
                (referrer_id, invited_id, now),
            )
            await db.execute(
                """
                UPDATE users
                SET referred_by = COALESCE(referred_by, ?)
                WHERE telegram_user_id = ?
                """,
                (referrer_id, invited_id),
            )
            await db.execute(
                """
                UPDATE users
                SET bonus_requests = COALESCE(bonus_requests, 0) + 5
                WHERE telegram_user_id = ?
                """,
                (referrer_id,),
            )
            await db.commit()

    async def referral_stats(self, telegram_id: int, bot_username: str | None = None) -> dict[str, Any]:
        await self.ensure_user(telegram_id)
        profile = await self.get_user_profile(telegram_id)
        code = (profile or {}).get("referral_code") or referral_code_for(telegram_id)
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                "SELECT COUNT(*) FROM referrals WHERE referrer_telegram_user_id = ?",
                (tg_text_id(telegram_id),),
            )
            invited = int((await cursor.fetchone())[0])
        link = f"https://t.me/{bot_username}?start={code}" if bot_username else code
        return {
            "referral_code": code,
            "referral_link": link,
            "invited_count": invited,
            "bonus_requests": int((profile or {}).get("bonus_requests") or 0),
        }

    async def archive_conversation(self, telegram_id: int, conversation_id: str) -> bool:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                UPDATE conversations
                SET is_archived = 1, updated_at = ?
                WHERE id = ? AND telegram_user_id = ?
                """,
                (now, conversation_id, tg_text_id(telegram_id)),
            )
            await db.commit()
            return cursor.rowcount > 0

    async def create_billing_order(
        self,
        order_id: str,
        telegram_id: int,
        plan: str,
        provider: str,
        amount: float,
        currency: str,
        metadata: dict[str, Any] | None = None,
        expires_at: str | None = None,
    ) -> dict[str, Any]:
        now = utc_now_iso()
        metadata_json = json.dumps(metadata or {}, ensure_ascii=False, separators=(",", ":"))
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO billing_orders (
                    id, telegram_user_id, plan, provider, amount, currency, status,
                    metadata_json, created_at, updated_at, expires_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)
                """,
                (order_id, tg_text_id(telegram_id), plan, provider, amount, currency, metadata_json, now, now, expires_at),
            )
            await db.commit()
        order = await self.get_billing_order(order_id)
        if not order:
            raise RuntimeError("Billing order was not created")
        return order

    async def get_billing_order(self, order_id: str) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM billing_orders WHERE id = ?", (order_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def find_billing_order_by_external_id(self, external_payment_id: str) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM billing_orders WHERE external_payment_id = ? ORDER BY created_at DESC LIMIT 1",
                (external_payment_id,),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def update_billing_order(
        self,
        order_id: str,
        *,
        status: str | None = None,
        payment_url: str | None = None,
        external_payment_id: str | None = None,
        payload: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        order = await self.get_billing_order(order_id)
        if not order:
            return None
        new_status = status or order.get("status")
        new_payment_url = payment_url if payment_url is not None else order.get("payment_url")
        new_external = external_payment_id if external_payment_id is not None else order.get("external_payment_id")
        new_payload = payload if payload is not None else order.get("payload")
        metadata_json = order.get("metadata_json")
        if metadata is not None:
            metadata_json = json.dumps(metadata, ensure_ascii=False, separators=(",", ":"))
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE billing_orders
                SET status = ?, payment_url = ?, external_payment_id = ?, payload = ?,
                    metadata_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (new_status, new_payment_url, new_external, new_payload, metadata_json, now, order_id),
            )
            await db.commit()
        return await self.get_billing_order(order_id)

    async def record_payment_event(
        self,
        provider: str,
        raw: dict[str, Any],
        event_type: str | None = None,
        order_id: str | None = None,
        external_payment_id: str | None = None,
    ) -> int:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                INSERT INTO payment_events (provider, event_type, order_id, external_payment_id, raw_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (provider, event_type, order_id, external_payment_id, json.dumps(raw, ensure_ascii=False), now),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def record_payment(
        self,
        *,
        order_id: str | None,
        telegram_id: int,
        provider: str,
        plan: str | None,
        amount: float | None,
        currency: str | None,
        status: str,
        external_payment_id: str | None = None,
        external_charge_id: str | None = None,
        payload: str | None = None,
        raw_event: dict[str, Any] | None = None,
    ) -> int:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            cursor = await db.execute(
                """
                INSERT INTO payments (
                    order_id, telegram_user_id, provider, plan, amount, currency, status,
                    external_payment_id, external_charge_id, payload, raw_event_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    order_id,
                    tg_text_id(telegram_id),
                    provider,
                    plan,
                    amount,
                    currency,
                    status,
                    external_payment_id,
                    external_charge_id,
                    payload,
                    json.dumps(raw_event, ensure_ascii=False) if raw_event is not None else None,
                    now,
                ),
            )
            await db.commit()
            return int(cursor.lastrowid)

    async def activate_paid_subscription(
        self,
        telegram_id: int,
        plan: str,
        provider: str,
        order_id: str,
        daily_limit: int,
        monthly_limit: int | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        await self.ensure_user(telegram_id)
        if monthly_limit is None:
            monthly_limit = daily_limit
        now_dt = datetime.now(timezone.utc)
        expires_dt = now_dt + timedelta(days=days)
        now = now_dt.isoformat()
        expires_at = expires_dt.isoformat()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET plan = ?, daily_limit = ?, free_limit = ?, monthly_limit = ?,
                    subscription_started_at = ?, subscription_until = ?, subscription_expires_at = ?,
                    unlimited_access = 0, blocked = 0, access_updated_at = ?, updated_at = ?, last_seen_at = ?
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (plan, daily_limit, daily_limit, monthly_limit, now, expires_at, expires_at, now, now, now, telegram_id, tg_text_id(telegram_id)),
            )
            await db.execute(
                """
                UPDATE subscriptions
                SET status = 'expired', updated_at = ?
                WHERE telegram_user_id = ? AND status = 'active'
                """,
                (now, tg_text_id(telegram_id)),
            )
            await db.execute(
                """
                INSERT INTO subscriptions (
                    telegram_user_id, plan, status, started_at, expires_at, daily_limit,
                    monthly_limit, provider, order_id, created_at, updated_at
                )
                VALUES (?, ?, 'active', ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (tg_text_id(telegram_id), plan, now, expires_at, daily_limit, monthly_limit, provider, order_id, now, now),
            )
            await db.execute(
                """
                UPDATE billing_orders
                SET status = 'paid', updated_at = ?
                WHERE id = ?
                """,
                (now, order_id),
            )
            await db.commit()
        await self.record_access_event(
            telegram_id,
            None,
            "subscription_paid",
            {"plan": plan, "provider": provider, "order_id": order_id, "daily_limit": daily_limit, "monthly_limit": monthly_limit, "expires_at": expires_at},
        )
        return {"plan": plan, "daily_limit": daily_limit, "monthly_limit": monthly_limit, "expires_at": expires_at, "status": "active"}

    async def upsert_payout_method(
        self,
        telegram_id: int,
        *,
        bik: str,
        account_number_encrypted: str,
        account_last4: str,
        account_mask: str,
        bank_name: str | None = None,
        holder_name: str | None = None,
    ) -> dict[str, Any]:
        now = utc_now_iso()
        await self.ensure_user(telegram_id)
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO payout_methods(
                    telegram_user_id, bik, bank_name, account_number_encrypted,
                    account_last4, account_mask, holder_name, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'saved', ?, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    bik=excluded.bik,
                    bank_name=excluded.bank_name,
                    account_number_encrypted=excluded.account_number_encrypted,
                    account_last4=excluded.account_last4,
                    account_mask=excluded.account_mask,
                    holder_name=excluded.holder_name,
                    status='saved',
                    updated_at=excluded.updated_at
                """,
                (str(telegram_id), bik, bank_name, account_number_encrypted, account_last4, account_mask, holder_name, now, now),
            )
            await db.commit()
        saved = await self.get_payout_method(telegram_id)
        return saved or {}

    async def get_payout_method(self, telegram_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT telegram_user_id, bik, bank_name, account_last4, account_mask, holder_name, status, created_at, updated_at
                FROM payout_methods
                WHERE telegram_user_id = ?
                """,
                (str(telegram_id),),
            )
            row = await cur.fetchone()
            return dict(row) if row else None

    async def get_payout_method_secret(self, telegram_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM payout_methods WHERE telegram_user_id = ?", (str(telegram_id),))
            row = await cur.fetchone()
            return dict(row) if row else None

    async def delete_payout_method(self, telegram_id: int) -> bool:
        async with aiosqlite.connect(self.path) as db:
            cur = await db.execute("DELETE FROM payout_methods WHERE telegram_user_id = ?", (str(telegram_id),))
            await db.commit()
            return cur.rowcount > 0

    async def upsert_autopay_settings(
        self,
        telegram_id: int,
        *,
        enabled: bool,
        provider: str = "yookassa",
        plan: str | None = None,
        status: str | None = None,
        payment_method_id_encrypted: str | None = None,
        payment_method_mask: str | None = None,
        next_charge_at: str | None = None,
    ) -> dict[str, Any]:
        now = utc_now_iso()
        existing = await self.get_autopay_settings_secret(telegram_id)
        encrypted = payment_method_id_encrypted if payment_method_id_encrypted is not None else (existing or {}).get("payment_method_id_encrypted")
        mask = payment_method_mask if payment_method_mask is not None else (existing or {}).get("payment_method_mask")
        final_status = status or ("active" if enabled and encrypted else "pending_payment_method" if enabled else "disabled")
        consent_at = now if enabled else (existing or {}).get("consent_at")
        created_at = (existing or {}).get("created_at") or now
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO autopay_settings(
                    telegram_user_id, enabled, provider, plan, payment_method_id_encrypted,
                    payment_method_mask, status, consent_at, next_charge_at, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    enabled=excluded.enabled,
                    provider=excluded.provider,
                    plan=COALESCE(excluded.plan, autopay_settings.plan),
                    payment_method_id_encrypted=COALESCE(excluded.payment_method_id_encrypted, autopay_settings.payment_method_id_encrypted),
                    payment_method_mask=COALESCE(excluded.payment_method_mask, autopay_settings.payment_method_mask),
                    status=excluded.status,
                    consent_at=COALESCE(excluded.consent_at, autopay_settings.consent_at),
                    next_charge_at=COALESCE(excluded.next_charge_at, autopay_settings.next_charge_at),
                    updated_at=excluded.updated_at
                """,
                (str(telegram_id), 1 if enabled else 0, provider, plan, encrypted, mask, final_status, consent_at, next_charge_at, created_at, now),
            )
            await db.commit()
        public = await self.get_autopay_settings(telegram_id)
        return public or {}

    async def get_autopay_settings(self, telegram_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT telegram_user_id, enabled, provider, plan, payment_method_mask, status,
                       consent_at, last_charge_at, next_charge_at, created_at, updated_at
                FROM autopay_settings
                WHERE telegram_user_id = ?
                """,
                (str(telegram_id),),
            )
            row = await cur.fetchone()
            if not row:
                return None
            item = dict(row)
            item["enabled"] = bool(item.get("enabled"))
            item["has_payment_method"] = bool(item.get("payment_method_mask"))
            return item

    async def get_autopay_settings_secret(self, telegram_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM autopay_settings WHERE telegram_user_id = ?", (str(telegram_id),))
            row = await cur.fetchone()
            return dict(row) if row else None

    async def save_autopay_payment_method(
        self,
        telegram_id: int,
        *,
        plan: str,
        payment_method_id_encrypted: str,
        payment_method_mask: str,
        next_charge_at: str | None,
    ) -> dict[str, Any]:
        await self.upsert_autopay_settings(
            telegram_id,
            enabled=True,
            provider="yookassa",
            plan=plan,
            status="active",
            payment_method_id_encrypted=payment_method_id_encrypted,
            payment_method_mask=payment_method_mask,
            next_charge_at=next_charge_at,
        )
        public = await self.get_autopay_settings(telegram_id)
        return public or {}

    async def mark_autopay_charge(self, telegram_id: int, *, status: str, next_charge_at: str | None = None) -> None:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE autopay_settings
                SET status = ?, last_charge_at = ?, next_charge_at = COALESCE(?, next_charge_at), updated_at = ?
                WHERE telegram_user_id = ?
                """,
                (status, now, next_charge_at, now, str(telegram_id)),
            )
            await db.commit()

    async def list_due_autopay(self, limit: int = 50) -> list[dict[str, Any]]:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT ap.*, u.telegram_id, u.subscription_until, u.subscription_expires_at
                FROM autopay_settings ap
                JOIN users u ON u.telegram_user_id = ap.telegram_user_id OR CAST(u.telegram_id AS TEXT) = ap.telegram_user_id
                WHERE ap.enabled = 1
                  AND ap.status IN ('active', 'retry')
                  AND ap.payment_method_id_encrypted IS NOT NULL
                  AND (u.subscription_until IS NULL OR u.subscription_until <= ? OR ap.next_charge_at <= ?)
                ORDER BY COALESCE(ap.next_charge_at, u.subscription_until, ap.updated_at) ASC
                LIMIT ?
                """,
                (now, now, int(limit)),
            )
            return [dict(row) for row in await cur.fetchall()]

    async def expire_subscription_if_needed(self, telegram_id: int) -> None:
        profile = await self.get_user_profile(telegram_id)
        if not profile:
            return
        raw_plan = str(profile.get("plan") or "free")
        if raw_plan in {"free", "blocked", "unlimited"}:
            return
        until = parse_iso_datetime(profile.get("subscription_until") or profile.get("subscription_expires_at"))
        if not until or until >= datetime.now(timezone.utc):
            return
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET plan = 'free', daily_limit = 100, free_limit = 100, monthly_limit = NULL,
                    subscription_started_at = NULL, subscription_until = NULL, subscription_expires_at = NULL,
                    updated_at = ?, access_updated_at = ?
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (now, now, telegram_id, tg_text_id(telegram_id)),
            )
            await db.execute(
                """
                UPDATE subscriptions
                SET status = 'expired', updated_at = ?
                WHERE telegram_user_id = ? AND status = 'active'
                """,
                (now, tg_text_id(telegram_id)),
            )
            await db.commit()

    async def billing_status(self, telegram_id: int, free_limit_default: int, monthly_limit_default: int) -> dict[str, Any]:
        await self.expire_subscription_if_needed(telegram_id)
        access = await self.get_access_state(telegram_id, free_limit_default, monthly_limit_default)
        return {
            "plan": access["raw_plan"] if access["raw_plan"] not in {"subscriber"} else "pro",
            "status": access["status"],
            "status_label": access["status_label"],
            "daily_limit": access["current_limit"],
            "daily_used": access["used_today"],
            "remaining": access["remaining"],
            "credits_daily_limit": access["daily_limit"],
            "credits_monthly_limit": access["monthly_limit"],
            "credits_used_today": access["credits_used_today"],
            "credits_used_month": access["credits_used_period"],
            "credits_remaining": access["remaining"],
            "subscription_expires_at": access["subscription_until"],
            "bonus_requests": access["bonus_requests"],
        }

    async def log_error(self, source: str, error_text: str, telegram_id: int | None = None) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO error_logs (telegram_user_id, source, error_text, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (tg_text_id(telegram_id) if telegram_id is not None else None, source, error_text, utc_now_iso()),
            )
            await db.commit()

    async def admin_stats(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        async with aiosqlite.connect(self.path) as db:
            db.row_factory = aiosqlite.Row

            async def scalar(sql: str, params: tuple[Any, ...] = ()) -> int:
                cursor = await db.execute(sql, params)
                row = await cursor.fetchone()
                return int(row[0]) if row else 0

            popular_cursor = await db.execute(
                """
                SELECT tool_id, COUNT(*) AS count
                FROM tool_runs
                GROUP BY tool_id
                ORDER BY count DESC
                LIMIT 5
                """
            )
            popular_tools = [dict(row) for row in await popular_cursor.fetchall()]

            return {
                "users_total": await scalar("SELECT COUNT(*) FROM users"),
                "requests_today": await scalar("SELECT COUNT(*) FROM usage_logs WHERE created_at >= ?", (day_start,)),
                "credits_charged_today": await scalar("SELECT COALESCE(SUM(amount), 0) FROM credit_transactions WHERE transaction_type = 'charge' AND created_at >= ?", (day_start,)),
                "active_ai_requests": await scalar("SELECT COUNT(*) FROM active_ai_requests"),
                "chat_messages_today": await scalar("SELECT COUNT(*) FROM chat_messages WHERE created_at >= ?", (day_start,)),
                "tool_runs_today": await scalar("SELECT COUNT(*) FROM tool_runs WHERE created_at >= ?", (day_start,)),
                "popular_tools": popular_tools,
                "saved_results_total": await scalar("SELECT COUNT(*) FROM saved_results"),
                "feedback_negative_count": await scalar("SELECT COUNT(*) FROM feedback WHERE rating < 0"),
                "errors_today": await scalar("SELECT COUNT(*) FROM error_logs WHERE created_at >= ?", (day_start,)),
                "active_users_today": await scalar("SELECT COUNT(DISTINCT telegram_user_id) FROM usage_logs WHERE created_at >= ?", (day_start,)),
                "payments_today": await scalar("SELECT COUNT(*) FROM payments WHERE created_at >= ?", (day_start,)),
                "active_subscriptions": await scalar("SELECT COUNT(*) FROM subscriptions WHERE status = 'active'"),
                "pending_orders": await scalar("SELECT COUNT(*) FROM billing_orders WHERE status = 'pending'"),
                "failed_orders": await scalar("SELECT COUNT(*) FROM billing_orders WHERE status IN ('failed', 'canceled', 'expired')"),
                "revenue_rub_total": await scalar("SELECT CAST(COALESCE(SUM(amount), 0) AS INTEGER) FROM payments WHERE status IN ('paid','succeeded') AND currency = 'RUB'"),
                "payments_by_provider": [
                    dict(row)
                    for row in await (await db.execute(
                        """
                        SELECT provider, COUNT(*) AS count, COALESCE(SUM(amount), 0) AS amount
                        FROM payments
                        WHERE status IN ('paid','succeeded')
                        GROUP BY provider
                        ORDER BY count DESC
                        """
                    )).fetchall()
                ],
            }

    async def record_access_event(
        self,
        telegram_id: int,
        admin_id: int | None,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        now = utc_now_iso()
        details_json = json.dumps(details or {}, ensure_ascii=False, separators=(",", ":"))
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO access_events (telegram_id, admin_id, action, details, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (telegram_id, admin_id, action, details_json, now),
            )
            await db.commit()

    async def set_subscription(
        self,
        telegram_id: int,
        admin_id: int | None,
        days: int,
        monthly_limit: int | None = None,
        note: str | None = None,
    ) -> None:
        await self.ensure_user(telegram_id)
        now = datetime.now(timezone.utc)
        until = now + timedelta(days=days)
        now_iso = now.isoformat()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET plan = 'subscriber',
                    subscription_started_at = ?,
                    subscription_until = ?,
                    monthly_limit = COALESCE(?, monthly_limit),
                    unlimited_access = 0,
                    blocked = 0,
                    admin_note = COALESCE(?, admin_note),
                    access_updated_at = ?,
                    updated_at = ?,
                    last_seen_at = ?
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (now_iso, until.isoformat(), monthly_limit, note, now_iso, now_iso, now_iso, telegram_id, tg_text_id(telegram_id)),
            )
            await db.commit()
        await self.record_access_event(
            telegram_id,
            admin_id,
            "subscription_granted",
            {"days": days, "monthly_limit": monthly_limit, "note": note, "until": until.isoformat()},
        )

    async def set_unlimited_access(
        self,
        telegram_id: int,
        admin_id: int | None,
        enabled: bool,
        note: str | None = None,
    ) -> None:
        await self.ensure_user(telegram_id)
        now = utc_now_iso()
        plan = "unlimited" if enabled else "free"
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET plan = ?,
                    unlimited_access = ?,
                    blocked = 0,
                    subscription_until = CASE WHEN ? = 1 THEN subscription_until ELSE NULL END,
                    admin_note = COALESCE(?, admin_note),
                    access_updated_at = ?,
                    updated_at = ?,
                    last_seen_at = ?
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (plan, int(enabled), int(enabled), note, now, now, now, telegram_id, tg_text_id(telegram_id)),
            )
            await db.commit()
        await self.record_access_event(
            telegram_id,
            admin_id,
            "unlimited_enabled" if enabled else "unlimited_disabled",
            {"note": note},
        )

    async def revoke_paid_access(self, telegram_id: int, admin_id: int | None, note: str | None = None) -> None:
        await self.ensure_user(telegram_id)
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET plan = 'free',
                    subscription_started_at = NULL,
                    subscription_until = NULL,
                    unlimited_access = 0,
                    blocked = 0,
                    admin_note = COALESCE(?, admin_note),
                    access_updated_at = ?,
                    updated_at = ?,
                    last_seen_at = ?
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (note, now, now, now, telegram_id, tg_text_id(telegram_id)),
            )
            await db.commit()
        await self.record_access_event(telegram_id, admin_id, "paid_access_revoked", {"note": note})

    async def set_blocked(self, telegram_id: int, admin_id: int | None, blocked: bool, note: str | None = None) -> None:
        await self.ensure_user(telegram_id)
        now = utc_now_iso()
        plan = "blocked" if blocked else "free"
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET plan = ?,
                    blocked = ?,
                    admin_note = COALESCE(?, admin_note),
                    access_updated_at = ?,
                    updated_at = ?,
                    last_seen_at = ?
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (plan, int(blocked), note, now, now, now, telegram_id, tg_text_id(telegram_id)),
            )
            await db.commit()
        await self.record_access_event(
            telegram_id,
            admin_id,
            "blocked" if blocked else "unblocked",
            {"note": note},
        )

    async def set_free_limit(self, telegram_id: int, admin_id: int | None, free_limit: int, note: str | None = None) -> None:
        await self.ensure_user(telegram_id)
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                UPDATE users
                SET free_limit = ?,
                    daily_limit = ?,
                    admin_note = COALESCE(?, admin_note),
                    access_updated_at = ?,
                    updated_at = ?,
                    last_seen_at = ?
                WHERE telegram_id = ? OR telegram_user_id = ?
                """,
                (free_limit, free_limit, note, now, now, now, telegram_id, tg_text_id(telegram_id)),
            )
            await db.commit()
        await self.record_access_event(
            telegram_id,
            admin_id,
            "free_limit_changed",
            {"free_limit": free_limit, "note": note},
        )
