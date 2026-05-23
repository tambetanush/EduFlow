from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ApprovalRequest, ApprovalRequestStatus, SalaryPayment


# ---------------------------------------------------------------------------
# Approval Requests
# ---------------------------------------------------------------------------


async def create_approval_request(db: AsyncSession, req: ApprovalRequest) -> ApprovalRequest:
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req


async def get_approval_request(db: AsyncSession, request_id: str) -> Optional[ApprovalRequest]:
    return await db.get(ApprovalRequest, request_id)


async def list_approval_requests(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
) -> Tuple[Sequence[ApprovalRequest], int]:
    q = select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc())
    if status:
        q = q.where(ApprovalRequest.status == status)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, int(total or 0)


async def resolve_approval_request(
    db: AsyncSession,
    req: ApprovalRequest,
    *,
    status: ApprovalRequestStatus,
) -> ApprovalRequest:
    req.status = status
    req.resolved_at = datetime.utcnow()
    db.add(req)
    await db.commit()
    await db.refresh(req)
    return req


# ---------------------------------------------------------------------------
# Salary Payments
# ---------------------------------------------------------------------------


async def list_salary_payments(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 200,
    month: Optional[str] = None,
) -> Tuple[Sequence[SalaryPayment], int]:
    q = select(SalaryPayment).order_by(SalaryPayment.created_at.desc())
    if month:
        q = q.where(SalaryPayment.month == month)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, int(total or 0)


async def get_salary_payment(db: AsyncSession, payment_id: str) -> Optional[SalaryPayment]:
    return await db.get(SalaryPayment, payment_id)


async def create_salary_payment(db: AsyncSession, payment: SalaryPayment) -> SalaryPayment:
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment