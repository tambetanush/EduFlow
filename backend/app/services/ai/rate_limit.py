from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIRateLimitCounter

@dataclass(frozen=True)
class RateLimitRule:
    max_requests: int
    window_seconds: int


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after_seconds: int


class RateLimitViolation(Exception):
    def __init__(self, decision: RateLimitDecision):
        self.decision = decision
        super().__init__(f"Rate limit exceeded. Retry after {decision.retry_after_seconds} seconds.")


class InMemorySlidingWindowRateLimiter:
    """In-memory sliding window limiter suitable for app-level helper usage."""

    def __init__(self) -> None:
        self._events: dict[str, deque[datetime]] = defaultdict(deque)

    def evaluate(
        self,
        *,
        key: str,
        rule: RateLimitRule,
        now: datetime | None = None,
    ) -> RateLimitDecision:
        now = now or datetime.now(timezone.utc)
        window_start = now - timedelta(seconds=rule.window_seconds)
        bucket = self._events[key]

        while bucket and bucket[0] <= window_start:
            bucket.popleft()

        used = len(bucket)
        if used >= rule.max_requests:
            retry_after = int((bucket[0] - window_start).total_seconds()) + 1 if bucket else rule.window_seconds
            return RateLimitDecision(allowed=False, remaining=0, retry_after_seconds=max(retry_after, 1))

        return RateLimitDecision(allowed=True, remaining=rule.max_requests - used - 1, retry_after_seconds=0)

    def consume(
        self,
        *,
        key: str,
        rule: RateLimitRule,
        now: datetime | None = None,
    ) -> RateLimitDecision:
        decision = self.evaluate(key=key, rule=rule, now=now)
        if not decision.allowed:
            return decision

        now = now or datetime.now(timezone.utc)
        self._events[key].append(now)
        return decision

    def consume_or_raise(
        self,
        *,
        key: str,
        rule: RateLimitRule,
        now: datetime | None = None,
    ) -> RateLimitDecision:
        decision = self.consume(key=key, rule=rule, now=now)
        if not decision.allowed:
            raise RateLimitViolation(decision)
        return decision


