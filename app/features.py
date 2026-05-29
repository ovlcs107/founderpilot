from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import Any
from uuid import uuid4

import aiosqlite


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def ip_hash(ip: str, secret: str) -> str:
    clean = (ip or "unknown").split(",")[0].strip()
    return hashlib.sha256(f"{secret}:{clean}".encode("utf-8")).hexdigest()


def ip_prefix_hash(ip: str, secret: str) -> str:
    clean = (ip or "unknown").split(",")[0].strip()
    parts = clean.split(".")
    if len(parts) == 4:
        clean = ".".join(parts[:3]) + ".0/24"
    return hashlib.sha256(f"{secret}:prefix:{clean}".encode("utf-8")).hexdigest()


FEATURE_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    telegram_user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    niche TEXT,
    marketplace TEXT,
    target_audience TEXT,
    description TEXT,
    tone TEXT,
    is_active INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_projects_user_active
ON projects(telegram_user_id, is_active, updated_at);

CREATE TABLE IF NOT EXISTS project_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    project_id TEXT,
    category TEXT DEFAULT 'general',
    key TEXT,
    value TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    source TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_project_memory_user_project
ON project_memory(telegram_user_id, project_id, category, updated_at);

CREATE TABLE IF NOT EXISTS user_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_user_templates_user
ON user_templates(telegram_user_id, category, updated_at);

CREATE TABLE IF NOT EXISTS credit_pack_orders (
    id TEXT PRIMARY KEY,
    telegram_user_id TEXT NOT NULL,
    pack_key TEXT NOT NULL,
    credits INTEGER NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'RUB',
    status TEXT NOT NULL DEFAULT 'created',
    provider TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS abuse_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_user_id TEXT,
    ip_hash TEXT,
    ip_prefix_hash TEXT,
    fingerprint_hash TEXT,
    path TEXT,
    event_type TEXT NOT NULL,
    risk_score INTEGER DEFAULT 0,
    metadata_json TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_abuse_ip_created
ON abuse_events(ip_hash, created_at);

CREATE INDEX IF NOT EXISTS idx_abuse_user_created
ON abuse_events(telegram_user_id, created_at);

CREATE TABLE IF NOT EXISTS notification_preferences (
    telegram_user_id TEXT PRIMARY KEY,
    low_credits INTEGER NOT NULL DEFAULT 1,
    subscription_reminders INTEGER NOT NULL DEFAULT 1,
    product_updates INTEGER NOT NULL DEFAULT 0,
    weekly_digest INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);


CREATE TABLE IF NOT EXISTS organizations (
    id TEXT PRIMARY KEY,
    owner_telegram_user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    slug TEXT,
    description TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_organizations_owner
ON organizations(owner_telegram_user_id, updated_at);

CREATE TABLE IF NOT EXISTS organization_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    organization_id TEXT NOT NULL,
    telegram_user_id TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    status TEXT NOT NULL DEFAULT 'active',
    limited_access INTEGER NOT NULL DEFAULT 1,
    invited_by TEXT,
    joined_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(organization_id, telegram_user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_members_user
ON organization_members(telegram_user_id, status, updated_at);

CREATE INDEX IF NOT EXISTS idx_org_members_org
ON organization_members(organization_id, status, updated_at);

CREATE TABLE IF NOT EXISTS organization_invites (
    token TEXT PRIMARY KEY,
    organization_id TEXT NOT NULL,
    inviter_telegram_user_id TEXT NOT NULL,
    invited_username TEXT NOT NULL,
    invited_telegram_user_id TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    accepted_at TEXT,
    expires_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_org_invites_username
ON organization_invites(invited_username, status, created_at);

CREATE INDEX IF NOT EXISTS idx_org_invites_user
ON organization_invites(invited_telegram_user_id, status, created_at);
"""


async def init_features(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(FEATURE_SCHEMA)
        # Small, safe migrations for older deployments.
        cols = await _columns(db, "users")
        if "purchased_credits" not in cols:
            await db.execute("ALTER TABLE users ADD COLUMN purchased_credits INTEGER DEFAULT 0")
        await db.commit()


async def _columns(db: aiosqlite.Connection, table: str) -> set[str]:
    cur = await db.execute(f"PRAGMA table_info({table})")
    rows = await cur.fetchall()
    return {str(row[1]) for row in rows}


class FeatureStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    async def list_projects(self, telegram_id: int) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM projects WHERE telegram_user_id = ? ORDER BY is_active DESC, updated_at DESC",
                (str(telegram_id),),
            )
            return [dict(row) for row in await cur.fetchall()]

    async def create_project(self, telegram_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        now = utc_now()
        project_id = f"prj_{uuid4().hex[:16]}"
        name = str(payload.get("name") or payload.get("business_name") or "Новый проект").strip()[:120]
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute("SELECT COUNT(*) FROM projects WHERE telegram_user_id = ?", (str(telegram_id),))
            count = int((await cur.fetchone())[0])
            is_active = 1 if count == 0 or payload.get("is_active") else 0
            if is_active:
                await db.execute("UPDATE projects SET is_active = 0 WHERE telegram_user_id = ?", (str(telegram_id),))
            await db.execute(
                """
                INSERT INTO projects(id, telegram_user_id, name, niche, marketplace, target_audience, description, tone, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    project_id,
                    str(telegram_id),
                    name,
                    payload.get("niche"),
                    payload.get("marketplace"),
                    payload.get("target_audience"),
                    payload.get("description"),
                    payload.get("tone"),
                    is_active,
                    now,
                    now,
                ),
            )
            await db.commit()
        return await self.get_project(telegram_id, project_id) or {"id": project_id, "name": name}

    async def get_project(self, telegram_id: int, project_id: str) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM projects WHERE telegram_user_id = ? AND id = ?",
                (str(telegram_id), str(project_id)),
            )
            row = await cur.fetchone()
            return dict(row) if row else None

    async def get_active_project(self, telegram_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT * FROM projects
                WHERE telegram_user_id = ?
                ORDER BY is_active DESC, updated_at DESC
                LIMIT 1
                """,
                (str(telegram_id),),
            )
            row = await cur.fetchone()
            return dict(row) if row else None

    async def update_project(self, telegram_id: int, project_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        allowed = ["name", "niche", "marketplace", "target_audience", "description", "tone"]
        updates: list[str] = []
        values: list[Any] = []
        for key in allowed:
            if key in payload:
                updates.append(f"{key} = ?")
                values.append(payload.get(key))
        if payload.get("is_active") is True:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("UPDATE projects SET is_active = 0 WHERE telegram_user_id = ?", (str(telegram_id),))
                await db.execute(
                    "UPDATE projects SET is_active = 1, updated_at = ? WHERE telegram_user_id = ? AND id = ?",
                    (utc_now(), str(telegram_id), str(project_id)),
                )
                await db.commit()
        if updates:
            updates.append("updated_at = ?")
            values.append(utc_now())
            values.extend([str(telegram_id), str(project_id)])
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    f"UPDATE projects SET {', '.join(updates)} WHERE telegram_user_id = ? AND id = ?",
                    tuple(values),
                )
                await db.commit()
        return await self.get_project(telegram_id, project_id)

    async def delete_project(self, telegram_id: int, project_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "DELETE FROM projects WHERE telegram_user_id = ? AND id = ?",
                (str(telegram_id), str(project_id)),
            )
            await db.execute(
                "DELETE FROM project_memory WHERE telegram_user_id = ? AND project_id = ?",
                (str(telegram_id), str(project_id)),
            )
            await db.commit()
            return cur.rowcount > 0

    async def list_memory(self, telegram_id: int, project_id: str | None = None) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if project_id:
                cur = await db.execute(
                    "SELECT * FROM project_memory WHERE telegram_user_id = ? AND project_id = ? ORDER BY updated_at DESC LIMIT 100",
                    (str(telegram_id), str(project_id)),
                )
            else:
                cur = await db.execute(
                    "SELECT * FROM project_memory WHERE telegram_user_id = ? ORDER BY updated_at DESC LIMIT 100",
                    (str(telegram_id),),
                )
            return [dict(row) for row in await cur.fetchall()]

    async def add_memory(self, telegram_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        now = utc_now()
        project_id = payload.get("project_id")
        if not project_id:
            active = await self.get_active_project(telegram_id)
            project_id = active.get("id") if active else None
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                """
                INSERT INTO project_memory(telegram_user_id, project_id, category, key, value, confidence, source, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(telegram_id),
                    project_id,
                    payload.get("category") or "general",
                    payload.get("key"),
                    str(payload.get("value") or payload.get("content") or "").strip(),
                    float(payload.get("confidence") or 1.0),
                    payload.get("source") or "manual",
                    now,
                    now,
                ),
            )
            await db.commit()
            memory_id = cur.lastrowid
            db.row_factory = aiosqlite.Row
            cur2 = await db.execute("SELECT * FROM project_memory WHERE id = ?", (memory_id,))
            row = await cur2.fetchone()
            return dict(row)

    async def delete_memory(self, telegram_id: int, memory_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "DELETE FROM project_memory WHERE telegram_user_id = ? AND id = ?",
                (str(telegram_id), memory_id),
            )
            await db.commit()
            return cur.rowcount > 0

    async def project_context_text(self, telegram_id: int) -> str:
        project = await self.get_active_project(telegram_id)
        memory = await self.list_memory(telegram_id, project.get("id") if project else None)
        lines: list[str] = []
        if project:
            labels = {
                "name": "Проект",
                "niche": "Ниша",
                "marketplace": "Маркетплейс",
                "target_audience": "ЦА",
                "description": "Описание проекта",
                "tone": "Тон общения",
            }
            for key, label in labels.items():
                if project.get(key):
                    lines.append(f"{label}: {project[key]}")
        for item in memory[:20]:
            value = str(item.get("value") or "").strip()
            if value:
                prefix = str(item.get("category") or "memory")
                key = str(item.get("key") or "").strip()
                lines.append(f"Память / {prefix}{' / ' + key if key else ''}: {value}")
        return "\n".join(lines)

    async def list_templates(self, telegram_id: int, category: str | None = None) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if category:
                cur = await db.execute(
                    "SELECT * FROM user_templates WHERE telegram_user_id = ? AND category = ? ORDER BY updated_at DESC",
                    (str(telegram_id), category),
                )
            else:
                cur = await db.execute(
                    "SELECT * FROM user_templates WHERE telegram_user_id = ? ORDER BY updated_at DESC",
                    (str(telegram_id),),
                )
            return [dict(row) for row in await cur.fetchall()]

    async def create_template(self, telegram_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        now = utc_now()
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                """
                INSERT INTO user_templates(telegram_user_id, title, category, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(telegram_id),
                    str(payload.get("title") or "Шаблон")[:120],
                    str(payload.get("category") or "general")[:80],
                    str(payload.get("content") or ""),
                    now,
                    now,
                ),
            )
            await db.commit()
            db.row_factory = aiosqlite.Row
            cur2 = await db.execute("SELECT * FROM user_templates WHERE id = ?", (cur.lastrowid,))
            return dict(await cur2.fetchone())

    async def delete_template(self, telegram_id: int, template_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "DELETE FROM user_templates WHERE telegram_user_id = ? AND id = ?",
                (str(telegram_id), template_id),
            )
            await db.commit()
            return cur.rowcount > 0

    def credit_packs(self) -> list[dict[str, Any]]:
        return [
            {"key": "credits_1000", "title": "1 000 кредитов", "credits": 1000, "amount": 199, "currency": "RUB"},
            {"key": "credits_5000", "title": "5 000 кредитов", "credits": 5000, "amount": 799, "currency": "RUB", "popular": True},
            {"key": "credits_20000", "title": "20 000 кредитов", "credits": 20000, "amount": 2490, "currency": "RUB"},
        ]

    async def create_credit_pack_order(self, telegram_id: int, pack_key: str, provider: str | None = None) -> dict[str, Any]:
        pack = next((p for p in self.credit_packs() if p["key"] == pack_key), None)
        if not pack:
            raise ValueError("Пакет кредитов не найден.")
        now = utc_now()
        order_id = f"cp_{uuid4().hex[:18]}"
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO credit_pack_orders(id, telegram_user_id, pack_key, credits, amount, currency, status, provider, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 'created', ?, ?, ?)
                """,
                (order_id, str(telegram_id), pack_key, pack["credits"], pack["amount"], pack["currency"], provider, now, now),
            )
            await db.commit()
        return {"ok": True, "order_id": order_id, "pack": pack, "status": "created"}

    async def grant_credit_pack(self, telegram_id: int, order_id: str, admin_note: str = "manual") -> dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM credit_pack_orders WHERE id = ? AND telegram_user_id = ?",
                (order_id, str(telegram_id)),
            )
            order = await cur.fetchone()
            if not order:
                raise ValueError("Заказ пакета не найден.")
            if order["status"] == "paid":
                return {"ok": True, "status": "already_paid", "credits": int(order["credits"])}
            credits = int(order["credits"])
            await db.execute(
                "UPDATE users SET purchased_credits = COALESCE(purchased_credits, 0) + ?, updated_at = ? WHERE telegram_id = ? OR telegram_user_id = ?",
                (credits, utc_now(), telegram_id, str(telegram_id)),
            )
            await db.execute(
                "UPDATE credit_pack_orders SET status = 'paid', updated_at = ? WHERE id = ?",
                (utc_now(), order_id),
            )
            await db.execute(
                """
                INSERT INTO credit_transactions(telegram_user_id, transaction_type, amount, reason, metadata_json, created_at)
                VALUES (?, 'grant', ?, ?, ?, ?)
                """,
                (str(telegram_id), credits, "credit_pack", json_dumps({"order_id": order_id, "note": admin_note}), utc_now()),
            )
            await db.commit()
            return {"ok": True, "status": "paid", "credits": credits}

    async def analytics_summary(self, telegram_id: int) -> dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            async def scalar(sql: str, params: tuple[Any, ...] = ()) -> int:
                cur = await db.execute(sql, params)
                row = await cur.fetchone()
                return int(row[0] or 0)
            return {
                "projects": await scalar("SELECT COUNT(*) FROM projects WHERE telegram_user_id = ?", (str(telegram_id),)),
                "memory_items": await scalar("SELECT COUNT(*) FROM project_memory WHERE telegram_user_id = ?", (str(telegram_id),)),
                "templates": await scalar("SELECT COUNT(*) FROM user_templates WHERE telegram_user_id = ?", (str(telegram_id),)),
                "saved_results": await scalar("SELECT COUNT(*) FROM saved_results WHERE telegram_user_id = ?", (str(telegram_id),)),
                "tool_runs": await scalar("SELECT COUNT(*) FROM tool_runs WHERE telegram_user_id = ?", (str(telegram_id),)),
                "chat_messages": await scalar("SELECT COUNT(*) FROM chat_messages cm JOIN conversations c ON c.id = cm.conversation_id WHERE c.telegram_user_id = ?", (str(telegram_id),)),
                "credits_charged": await scalar("SELECT COALESCE(SUM(credits_charged),0) FROM ai_usage_events WHERE telegram_user_id = ? AND status = 'success'", (str(telegram_id),)),
            }

    async def admin_overview(self) -> dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            async def scalar(sql: str, params: tuple[Any, ...] = ()) -> int:
                cur = await db.execute(sql, params)
                row = await cur.fetchone()
                return int(row[0] or 0)
            return {
                "users": await scalar("SELECT COUNT(*) FROM users"),
                "projects": await scalar("SELECT COUNT(*) FROM projects"),
                "payments": await scalar("SELECT COUNT(*) FROM payments"),
                "paid_orders": await scalar("SELECT COUNT(*) FROM billing_orders WHERE status IN ('paid','succeeded')"),
                "tool_runs": await scalar("SELECT COUNT(*) FROM tool_runs"),
                "saved_results": await scalar("SELECT COUNT(*) FROM saved_results"),
                "abuse_events_24h": await scalar("SELECT COUNT(*) FROM abuse_events WHERE created_at >= ?", ((datetime.now(timezone.utc)-timedelta(days=1)).isoformat(),)),
            }

    async def admin_users(self, limit: int = 50) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT telegram_id, username, first_name, plan, monthly_limit, daily_limit, purchased_credits, created_at, last_seen_at FROM users ORDER BY id DESC LIMIT ?",
                (max(1, min(int(limit), 200)),),
            )
            return [dict(row) for row in await cur.fetchall()]


    async def user_plan(self, telegram_id: int) -> dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT telegram_id, telegram_user_id, username, first_name, plan, subscription_until, subscription_expires_at, unlimited_access FROM users WHERE telegram_id = ? OR telegram_user_id = ?",
                (telegram_id, str(telegram_id)),
            )
            row = await cur.fetchone()
            return dict(row) if row else {}

    async def can_manage_organization(self, telegram_id: int) -> tuple[bool, str]:
        user = await self.user_plan(telegram_id)
        plan = str(user.get("plan") or "free").lower()
        if plan == "business" or bool(user.get("unlimited_access")):
            return True, "ok"
        return False, "Создание компании доступно только на тарифе Business."

    async def list_organizations(self, telegram_id: int, username: str | None = None) -> dict[str, Any]:
        clean_username = (username or "").strip().lstrip("@").lower()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            owned_cur = await db.execute(
                "SELECT * FROM organizations WHERE owner_telegram_user_id = ? ORDER BY updated_at DESC",
                (str(telegram_id),),
            )
            owned = [dict(row) for row in await owned_cur.fetchall()]

            member_cur = await db.execute(
                """
                SELECT o.*, om.role, om.limited_access, om.joined_at, om.status AS member_status
                FROM organization_members om
                JOIN organizations o ON o.id = om.organization_id
                WHERE om.telegram_user_id = ? AND om.status = 'active'
                ORDER BY om.updated_at DESC
                """,
                (str(telegram_id),),
            )
            memberships = [dict(row) for row in await member_cur.fetchall()]

            pending: list[dict[str, Any]] = []
            if clean_username:
                inv_cur = await db.execute(
                    """
                    SELECT oi.*, o.title AS organization_title, o.owner_telegram_user_id
                    FROM organization_invites oi
                    JOIN organizations o ON o.id = oi.organization_id
                    WHERE oi.status = 'pending' AND (oi.invited_telegram_user_id = ? OR lower(oi.invited_username) = ?)
                    ORDER BY oi.created_at DESC
                    """,
                    (str(telegram_id), clean_username),
                )
                pending = [dict(row) for row in await inv_cur.fetchall()]
            else:
                inv_cur = await db.execute(
                    """
                    SELECT oi.*, o.title AS organization_title, o.owner_telegram_user_id
                    FROM organization_invites oi
                    JOIN organizations o ON o.id = oi.organization_id
                    WHERE oi.status = 'pending' AND oi.invited_telegram_user_id = ?
                    ORDER BY oi.created_at DESC
                    """,
                    (str(telegram_id),),
                )
                pending = [dict(row) for row in await inv_cur.fetchall()]

        active = memberships[0] if memberships else None
        return {"owned": owned, "memberships": memberships, "active": active, "pending_invites": pending}

    async def create_organization(self, telegram_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        allowed, reason = await self.can_manage_organization(telegram_id)
        if not allowed:
            raise PermissionError(reason)
        now = utc_now()
        org_id = f"org_{uuid4().hex[:16]}"
        title = str(payload.get("title") or payload.get("name") or "Моя компания").strip()[:120]
        description = str(payload.get("description") or "").strip()[:1000]
        slug = "".join(ch.lower() for ch in title if ch.isalnum())[:40] or org_id
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO organizations(id, owner_telegram_user_id, title, slug, description, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (org_id, str(telegram_id), title, slug, description, now, now),
            )
            await db.execute(
                """
                INSERT OR REPLACE INTO organization_members(organization_id, telegram_user_id, role, status, limited_access, invited_by, joined_at, created_at, updated_at)
                VALUES (?, ?, 'owner', 'active', 0, ?, ?, ?, ?)
                """,
                (org_id, str(telegram_id), str(telegram_id), now, now, now),
            )
            await db.commit()
        return {"id": org_id, "title": title, "slug": slug, "description": description, "role": "owner"}

    async def list_organization_members(self, telegram_id: int, organization_id: str | None = None) -> list[dict[str, Any]]:
        org_id = organization_id
        if not org_id:
            orgs = (await self.list_organizations(telegram_id)).get("owned", [])
            org_id = orgs[0].get("id") if orgs else None
        if not org_id:
            return []
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur_owner = await db.execute(
                "SELECT id FROM organizations WHERE id = ? AND owner_telegram_user_id = ?",
                (str(org_id), str(telegram_id)),
            )
            if not await cur_owner.fetchone():
                cur_member = await db.execute(
                    "SELECT id FROM organization_members WHERE organization_id = ? AND telegram_user_id = ? AND status = 'active'",
                    (str(org_id), str(telegram_id)),
                )
                if not await cur_member.fetchone():
                    raise PermissionError("Нет доступа к участникам этой организации.")
            cur = await db.execute(
                """
                SELECT om.organization_id, om.telegram_user_id, om.role, om.status, om.limited_access,
                       om.joined_at, u.username, u.first_name, u.last_name, u.photo_url
                FROM organization_members om
                LEFT JOIN users u ON u.telegram_user_id = om.telegram_user_id OR CAST(u.telegram_id AS TEXT) = om.telegram_user_id
                WHERE om.organization_id = ?
                ORDER BY CASE om.role WHEN 'owner' THEN 0 WHEN 'admin' THEN 1 ELSE 2 END, om.created_at ASC
                """,
                (str(org_id),),
            )
            return [dict(row) for row in await cur.fetchall()]

    async def get_organization_for_owner(self, telegram_id: int, organization_id: str) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT * FROM organizations WHERE id = ? AND owner_telegram_user_id = ?",
                (organization_id, str(telegram_id)),
            )
            row = await cur.fetchone()
            return dict(row) if row else None

    async def find_user_by_username(self, username: str) -> dict[str, Any] | None:
        clean_username = username.strip().lstrip("@").lower()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                "SELECT telegram_id, telegram_user_id, username, first_name, plan FROM users WHERE lower(username) = ? ORDER BY id DESC LIMIT 1",
                (clean_username,),
            )
            row = await cur.fetchone()
            return dict(row) if row else None

    async def invite_organization_member(self, telegram_id: int, organization_id: str, username: str) -> dict[str, Any]:
        org = await self.get_organization_for_owner(telegram_id, organization_id)
        if not org:
            raise PermissionError("Приглашать людей может только владелец компании.")
        clean_username = username.strip().lstrip("@").lower()
        if not clean_username:
            raise ValueError("Укажите username Telegram.")
        invited_user = await self.find_user_by_username(clean_username)
        now_dt = datetime.now(timezone.utc)
        now = now_dt.isoformat()
        expires_at = (now_dt + timedelta(days=14)).isoformat()
        token = f"inv_{uuid4().hex}"
        invited_tg = str(invited_user.get("telegram_id")) if invited_user and invited_user.get("telegram_id") else None
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO organization_invites(token, organization_id, inviter_telegram_user_id, invited_username, invited_telegram_user_id, status, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
                """,
                (token, organization_id, str(telegram_id), clean_username, invited_tg, now, expires_at),
            )
            await db.commit()
        return {
            "token": token,
            "organization_id": organization_id,
            "organization_title": org.get("title"),
            "invited_username": clean_username,
            "invited_telegram_user_id": invited_tg,
            "status": "pending",
            "expires_at": expires_at,
        }

    async def pending_invites(self, telegram_id: int, username: str | None = None) -> list[dict[str, Any]]:
        return (await self.list_organizations(telegram_id, username)).get("pending_invites", [])

    async def decline_organization_invite(self, telegram_id: int, username: str | None, token: str) -> dict[str, Any]:
        clean_username = (username or "").strip().lstrip("@").lower()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM organization_invites WHERE token = ? AND status = 'pending'", (token,))
            invite = await cur.fetchone()
            if not invite:
                raise ValueError("Приглашение не найдено или уже использовано.")
            invite_dict = dict(invite)
            invited_tg = invite_dict.get("invited_telegram_user_id")
            invited_username = str(invite_dict.get("invited_username") or "").lower()
            if invited_tg and str(invited_tg) != str(telegram_id):
                raise PermissionError("Это приглашение предназначено для другого пользователя.")
            if (not invited_tg) and clean_username and invited_username != clean_username:
                raise PermissionError("Это приглашение предназначено для другого username.")
            await db.execute("UPDATE organization_invites SET status = 'declined' WHERE token = ?", (token,))
            await db.commit()
        return {"ok": True, "status": "declined"}

    async def accept_organization_invite(self, telegram_id: int, username: str | None, token: str) -> dict[str, Any]:
        clean_username = (username or "").strip().lstrip("@").lower()
        now = utc_now()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute(
                """
                SELECT oi.*, o.title AS organization_title, o.owner_telegram_user_id
                FROM organization_invites oi
                JOIN organizations o ON o.id = oi.organization_id
                WHERE oi.token = ? AND oi.status = 'pending'
                """,
                (token,),
            )
            invite = await cur.fetchone()
            if not invite:
                raise ValueError("Приглашение не найдено или уже использовано.")
            invite_dict = dict(invite)
            invited_tg = invite_dict.get("invited_telegram_user_id")
            invited_username = str(invite_dict.get("invited_username") or "").lower()
            if invited_tg and str(invited_tg) != str(telegram_id):
                raise PermissionError("Это приглашение предназначено для другого пользователя.")
            if (not invited_tg) and clean_username and invited_username != clean_username:
                raise PermissionError("Это приглашение предназначено для другого username.")

            await db.execute(
                """
                INSERT OR REPLACE INTO organization_members(organization_id, telegram_user_id, role, status, limited_access, invited_by, joined_at, created_at, updated_at)
                VALUES (?, ?, 'member', 'active', 1, ?, ?, ?, ?)
                """,
                (invite_dict["organization_id"], str(telegram_id), invite_dict["inviter_telegram_user_id"], now, now, now),
            )
            await db.execute(
                "UPDATE organization_invites SET status = 'accepted', invited_telegram_user_id = ?, accepted_at = ? WHERE token = ?",
                (str(telegram_id), now, token),
            )
            await db.commit()
        return {"ok": True, "organization_id": invite_dict["organization_id"], "organization_title": invite_dict["organization_title"], "role": "member", "limited_access": True}

    async def record_abuse_event(self, *, telegram_id: int | None, ip: str, fingerprint_hash: str | None, path: str, event_type: str, risk_score: int, metadata: dict[str, Any], secret: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO abuse_events(telegram_user_id, ip_hash, ip_prefix_hash, fingerprint_hash, path, event_type, risk_score, metadata_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(telegram_id) if telegram_id else None,
                    ip_hash(ip, secret),
                    ip_prefix_hash(ip, secret),
                    fingerprint_hash,
                    path,
                    event_type,
                    int(risk_score),
                    json_dumps(metadata),
                    utc_now(),
                ),
            )
            await db.commit()

    async def ip_event_count(self, ip: str, secret: str, minutes: int = 10) -> int:
        since = (datetime.now(timezone.utc) - timedelta(minutes=minutes)).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "SELECT COUNT(*) FROM abuse_events WHERE ip_hash = ? AND created_at >= ?",
                (ip_hash(ip, secret), since),
            )
            row = await cur.fetchone()
            return int(row[0] or 0)

    async def notification_preferences(self, telegram_id: int) -> dict[str, Any]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cur = await db.execute("SELECT * FROM notification_preferences WHERE telegram_user_id = ?", (str(telegram_id),))
            row = await cur.fetchone()
            if row:
                return dict(row)
            now = utc_now()
            await db.execute(
                "INSERT INTO notification_preferences(telegram_user_id, updated_at) VALUES (?, ?)",
                (str(telegram_id), now),
            )
            await db.commit()
            return {"telegram_user_id": str(telegram_id), "low_credits": 1, "subscription_reminders": 1, "product_updates": 0, "weekly_digest": 0, "updated_at": now}

    async def update_notification_preferences(self, telegram_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        await self.notification_preferences(telegram_id)
        allowed = ["low_credits", "subscription_reminders", "product_updates", "weekly_digest"]
        updates = []
        values = []
        for key in allowed:
            if key in payload:
                updates.append(f"{key} = ?")
                values.append(1 if bool(payload.get(key)) else 0)
        if updates:
            updates.append("updated_at = ?")
            values.append(utc_now())
            values.append(str(telegram_id))
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(f"UPDATE notification_preferences SET {', '.join(updates)} WHERE telegram_user_id = ?", tuple(values))
                await db.commit()
        return await self.notification_preferences(telegram_id)
