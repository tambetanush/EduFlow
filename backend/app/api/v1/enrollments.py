from __future__ import annotations

from app.api.deps import (PaginationParams, get_current_user, get_db,
                          require_role)
from app.crud import (create_enrollment, delete_enrollment, get_enrollment,
                      get_enrollments_by_student, get_enrollments_by_workshop,
                      update_enrollment)
from app.crud.crud_misc import create_notification
from app.models import User, UserRole
from app.schemas.base import Page
from app.schemas.misc import NotificationCreate
from app.schemas.workshop import (EnrollmentCreate, EnrollmentResponse,
                                  EnrollmentUpdate)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ---------------------------------------------------------------------------
# POST /enrollments/
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enrol a student in a workshop",
)
async def enrol(
    payload: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnrollmentResponse:
    # Students may only enrol themselves
    if current_user.role == UserRole.STUDENT:
        if payload.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students may only enrol themselves.",
            )
    enrollment = await create_enrollment(db, payload)
    await create_notification(
        db,
        NotificationCreate(
            user_id=payload.student_id,
            title="Enrollment confirmed",
            message=f"You are enrolled in workshop {payload.workshop_id}",
            notification_type="success",
        ),
    )
    return EnrollmentResponse.model_validate(enrollment)


# ---------------------------------------------------------------------------
# GET /enrollments/student/{student_id}
# ---------------------------------------------------------------------------


@router.get(
    "/student/{student_id}",
    response_model=Page[EnrollmentResponse],
    summary="Get enrollments for a student",
)
async def list_by_student(
    student_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[EnrollmentResponse]:
    # Students may only query their own enrollments
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    items, total = await get_enrollments_by_student(
        db, student_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[EnrollmentResponse.model_validate(e) for e in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ---------------------------------------------------------------------------
# GET /enrollments/workshop/{workshop_id}
# ---------------------------------------------------------------------------


@router.get(
    "/workshop/{workshop_id}",
    response_model=Page[EnrollmentResponse],
    summary="Get all enrollments for a workshop (staff only)",
)
async def list_by_workshop(
    workshop_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_STAFF)),
) -> Page[EnrollmentResponse]:
    items, total = await get_enrollments_by_workshop(
        db, workshop_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[EnrollmentResponse.model_validate(e) for e in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ---------------------------------------------------------------------------
# GET /enrollments/{enrollment_id}
# ---------------------------------------------------------------------------


@router.get(
    "/{enrollment_id}",
    response_model=EnrollmentResponse,
    summary="Get a single enrollment",
)
async def get_one(
    enrollment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EnrollmentResponse:
    enrollment = await get_enrollment(db, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found.")
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return EnrollmentResponse.model_validate(enrollment)


# ---------------------------------------------------------------------------
# PATCH /enrollments/{enrollment_id}
# ---------------------------------------------------------------------------


@router.patch(
    "/{enrollment_id}",
    response_model=EnrollmentResponse,
    summary="Update enrollment status (staff only)",
)
async def update_one(
    enrollment_id: str,
    payload: EnrollmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> EnrollmentResponse:
    enrollment = await get_enrollment(db, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found.")
    updated = await update_enrollment(db, enrollment, payload)
    return EnrollmentResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# DELETE /enrollments/{enrollment_id}
# ---------------------------------------------------------------------------


@router.delete(
    "/{enrollment_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Drop / delete an enrollment",
)
async def delete_one(
    enrollment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    enrollment = await get_enrollment(db, enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found.")
    if current_user.role == UserRole.STUDENT and enrollment.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    await delete_enrollment(db, enrollment)
