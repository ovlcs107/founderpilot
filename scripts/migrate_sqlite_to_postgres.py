from __future__ import annotations

"""One-time SQLite -> PostgreSQL migration helper.

Usage:
  python scripts/migrate_sqlite_to_postgres.py --sqlite founderpilot.sqlite3 --postgres "$DATABASE_URL"

Run this locally after you download the old SQLite file, or in Railway shell if the
old file is still available. The script initializes the PostgreSQL schema first,
then copies matching tables and columns.
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import aiosqlite

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import Database  # noqa: E402
from app.db_adapter import connect  # noqa: E402
from app.features import init_features  # noqa: E402

SERIAL_ID_TABLES = {
    "users", "ai_requests", "access_events", "chat_messages", "tool_runs", "usage_logs",
    "saved_results", "feedback", "referrals", "subscriptions", "payments", "payment_events",
    "credit_transactions", "ai_usage_events", "error_logs", "project_memory", "user_templates",
    "abuse_events", "notification_events", "organization_members", "support_messages",
    "support_group_bridge_messages",
}


async def sqlite_tables(sqlite_path: str) -> list[str]:
    async with aiosqlite.connect(sqlite_path) as db:
        cur = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        return [str(row[0]) for row in await cur.fetchall()]


async def sqlite_columns(db: aiosqlite.Connection, table: str) -> list[str]:
    cur = await db.execute(f"PRAGMA table_info({table})")
    return [str(row[1]) for row in await cur.fetchall()]


async def pg_columns(pg: Any, table: str) -> list[str]:
    cur = await pg.execute(f"PRAGMA table_info({table})")
    return [str(row[1]) for row in await cur.fetchall()]


async def copy_table(sqlite_path: str, postgres_url: str, table: str) -> int:
    async with aiosqlite.connect(sqlite_path) as src, connect(postgres_url) as dst:
        src.row_factory = aiosqlite.Row
        source_cols = await sqlite_columns(src, table)
        target_cols = await pg_columns(dst, table)
        columns = [col for col in source_cols if col in set(target_cols)]
        if not columns:
            return 0
        select_sql = f"SELECT {', '.join(columns)} FROM {table}"
        rows = await (await src.execute(select_sql)).fetchall()
        if not rows:
            return 0
        placeholders = ", ".join("?" for _ in columns)
        insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
        copied = 0
        for row in rows:
            values = tuple(row[col] for col in columns)
            cur = await dst.execute(insert_sql, values)
            copied += max(0, int(cur.rowcount or 0))
        await dst.commit()
        return copied


async def reset_sequences(postgres_url: str) -> None:
    async with connect(postgres_url) as pg:
        for table in sorted(SERIAL_ID_TABLES):
            try:
                await pg.execute(
                    f"""
                    SELECT setval(
                        pg_get_serial_sequence('{table}', 'id'),
                        GREATEST(COALESCE((SELECT MAX(id) FROM {table}), 1), 1),
                        true
                    )
                    """
                )
            except Exception:
                # Some tables may not exist in older projects. Safe to skip.
                await pg.rollback()
        await pg.commit()


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sqlite", required=True, help="Path to old founderpilot.sqlite3")
    parser.add_argument("--postgres", default=os.getenv("DATABASE_URL") or os.getenv("DATABASE_PATH") or "", help="PostgreSQL DATABASE_URL")
    args = parser.parse_args()
    sqlite_path = str(Path(args.sqlite).expanduser().resolve())
    postgres_url = str(args.postgres or "").strip()
    if not Path(sqlite_path).exists():
        raise SystemExit(f"SQLite file not found: {sqlite_path}")
    if not postgres_url.startswith(("postgres://", "postgresql://")):
        raise SystemExit("Pass PostgreSQL URL via --postgres or DATABASE_URL")

    await Database(postgres_url).init()
    await init_features(postgres_url)

    total = 0
    for table in await sqlite_tables(sqlite_path):
        try:
            copied = await copy_table(sqlite_path, postgres_url, table)
            total += copied
            print(f"{table}: copied {copied}")
        except Exception as exc:  # noqa: BLE001
            print(f"{table}: skipped/failed: {exc}")
    await reset_sequences(postgres_url)
    print(f"Done. Total copied rows: {total}")


if __name__ == "__main__":
    asyncio.run(main())
