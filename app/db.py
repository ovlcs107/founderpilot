from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import aiosqlite


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT UNIQUE NOT NULL,
    telegram_id INTEGER UNIQUE,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT,
    plan TEXT DEFAULT 'free',
    daily_limit INTEGER DEFAULT 20,
    bonus_requests INTEGER DEFAULT 0,
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
    last_seen_at TEXT
);

CREATE TABLE IF NOT EXISTS ai_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    mode TEXT NOT NULL,
    user_text TEXT NOT NULL,
    ai_answer TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);

CREATE TABLE IF NOT EXISTS access_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    admin_id INTEGER,
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
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    provider TEXT,
    amount REAL,
    currency TEXT,
    status TEXT,
    external_payment_id TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT,
    source TEXT NOT NULL,
    error_text TEXT NOT NULL,
    created_at TEXT NOT NULL
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
"""


USER_ADD_COLUMNS = {
    "telegram_id": "ALTER TABLE users ADD COLUMN telegram_id INTEGER",
    "username": "ALTER TABLE users ADD COLUMN username TEXT",
    "first_name": "ALTER TABLE users ADD COLUMN first_name TEXT",
    "last_name": "ALTER TABLE users ADD COLUMN last_name TEXT",
    "language_code": "ALTER TABLE users ADD COLUMN language_code TEXT",
    "plan": "ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free'",
    "daily_limit": "ALTER TABLE users ADD COLUMN daily_limit INTEGER DEFAULT 20",
    "bonus_requests": "ALTER TABLE users ADD COLUMN bonus_requests INTEGER DEFAULT 0",
    "referral_code": "ALTER TABLE users ADD COLUMN referral_code TEXT",
    "referred_by": "ALTER TABLE users ADD COLUMN referred_by TEXT",
    "onboarding_completed": "ALTER TABLE users ADD COLUMN onboarding_completed INTEGER DEFAULT 0",
    "free_limit": "ALTER TABLE users ADD COLUMN free_limit INTEGER NOT NULL DEFAULT 15",
    "monthly_limit": "ALTER TABLE users ADD COLUMN monthly_limit INTEGER",
    "subscription_started_at": "ALTER TABLE users ADD COLUMN subscription_started_at TEXT",
    "subscription_until": "ALTER TABLE users ADD COLUMN subscription_until TEXT",
    "unlimited_access": "ALTER TABLE users ADD COLUMN unlimited_access INTEGER NOT NULL DEFAULT 0",
    "blocked": "ALTER TABLE users ADD COLUMN blocked INTEGER NOT NULL DEFAULT 0",
    "admin_note": "ALTER TABLE users ADD COLUMN admin_note TEXT",
    "access_updated_at": "ALTER TABLE users ADD COLUMN access_updated_at TEXT",
    "updated_at": "ALTER TABLE users ADD COLUMN updated_at TEXT",
    "last_seen_at": "ALTER TABLE users ADD COLUMN last_seen_at TEXT",
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
    "updated_at": "ALTER TABLE business_profiles ADD COLUMN updated_at TEXT",
}

FEEDBACK_ADD_COLUMNS = {
    "source_type": "ALTER TABLE feedback ADD COLUMN source_type TEXT",
    "source_id": "ALTER TABLE feedback ADD COLUMN source_id TEXT",
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


class Database:
    def __init__(self, path: str) -> None:
        self.path = path

    async def init(self) -> None:
        db_path = Path(self.path)
        if db_path.parent and str(db_path.parent) != ".":
            db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.path) as db:
            await db.execute("PRAGMA foreign_keys=OFF")
            await db.executescript(SCHEMA)
            await self._migrate_users_table(db)
            await self._migrate_conversations_table(db)
            await self._migrate_chat_messages_table(db)
            await self._migrate_simple_add_columns(db, "business_profiles", BUSINESS_PROFILE_ADD_COLUMNS)
            await self._migrate_simple_add_columns(db, "feedback", FEEDBACK_ADD_COLUMNS)
            await db.executescript(INDEXES)
            await db.commit()
            await db.execute("PRAGMA foreign_keys=ON")

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
                    telegram_id INTEGER UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    plan TEXT DEFAULT 'free',
                    daily_limit INTEGER DEFAULT 20,
                    bonus_requests INTEGER DEFAULT 0,
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
                    last_seen_at TEXT
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
                    telegram_user_id, telegram_id, username, first_name, last_name, language_code,
                    plan, daily_limit, bonus_requests, referral_code, referred_by, onboarding_completed,
                    free_limit, monthly_limit, subscription_started_at,
                    subscription_until, unlimited_access, blocked, admin_note, access_updated_at,
                    created_at, updated_at, last_seen_at
                )
                SELECT
                    {telegram_user_expr},
                    {telegram_id_expr},
                    {expr("username")},
                    {expr("first_name")},
                    {expr("last_name")},
                    {expr("language_code")},
                    {expr("plan", "'free'")},
                    {expr("daily_limit", "20")},
                    {expr("bonus_requests", "0")},
                    {expr("referral_code")},
                    {expr("referred_by")},
                    {expr("onboarding_completed", "0")},
                    {expr("free_limit", "15")},
                    {expr("monthly_limit")},
                    {expr("subscription_started_at")},
                    {expr("subscription_until")},
                    {expr("unlimited_access", "0")},
                    {expr("blocked", "0")},
                    {expr("admin_note")},
                    {expr("access_updated_at")},
                    {expr("created_at", repr(now))},
                    {expr("updated_at", expr("created_at", repr(now)))},
                    {expr("last_seen_at", expr("updated_at", expr("created_at", repr(now))))}
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

    async def ensure_user(self, telegram_id: int) -> None:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO users (telegram_user_id, telegram_id, referral_code, created_at, updated_at, last_seen_at)
                VALUES (?, ?, ?, ?, ?, ?)
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
    ) -> None:
        now = utc_now_iso()
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO users (
                    telegram_user_id, telegram_id, username, first_name, last_name,
                    language_code, referral_code, created_at, updated_at, last_seen_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(telegram_user_id) DO UPDATE SET
                    telegram_id=excluded.telegram_id,
                    username=excluded.username,
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    language_code=COALESCE(excluded.language_code, users.language_code),
                    referral_code=COALESCE(users.referral_code, excluded.referral_code),
                    updated_at=excluded.updated_at,
                    last_seen_at=excluded.last_seen_at
                """,
                (
                    tg_text_id(telegram_id),
                    telegram_id,
                    username,
                    first_name,
                    last_name,
                    language_code,
                    referral_code_for(telegram_id),
                    now,
                    now,
                    now,
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
        free_limit = daily_limit + bonus_requests
        monthly_limit = profile.get("monthly_limit")
        monthly_limit = int(monthly_limit) if monthly_limit is not None else int(monthly_limit_default)

        subscription_started_at = parse_iso_datetime(profile.get("subscription_started_at"))
        subscription_until = parse_iso_datetime(profile.get("subscription_until"))
        subscription_active = bool(subscription_until and subscription_until >= now)

        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        paid_period_start = month_start
        if subscription_started_at and subscription_started_at > paid_period_start:
            paid_period_start = subscription_started_at

        used_total = await self.count_requests_total(telegram_id)
        used_period = await self.count_requests_since(telegram_id, paid_period_start.isoformat())
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        used_today = await self.count_requests_since(telegram_id, day_start.isoformat())

        blocked = bool(profile.get("blocked")) or raw_plan == "blocked"
        unlimited = bool(profile.get("unlimited_access")) or raw_plan == "unlimited"

        current_limit: int | None
        used_for_limit: int
        remaining: int | None
        plan = "free"
        status = "free_trial"
        status_label = "Пробный доступ"
        denial_reason = ""

        if blocked:
            plan = "blocked"
            status = "blocked"
            status_label = "Доступ отключен"
            current_limit = 0
            used_for_limit = used_total
            remaining = 0
            can_request = False
            denial_reason = "Доступ к боту отключен администратором."
        elif unlimited:
            plan = "unlimited"
            status = "active"
            status_label = "Unlimited"
            current_limit = None
            used_for_limit = used_period
            remaining = None
            can_request = True
        elif subscription_active:
            plan = "subscriber"
            status = "active"
            status_label = "Подписка активна"
            current_limit = None if monthly_limit <= 0 else monthly_limit
            used_for_limit = used_period
            remaining = None if current_limit is None else max(current_limit - used_for_limit, 0)
            can_request = current_limit is None or used_for_limit < current_limit
            if not can_request:
                denial_reason = (
                    f"Месячный лимит подписки исчерпан: {monthly_limit} запросов. "
                    "Напишите администратору для расширения лимита."
                )
        else:
            status = "expired" if subscription_until else "free_trial"
            status_label = "Free" if not subscription_until else "Подписка истекла"
            current_limit = free_limit
            used_for_limit = used_today
            remaining = max(free_limit - used_today, 0)
            can_request = used_today < free_limit
            if not can_request:
                denial_reason = (
                    f"Дневной лимит исчерпан: {free_limit} запросов. "
                    "Попробуйте завтра или перейдите на платный тариф."
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
            "monthly_limit": monthly_limit,
            "current_limit": current_limit,
            "remaining": remaining,
            "used_today": used_today,
            "used_total": used_total,
            "used_period": used_for_limit,
            "subscription_started_at": profile.get("subscription_started_at"),
            "subscription_until": profile.get("subscription_until"),
            "unlimited": unlimited,
            "blocked": blocked,
            "admin_note": profile.get("admin_note"),
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
        }
        data = {key: (str(payload.get(key)).strip() if payload.get(key) is not None else None) for key in allowed}
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO business_profiles (
                    telegram_user_id, user_type, main_goal, business_name, niche, marketplace,
                    target_audience, average_price, description, main_problem, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                "chat_messages_today": await scalar("SELECT COUNT(*) FROM chat_messages WHERE created_at >= ?", (day_start,)),
                "tool_runs_today": await scalar("SELECT COUNT(*) FROM tool_runs WHERE created_at >= ?", (day_start,)),
                "popular_tools": popular_tools,
                "saved_results_total": await scalar("SELECT COUNT(*) FROM saved_results"),
                "feedback_negative_count": await scalar("SELECT COUNT(*) FROM feedback WHERE rating < 0"),
                "errors_today": await scalar("SELECT COUNT(*) FROM error_logs WHERE created_at >= ?", (day_start,)),
                "active_users_today": await scalar("SELECT COUNT(DISTINCT telegram_user_id) FROM usage_logs WHERE created_at >= ?", (day_start,)),
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