class DatabaseFixedWindowRateLimiter:
    """DB-backed fixed-window limiter suitable for multi-instance deployments."""

    def __init__(
        self,
        *,
        retention_seconds: int = 86400,
        cleanup_interval_seconds: int = 60,
    ) -> None:
        self._retention_seconds = max(retention_seconds, 60)
        self._cleanup_interval_seconds = max(cleanup_interval_seconds, 30)
        self._last_cleanup_at: datetime | None = None

    @staticmethod
    def _window_start(now: datetime, window_seconds: int) -> datetime:
        epoch_seconds = int(now.timestamp())
        aligned_epoch = epoch_seconds - (epoch_seconds % window_seconds)
        return datetime.fromtimestamp(aligned_epoch, tz=timezone.utc)

    async def _cleanup_expired(self, *, db: AsyncSession, now: datetime) -> None:
        if self._last_cleanup_at and (now - self._last_cleanup_at).total_seconds() < self._cleanup_interval_seconds:
            return

        cutoff = now - timedelta(seconds=self._retention_seconds)
        await db.execute(delete(AIRateLimitCounter).where(AIRateLimitCounter.window_start < cutoff))
        self._last_cleanup_at = now

    async def _consume_with_upsert(
        self,
        *,
        db: AsyncSession,
        key: str,
        window_start: datetime,
        now: datetime,
        max_requests: int,
    ) -> int | None:
        dialect = db.bind.dialect.name if db.bind is not None else ""
        values = {
            "key": key,
            "window_start": window_start,
            "request_count": 1,
            "created_at": now,
            "updated_at": now,
        }
        if dialect == "postgresql":
            stmt = (
                postgresql_insert(AIRateLimitCounter)
                .values(**values)
                .on_conflict_do_update(
                    index_elements=["key", "window_start"],
                    set_={
                        "request_count": AIRateLimitCounter.request_count + 1,
                        "updated_at": now,
                    },
                    where=AIRateLimitCounter.request_count < max_requests,
                )
            )
            result = await db.execute(stmt)
        elif dialect == "sqlite":
            stmt = (
                sqlite_insert(AIRateLimitCounter)
                .values(**values)
                .on_conflict_do_update(
                    index_elements=["key", "window_start"],
                    set_={
                        "request_count": AIRateLimitCounter.request_count + 1,
                        "updated_at": now,
                    },
                    where=AIRateLimitCounter.request_count < max_requests,
                )
            )
            result = await db.execute(stmt)
        else:
            row = (
                await db.execute(
                    select(AIRateLimitCounter)
                    .where(AIRateLimitCounter.key == key)
                    .where(AIRateLimitCounter.window_start == window_start)
                    .with_for_update()
                )
            ).scalar_one_or_none()
            if row is None:
                db.add(
                    AIRateLimitCounter(
                        key=key,
                        window_start=window_start,
                        request_count=1,
                        created_at=now,
                        updated_at=now,
                    )
                )
                await db.flush()
                return 1
            if row.request_count >= max_requests:
                return None
            row.request_count += 1
            row.updated_at = now
            await db.flush()
            return int(row.request_count)

        if (result.rowcount or 0) <= 0:
            return None

        count_stmt = (
            select(AIRateLimitCounter.request_count)
            .where(AIRateLimitCounter.key == key)
            .where(AIRateLimitCounter.window_start == window_start)
            .limit(1)
        )
        count = (await db.execute(count_stmt)).scalar_one_or_none()
        return int(count) if count is not None else None

    async def consume(
        self,
        *,
        db: AsyncSession,
        key: str,
        rule: RateLimitRule,
        now: datetime | None = None,
    ) -> RateLimitDecision:
        now = now or datetime.now(timezone.utc)
        await self._cleanup_expired(db=db, now=now)

        window_start = self._window_start(now, rule.window_seconds)
        new_count = await self._consume_with_upsert(
            db=db,
            key=key,
            window_start=window_start,
            now=now,
            max_requests=rule.max_requests,
        )

        if new_count is None:
            window_end = window_start + timedelta(seconds=rule.window_seconds)
            retry_after = int((window_end - now).total_seconds())
            return RateLimitDecision(allowed=False, remaining=0, retry_after_seconds=max(retry_after, 1))

        remaining = max(rule.max_requests - new_count, 0)
        return RateLimitDecision(allowed=True, remaining=remaining, retry_after_seconds=0)

    async def consume_or_raise(
        self,
        *,
        db: AsyncSession,
        key: str,
        rule: RateLimitRule,
        now: datetime | None = None,
    ) -> RateLimitDecision:
        decision = await self.consume(db=db, key=key, rule=rule, now=now)
        if not decision.allowed:
            raise RateLimitViolation(decision)
        return decision


class SupportsSyncRateLimit(Protocol):
    def consume_or_raise(
        self,
        *,
        key: str,
        rule: RateLimitRule,
        now: datetime | None = None,
    ) -> RateLimitDecision: ...


class SupportsAsyncDbRateLimit(Protocol):
    async def consume_or_raise(
        self,
        *,
        db: AsyncSession,
        key: str,
        rule: RateLimitRule,
        now: datetime | None = None,
    ) -> RateLimitDecision: ...


async def consume_rate_limit_or_raise(
    *,
    limiter: SupportsSyncRateLimit | SupportsAsyncDbRateLimit,
    key: str,
    rule: RateLimitRule,
    db: AsyncSession | None = None,
    now: datetime | None = None,
) -> RateLimitDecision:
    if isinstance(limiter, DatabaseFixedWindowRateLimiter):
        if db is None:
            raise ValueError("Database session is required for DatabaseFixedWindowRateLimiter.")
        return await limiter.consume_or_raise(db=db, key=key, rule=rule, now=now)
    return limiter.consume_or_raise(key=key, rule=rule, now=now)
