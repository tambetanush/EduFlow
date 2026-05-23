from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.crud.crud_misc import create_notification
from app.models import NotificationType, User, UserRole
from app.schemas.misc import (
    NotificationCreate,
    ParentContactDirectoryResponse,
    ParentContactItem,
    ParentMessageRequest,
    ParentMessageResponse,
)

router = APIRouter(prefix="/communication", tags=["communication"])


@router.get(
    "/parent-contacts",
    response_model=ParentContactDirectoryResponse,
    summary="Fetch parent contact directory entries for students",
)
async def parent_contact_directory(
    student_ids: list[str] = Query(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)),
) -> ParentContactDirectoryResponse:
    unique_ids = [student_id for student_id in dict.fromkeys(student_ids) if student_id]
    if not unique_ids:
        return ParentContactDirectoryResponse(items=[], total=0)

    query = select(User).where(User.id.in_(unique_ids)).where(User.role == UserRole.STUDENT)
    if current_user.role in {UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR}:
        query = query.where(User.institution_id == current_user.institution_id)

    students = (await db.execute(query)).scalars().all()
    contacts = [
        ParentContactItem(
            student_id=student.id,
            parent_name=student.parent_name,
            parent_email=student.parent_email,
        )
        for student in students
    ]
    return ParentContactDirectoryResponse(items=contacts, total=len(contacts))


@router.post(
    "/parent-email",
    response_model=ParentMessageResponse,
    summary="Dispatch parent communication message and log notifications",
)
async def dispatch_parent_email(
    payload: ParentMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)),
) -> ParentMessageResponse:
    student_ids = [student_id for student_id in dict.fromkeys(payload.student_ids) if student_id]
    if not student_ids:
        return ParentMessageResponse(accepted=0, failed=0, message="No student recipients provided.")

    query = select(User).where(User.id.in_(student_ids)).where(User.role == UserRole.STUDENT)
    if current_user.role in {UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR}:
        query = query.where(User.institution_id == current_user.institution_id)
    students = (await db.execute(query)).scalars().all()
    student_by_id = {student.id: student for student in students}

    accepted = 0
    failed = 0

    for student_id in student_ids:
        student = student_by_id.get(student_id)
        if not student or not student.parent_email:
            failed += 1
            continue
        try:
            await create_notification(
                db,
                NotificationCreate(
                    user_id=student_id,
                    message=f"[Parent Message to {student.parent_email}] {payload.subject}: {payload.body}",
                    notification_type=NotificationType.GENERAL,
                ),
            )
            accepted += 1
        except Exception:
            failed += 1

    return ParentMessageResponse(
        accepted=accepted,
        failed=failed,
        message="Parent communication request processed.",
    )
