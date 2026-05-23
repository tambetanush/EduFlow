from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_current_user, get_db, require_role
from app.crud.crud_misc import (
    create_payment,
    get_payment,
    get_payments_by_student,
    get_student_fees_by_student,
)
from app.models import User, UserRole
from app.schemas.base import Page
from app.schemas.misc import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/payments", tags=["payments"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ────────────────────────────────────────────────────────────────────────────
# POST /payments/
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a payment (staff only); optionally credits a student fee balance",
)
async def record_payment(
    payload: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> PaymentResponse:
    # If a student_fee_id is provided, verify it belongs to the same student
    if payload.student_fee_id:
        fees, _ = await get_student_fees_by_student(db, payload.student_id, limit=200)
        ids = {f.id for f in fees}
        if payload.student_fee_id not in ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="student_fee_id does not belong to this student.",
            )

    payment = await create_payment(db, payload)
    return PaymentResponse.model_validate(payment)


# ────────────────────────────────────────────────────────────────────────────
# GET /payments/{payment_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
    summary="Get a payment record by ID (staff only)",
)
async def get_one(
    payment_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> PaymentResponse:
    payment = await get_payment(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    return PaymentResponse.model_validate(payment)


# ────────────────────────────────────────────────────────────────────────────
# GET /payments/student/{student_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/student/{student_id}",
    response_model=Page[PaymentResponse],
    summary="List payment history for a student (newest first)",
)
async def list_by_student(
    student_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[PaymentResponse]:
    # Students can see their own history; staff see all
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    items, total = await get_payments_by_student(
        db, student_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[PaymentResponse.model_validate(p) for p in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )
