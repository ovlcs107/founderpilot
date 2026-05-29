from __future__ import annotations

import time
from collections import defaultdict, deque
from datetime import datetime, timezone

from app.config import Settings
from app.db import Database


class RateLimitError(RuntimeError):
    pass


class RateLimiter:
    """Per-user minute limiter plus product access checks from SQLite."""

    def __init__(self, settings: Settings, db: Database) -> None:
        self.settings = settings
        self.db = db
        self._minute_hits: dict[int, deque[float]] = defaultdict(deque)

    async def check(self, telegram_id: int, estimated_credits: int = 1) -> dict:
        now = time.time()
        hits = self._minute_hits[telegram_id]
        while hits and now - hits[0] > 60:
            hits.popleft()

        if len(hits) >= self.settings.per_minute_limit:
            raise RateLimitError(
                f"Слишком много запросов за минуту. Лимит: {self.settings.per_minute_limit}/мин. Повторите чуть позже."
            )

        access = await self.db.get_access_state(
            telegram_id,
            free_limit_default=self.settings.free_trial_requests,
            monthly_limit_default=self.settings.free_monthly_credits,
            now=datetime.now(timezone.utc),
        )
        if not access["can_request"]:
            raise RateLimitError(str(access["denial_reason"]))
        remaining = access.get("remaining")
        if remaining is not None and int(estimated_credits or 1) > int(remaining):
            raise RateLimitError(
                f"Недостаточно кредитов для этого запроса. Нужно примерно {int(estimated_credits or 1)}, осталось {remaining}."
            )

        hits.append(now)
        return access
