from __future__ import annotations

from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Certificate, FeePlan, Notification, Payment, StudentFee, StudentProgress
from app.schemas.misc import (
    CertificateCreate,
    FeePlanCreate,
    FeePlanUpdate,
    NotificationCreate,
    NotificationUpdate,
    PaymentCreate,
    StudentProgressCreate,
    StudentProgressUpdate,
    StudentFeeCreate,
    StudentFeeUpdate,
)


# ---------------------------------------------------------------------------
# Certificate CRUD
# ---------------------------------------------------------------------------


async def create_certificate(
    db: AsyncSession, data: CertificateCreate, verification_code: str
) -> Certificate:
    cert = Certificate(
        student_id=data.student_id,
        workshop_id=data.workshop_id,
        verification_code=verification_code,
    )
    db.add(cert)
    await db.flush()
    await db.refresh(cert)
    return cert


async def get_certificate(
    db: AsyncSession, certificate_id: str
) -> Optional[Certificate]:
    return await db.get(Certificate, certificate_id)


async def get_certificate_by_code(
    db: AsyncSession, verification_code: str
) -> Optional[Certificate]:
    result = await db.execute(
        select(Certificate).where(Certificate.verification_code == verification_code)
    )
    return result.scalars().first()


async def get_certificates_by_student(
    db: AsyncSession, student_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Certificate], int]:
    """Return (certificates, total_count) for a student."""
    q = select(Certificate).where(Certificate.student_id == student_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def delete_certificate(db: AsyncSession, cert: Certificate) -> None:
    await db.delete(cert)
    await db.flush()


# ---------------------------------------------------------------------------
# FeePlan CRUD
# ---------------------------------------------------------------------------


async def create_fee_plan(db: AsyncSession, data: FeePlanCreate) -> FeePlan:
    plan = FeePlan(**data.model_dump())
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return plan


async def get_fee_plan(db: AsyncSession, plan_id: str) -> Optional[FeePlan]:
    return await db.get(FeePlan, plan_id)


async def get_fee_plans(
    db: AsyncSession, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[FeePlan], int]:
    """Return (fee_plans, total_count)."""
    q = select(FeePlan)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def update_fee_plan(
    db: AsyncSession, plan: FeePlan, data: FeePlanUpdate
) -> FeePlan:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    await db.flush()
    await db.refresh(plan)
    return plan


async def delete_fee_plan(db: AsyncSession, plan: FeePlan) -> None:
    await db.delete(plan)
    await db.flush()


# ---------------------------------------------------------------------------
# StudentFee CRUD
# ---------------------------------------------------------------------------


async def create_student_fee(
    db: AsyncSession, data: StudentFeeCreate
) -> StudentFee:
    fee = StudentFee(**data.model_dump())
    db.add(fee)
    await db.flush()
    await db.refresh(fee)
    return fee


async def get_student_fee(
    db: AsyncSession, student_fee_id: str
) -> Optional[StudentFee]:
    return await db.get(StudentFee, student_fee_id)


async def get_student_fees_by_student(
    db: AsyncSession, student_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[StudentFee], int]:
    """Return (student_fees, total_count) for a student."""
    q = select(StudentFee).where(StudentFee.student_id == student_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def update_student_fee(
    db: AsyncSession, fee: StudentFee, data: StudentFeeUpdate
) -> StudentFee:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(fee, field, value)
    await db.flush()
    await db.refresh(fee)
    return fee


async def delete_student_fee(db: AsyncSession, fee: StudentFee) -> None:
    await db.delete(fee)
    await db.flush()


# ---------------------------------------------------------------------------
# Payment CRUD
# ---------------------------------------------------------------------------


async def create_payment(db: AsyncSession, data: PaymentCreate) -> Payment:
    """Create a payment record and optionally reduce the student's fee balance."""
    payment = Payment(
        student_id=data.student_id,
        amount=data.amount,
        method=data.method,
        reference=data.reference,
    )
    db.add(payment)
    await db.flush()

    # If a specific StudentFee row is targeted, credit the balance
    if data.student_fee_id:
        student_fee = await db.get(StudentFee, data.student_fee_id)
        if student_fee and student_fee.student_id == data.student_id:
            student_fee.balance = max(0, (student_fee.balance or 0) - data.amount)
            await db.flush()

    await db.refresh(payment)
    return payment


async def get_payment(db: AsyncSession, payment_id: str) -> Optional[Payment]:
    return await db.get(Payment, payment_id)


async def get_payments_by_student(
    db: AsyncSession, student_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Payment], int]:
    """Return (payments, total_count) for a student, newest first."""
    q = (
        select(Payment)
        .where(Payment.student_id == student_id)
        .order_by(Payment.created_at.desc())
    )
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


# Payments are immutable; no update function intentionally.


async def delete_payment(db: AsyncSession, payment: Payment) -> None:
    await db.delete(payment)
    await db.flush()


# ---------------------------------------------------------------------------
# Notification CRUD
# ---------------------------------------------------------------------------


async def create_notification(
    db: AsyncSession, data: NotificationCreate
) -> Notification:
    payload = data.model_dump()
    if not payload.get("title"):
        payload["title"] = "Notification"
    notification = Notification(**payload)
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    return notification


async def get_notification(
    db: AsyncSession, notification_id: str
) -> Optional[Notification]:
    return await db.get(Notification, notification_id)


async def get_notifications_by_user(
    db: AsyncSession, user_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Notification], int]:
    """Return (notifications, total_count), newest first."""
    q = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def update_notification(
    db: AsyncSession, notification: Notification, data: NotificationUpdate
) -> Notification:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(notification, field, value)
    await db.flush()
    await db.refresh(notification)
    return notification


async def delete_notification(db: AsyncSession, notification: Notification) -> None:
    await db.delete(notification)
    await db.flush()


# ---------------------------------------------------------------------------
# StudentProgress CRUD
# ---------------------------------------------------------------------------


async def get_student_progress_by_student(
    db: AsyncSession, student_id: str
) -> Sequence[StudentProgress]:
    result = await db.execute(select(StudentProgress).where(StudentProgress.student_id == student_id))
    return result.scalars().all()


async def get_student_progress_entry(
    db: AsyncSession, student_id: str, workshop_id: str
) -> Optional[StudentProgress]:
    result = await db.execute(
        select(StudentProgress).where(
            StudentProgress.student_id == student_id,
            StudentProgress.workshop_id == workshop_id,
        )
    )
    return result.scalars().first()


async def upsert_student_progress(
    db: AsyncSession, student_id: str, data: StudentProgressCreate | StudentProgressUpdate
) -> StudentProgress:
    workshop_id = data.workshop_id
    current_module_index = data.current_module_index
    entry = await get_student_progress_entry(db, student_id, workshop_id)
    if entry is None:
        entry = StudentProgress(
            student_id=student_id,
            workshop_id=workshop_id,
            current_module_index=current_module_index,
        )
        db.add(entry)
    else:
        entry.current_module_index = current_module_index
    await db.flush()
    await db.refresh(entry)
    return entry
