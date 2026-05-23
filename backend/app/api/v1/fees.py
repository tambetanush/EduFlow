from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_current_user, get_db, require_role
from app.crud.crud_misc import (
    create_fee_plan,
    create_student_fee,
    get_fee_plan,
    get_fee_plans,
    get_student_fee,
    get_student_fees_by_student,
    update_fee_plan,
)
from app.models import User, UserRole
from app.schemas.base import Page
from app.schemas.misc import (
    FeePlanCreate,
    FeePlanResponse,
    FeePlanUpdate,
    StudentFeeAssign,
    StudentFeeCreate,
    StudentFeeResponse,
)

router = APIRouter(prefix="/fees", tags=["fees"])

_ADMIN_ROLES = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)
_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ────────────────────────────────────────────────────────────────────────────
# Fee Plans
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/plans",
    response_model=FeePlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a fee plan (admin / institution_admin only)",
)
async def create_plan(
    payload: FeePlanCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_ADMIN_ROLES)),
) -> FeePlanResponse:
    plan = await create_fee_plan(db, payload)
    return FeePlanResponse.model_validate(plan)


@router.get(
    "/plans",
    response_model=Page[FeePlanResponse],
    summary="List all fee plans",
)
async def list_plans(
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Page[FeePlanResponse]:
    items, total = await get_fee_plans(db, offset=page.offset, limit=page.limit)
    return Page(
        items=[FeePlanResponse.model_validate(p) for p in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.get(
    "/plans/{plan_id}",
    response_model=FeePlanResponse,
    summary="Get a fee plan by ID",
)
async def get_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> FeePlanResponse:
    plan = await get_fee_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee plan not found.")
    return FeePlanResponse.model_validate(plan)


@router.patch(
    "/plans/{plan_id}",
    response_model=FeePlanResponse,
    summary="Update a fee plan (admin / institution_admin only)",
)
async def update_plan(
    plan_id: str,
    payload: FeePlanUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_ADMIN_ROLES)),
) -> FeePlanResponse:
    plan = await get_fee_plan(db, plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee plan not found.")
    updated = await update_fee_plan(db, plan, payload)
    return FeePlanResponse.model_validate(updated)


# ────────────────────────────────────────────────────────────────────────────
# Student Fee Assignment
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/assign",
    response_model=StudentFeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a fee plan to a student",
)
async def assign_fee(
    payload: StudentFeeAssign,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_ADMIN_ROLES)),
) -> StudentFeeResponse:
    plan = await get_fee_plan(db, payload.fee_plan_id)
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee plan not found.")

    fee = await create_student_fee(
        db,
        StudentFeeCreate(
            student_id=payload.student_id,
            fee_plan_id=payload.fee_plan_id,
            balance=payload.initial_balance,
        ),
    )
    response = StudentFeeResponse.model_validate(fee)
    response.fee_plan = FeePlanResponse.model_validate(plan)
    return response


# ────────────────────────────────────────────────────────────────────────────
# GET /fees/student/{student_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/student/{student_id}",
    response_model=Page[StudentFeeResponse],
    summary="Get fee records for a student (with fee plan detail)",
)
async def list_student_fees(
    student_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[StudentFeeResponse]:
    # Students can only see their own fees
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    items, total = await get_student_fees_by_student(
        db, student_id, offset=page.offset, limit=page.limit
    )

    enriched: list[StudentFeeResponse] = []
    for fee in items:
        r = StudentFeeResponse.model_validate(fee)
        if fee.fee_plan_id:
            plan = await get_fee_plan(db, fee.fee_plan_id)
            if plan:
                r.fee_plan = FeePlanResponse.model_validate(plan)
        enriched.append(r)

    return Page(items=enriched, total=total, offset=page.offset, limit=page.limit)


# ────────────────────────────────────────────────────────────────────────────
# GET /fees/{student_fee_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{student_fee_id}",
    response_model=StudentFeeResponse,
    summary="Get a specific student fee record",
)
async def get_student_fee_record(
    student_fee_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentFeeResponse:
    fee = await get_student_fee(db, student_fee_id)
    if not fee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fee record not found.")

    if current_user.role == UserRole.STUDENT and fee.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    r = StudentFeeResponse.model_validate(fee)
    if fee.fee_plan_id:
        plan = await get_fee_plan(db, fee.fee_plan_id)
        if plan:
            r.fee_plan = FeePlanResponse.model_validate(plan)
    return r
