from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db, require_role
from app.crud.crud_admin import create_salary_payment, list_salary_payments
from app.models import SalaryPayment, SalaryPaymentStatus, User, UserRole
from app.schemas.base import Page
from app.schemas.misc import SalaryPaymentCreate, SalaryPaymentResponse

router = APIRouter(prefix="/salaries", tags=["salaries"])


@router.get(
    "/",
    response_model=Page[SalaryPaymentResponse],
    summary="List salary payments (admin or institution admin)",
)
async def list_payments(
    page: PaginationParams = Depends(),
    month: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> Page[SalaryPaymentResponse]:
    items, total = await list_salary_payments(db, offset=page.offset, limit=page.limit, month=month)
    return Page(
        items=[SalaryPaymentResponse.model_validate(p) for p in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.post(
    "/pay",
    response_model=SalaryPaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark an educator salary as paid for a month (admin or institution admin)",
)
async def pay(
    payload: SalaryPaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> SalaryPaymentResponse:
    # Keep month stable (YYYY-MM) but allow callers to pass it through.
    month = payload.month
    if not month:
        month = datetime.utcnow().strftime("%Y-%m")

    payment = SalaryPayment(
        educator_id=payload.educator_id,
        month=month,
        amount=payload.amount,
        status=SalaryPaymentStatus.PAID,
    )
    created = await create_salary_payment(db, payment)
    return SalaryPaymentResponse.model_validate(created)