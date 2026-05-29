from __future__ import annotations

"""Small async database adapter used by FounderPilot.

The project originally used aiosqlite directly.  This module keeps the tiny
subset of the aiosqlite API that the codebase uses, while allowing production
Railway deployments to use PostgreSQL through asyncpg.

Supported modes:
- SQLite: DATABASE_PATH=founderpilot.sqlite3
- PostgreSQL: DATABASE_URL=postgresql://...  (or DATABASE_PATH=postgresql://...)
"""

import asyncio
import os
import re
from collections.abc import Iterator, Mapping
from typing import Any

import aiosqlite as _aiosqlite

Row = _aiosqlite.Row
Connection = Any

_POSTGRES_PREFIXES = ("postgres://", "postgresql://")
_POOLS: dict[str, Any] = {}
_POOL_LOCK = asyncio.Lock()

# Tables with an integer identity primary key named "id".  For PostgreSQL we
# transparently add RETURNING id to INSERTs for these tables so cursor.lastrowid
# continues to work in the existing code.
_SERIAL_ID_TABLES = {
    "users",
    "ai_requests",
    "access_events",
    "chat_messages",
    "tool_runs",
    "usage_logs",
    "saved_results",
    "feedback",
    "referrals",
    "subscriptions",
    "payments",
    "payment_events",
    "credit_transactions",
    "ai_usage_events",
    "error_logs",
    "project_memory",
    "user_templates",
    "abuse_events",
    "notification_events",
    "organization_members",
    "support_messages",
    "support_group_bridge_messages",
    "ai_response_feedback",
}


def normalize_database_url(value: str | None) -> str:
    """Return a clean DB setting and prefer DATABASE_URL when it exists."""
    raw = (os.getenv("DATABASE_URL") or value or "founderpilot.sqlite3").strip()
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        raw = raw[1:-1].strip()
    return raw


def is_postgres_dsn(value: str | None) -> bool:
    raw = normalize_database_url(value).lower()
    return raw.startswith(_POSTGRES_PREFIXES)


def connect(database: str):
    database = normalize_database_url(database)
    if is_postgres_dsn(database):
        return _PostgresConnectContext(database)
    return _aiosqlite.connect(database)


class _PgRow(Mapping[str, Any]):
    def __init__(self, keys: list[str], values: list[Any]) -> None:
        self._keys = keys
        self._values = values
        self._data = dict(zip(keys, values, strict=False))

    @classmethod
    def from_record(cls, record: Any) -> "_PgRow":
        keys = list(record.keys())
        return cls(keys, [record[key] for key in keys])

    def __getitem__(self, key: str | int) -> Any:
        if isinstance(key, int):
            return self._values[key]
        return self._data[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._keys)

    def __len__(self) -> int:
        return len(self._keys)

    def keys(self):  # type: ignore[override]
        return self._data.keys()

    def items(self):  # type: ignore[override]
        return self._data.items()

    def values(self):  # type: ignore[override]
        return self._data.values()

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def __repr__(self) -> str:
        return repr(self._data)


class _PgCursor:
    def __init__(self, rows: list[_PgRow] | None = None, *, rowcount: int = -1, lastrowid: int | None = None) -> None:
        self._rows = rows or []
        self._index = 0
        self.rowcount = rowcount
        self.lastrowid = lastrowid

    async def fetchone(self) -> _PgRow | None:
        if self._index >= len(self._rows):
            return None
        row = self._rows[self._index]
        self._index += 1
        return row

    async def fetchall(self) -> list[_PgRow]:
        if self._index == 0:
            self._index = len(self._rows)
            return list(self._rows)
        rows = self._rows[self._index :]
        self._index = len(self._rows)
        return rows


class _PostgresConnectContext:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self._conn: _PostgresConnection | None = None

    async def __aenter__(self) -> "_PostgresConnection":
        pool = await _get_pool(self.dsn)
        raw = await pool.acquire()
        self._conn = _PostgresConnection(pool, raw)
        await self._conn._begin()
        return self._conn

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._conn is not None:
            await self._conn._close(exc_type is not None)


async def _get_pool(dsn: str):
    async with _POOL_LOCK:
        pool = _POOLS.get(dsn)
        if pool is not None:
            return pool
        import asyncpg

        pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=int(os.getenv("POSTGRES_POOL_MIN_SIZE", "1")),
            max_size=int(os.getenv("POSTGRES_POOL_MAX_SIZE", "10")),
            command_timeout=float(os.getenv("POSTGRES_COMMAND_TIMEOUT_SECONDS", "60")),
        )
        _POOLS[dsn] = pool
        return pool


class _PostgresConnection:
    def __init__(self, pool: Any, raw: Any) -> None:
        self._pool = pool
        self._raw = raw
        self._tx: Any | None = None
        self.row_factory: Any | None = None

    async def _begin(self) -> None:
        self._tx = self._raw.transaction()
        await self._tx.start()

    async def _close(self, had_error: bool) -> None:
        try:
            if self._tx is not None:
                if had_error:
                    await self._tx.rollback()
                else:
                    await self._tx.commit()
                self._tx = None
        finally:
            await self._pool.release(self._raw)

    async def commit(self) -> None:
        if self._tx is not None:
            await self._tx.commit()
            self._tx = None

    async def rollback(self) -> None:
        if self._tx is not None:
            await self._tx.rollback()
            self._tx = None

    async def executescript(self, script: str) -> None:
        for statement in _split_sql_script(script):
            if statement.strip():
                await self.execute(statement)

    async def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> _PgCursor:
        rewritten, rewritten_params = _rewrite_sql(sql, tuple(params or ()))
        lowered = rewritten.lstrip().lower()
        fetch_expected = lowered.startswith(("select", "with", "show")) or " returning " in lowered
        if fetch_expected:
            records = await self._raw.fetch(rewritten, *rewritten_params)
            rows = [_PgRow.from_record(record) for record in records]
            lastrowid = _extract_lastrowid(rows)
            return _PgCursor(rows, rowcount=len(rows), lastrowid=lastrowid)

        status = await self._raw.execute(rewritten, *rewritten_params)
        return _PgCursor([], rowcount=_parse_rowcount(status), lastrowid=None)


def _parse_rowcount(status: str) -> int:
    if not status:
        return -1
    match = re.search(r"(\d+)$", status)
    return int(match.group(1)) if match else -1


def _extract_lastrowid(rows: list[_PgRow]) -> int | None:
    if not rows:
        return None
    first = rows[0]
    if "id" not in first.keys():
        return None
    try:
        return int(first["id"])
    except Exception:
        return None


def _split_sql_script(script: str) -> list[str]:
    statements: list[str] = []
    buf: list[str] = []
    in_single = False
    in_double = False
    i = 0
    while i < len(script):
        ch = script[i]
        nxt = script[i + 1] if i + 1 < len(script) else ""
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        if ch == ";" and not in_single and not in_double:
            statements.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
    return statements


def _rewrite_sql(sql: str, params: tuple[Any, ...]) -> tuple[str, tuple[Any, ...]]:
    statement = sql.strip().rstrip(";")

    # SQLite runtime toggles. PostgreSQL does not need them.
    if statement.upper().startswith("PRAGMA FOREIGN_KEYS"):
        return "SELECT 1", ()

    pragma = re.fullmatch(r"PRAGMA\s+table_info\(([^)]+)\)", statement, flags=re.IGNORECASE)
    if pragma:
        table = pragma.group(1).strip().strip('"').strip("'")
        return (
            """
            SELECT
                ordinal_position - 1 AS cid,
                column_name AS name,
                data_type AS type,
                CASE WHEN is_nullable = 'NO' THEN 1 ELSE 0 END AS notnull,
                column_default AS dflt_value,
                CASE WHEN constraint_name IS NULL THEN 0 ELSE 1 END AS pk
            FROM (
                SELECT c.ordinal_position, c.column_name, c.data_type, c.is_nullable, c.column_default,
                       kcu.constraint_name
                FROM information_schema.columns c
                LEFT JOIN information_schema.key_column_usage kcu
                  ON kcu.table_schema = c.table_schema
                 AND kcu.table_name = c.table_name
                 AND kcu.column_name = c.column_name
                 AND kcu.constraint_name IN (
                    SELECT tc.constraint_name
                    FROM information_schema.table_constraints tc
                    WHERE tc.table_schema = c.table_schema
                      AND tc.table_name = c.table_name
                      AND tc.constraint_type = 'PRIMARY KEY'
                 )
                WHERE c.table_schema = 'public' AND c.table_name = $1
            ) t
            ORDER BY ordinal_position
            """,
            (table,),
        )

    sqlite_master = "FROM SQLITE_MASTER" in statement.upper()
    if sqlite_master:
        # The codebase only uses this shape to check table existence.
        return (
            "SELECT table_name AS name FROM information_schema.tables WHERE table_schema = 'public' AND table_name = $1",
            tuple(params),
        )

    statement = _rewrite_sqlite_ddl_to_postgres(statement)
    statement = _rewrite_insert_or_ignore(statement)
    statement = _maybe_add_returning_id(statement)
    statement = _convert_qmark_params(statement)
    return statement, params


def _rewrite_sqlite_ddl_to_postgres(sql: str) -> str:
    rewritten = re.sub(
        r"\bINTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT\b",
        "INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY",
        sql,
        flags=re.IGNORECASE,
    )
    rewritten = re.sub(r"lower\(hex\(randomblob\(8\)\)\)", "substr(md5(random()::text), 1, 16)", rewritten, flags=re.IGNORECASE)
    return rewritten


def _rewrite_insert_or_ignore(sql: str) -> str:
    if not re.match(r"\s*INSERT\s+OR\s+IGNORE\s+INTO\b", sql, flags=re.IGNORECASE):
        return sql
    rewritten = re.sub(r"\s*INSERT\s+OR\s+IGNORE\s+INTO\b", "INSERT INTO", sql, count=1, flags=re.IGNORECASE)
    if " ON CONFLICT " not in rewritten.upper():
        rewritten += " ON CONFLICT DO NOTHING"
    return rewritten


def _maybe_add_returning_id(sql: str) -> str:
    lowered = sql.lower()
    if " returning " in lowered:
        return sql
    match = re.match(r"\s*insert\s+into\s+([a-zA-Z_][a-zA-Z0-9_]*)\b", sql, flags=re.IGNORECASE)
    if not match:
        return sql
    table = match.group(1).lower()
    if table in _SERIAL_ID_TABLES:
        return sql + " RETURNING id"
    return sql


def _convert_qmark_params(sql: str) -> str:
    out: list[str] = []
    in_single = False
    in_double = False
    placeholder_index = 1
    i = 0
    while i < len(sql):
        ch = sql[i]
        if ch == "'" and not in_double:
            out.append(ch)
            # SQL escapes a single quote inside string as ''. Keep string state.
            if in_single and i + 1 < len(sql) and sql[i + 1] == "'":
                out.append(sql[i + 1])
                i += 2
                continue
            in_single = not in_single
        elif ch == '"' and not in_single:
            out.append(ch)
            in_double = not in_double
        elif ch == "?" and not in_single and not in_double:
            out.append(f"${placeholder_index}")
            placeholder_index += 1
        else:
            out.append(ch)
        i += 1
    return "".join(out)
