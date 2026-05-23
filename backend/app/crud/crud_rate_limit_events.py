from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RateLimitEvent


async def create_rate_limit_event(
    db: AsyncSession,
    *,
    key: str,
    allowed: bool,
    remaining: int,
    retry_after_seconds: int,
    rule_max_requests: int,
    rule_window_seconds: int,
    actor_user_id: str | None = None,
    institution_id: str | None = None,
) -> RateLimitEvent:
    row = RateLimitEvent(
        key=key,
        allowed=allowed,
        remaining=remaining,
        retry_after_seconds=retry_after_seconds,
        rule_max_requests=rule_max_requests,
        rule_window_seconds=rule_window_seconds,
        actor_user_id=actor_user_id,
        institution_id=institution_id,
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


async def list_rate_limit_events(
    db: AsyncSession,
    *,
    key_prefix: str | None = None,
    allowed: bool | None = None,
    since: datetime | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[RateLimitEvent], int]:
    q = select(RateLimitEvent)
    if key_prefix:
        q = q.where(RateLimitEvent.key.like(f"{key_prefix}%"))
    if allowed is not None:
        q = q.where(RateLimitEvent.allowed == allowed)
    if since:
        q = q.where(RateLimitEvent.created_at >= since)
    q = q.order_by(RateLimitEvent.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(rows), int(total or 0)

