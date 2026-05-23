from __future__ import annotations

from datetime import datetime
from typing import Any

from app.models import AuditLog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_audit_log(
    db: AsyncSession,
    *,
    actor_user_id: str | None,
    actor_role: str | None,
    action: str,
    target_type: str | None = None,
    target_id: str | None = None,
    metadata_: dict[str, Any] | None = None,
) -> AuditLog:
    row = AuditLog(
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata_=metadata_ or {},
    )
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row


async def list_audit_logs(
    db: AsyncSession,
    *,
    actor_user_id: str | None = None,
    action: str | None = None,
    target_type: str | None = None,
    since: datetime | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[AuditLog], int]:
    q = select(AuditLog)
    if actor_user_id:
        q = q.where(AuditLog.actor_user_id == actor_user_id)
    if action:
        q = q.where(AuditLog.action == action)
    if target_type:
        q = q.where(AuditLog.target_type == target_type)
    if since:
        q = q.where(AuditLog.created_at >= since)

    q = q.order_by(AuditLog.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(rows), int(total or 0)
