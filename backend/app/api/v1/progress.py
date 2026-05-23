from __future__ import annotations

from app.api.deps import get_current_user, get_db
from app.crud import get_student_progress_by_student, upsert_student_progress
from app.models import User, UserRole
from app.schemas.misc import StudentProgressCreate, StudentProgressResponse, StudentProgressUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/", response_model=list[StudentProgressResponse], summary="List student progress records")
async def list_progress(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[StudentProgressResponse]:
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    items = await get_student_progress_by_student(db, current_user.id)
    return [StudentProgressResponse.model_validate(item) for item in items]


@router.patch("/", response_model=StudentProgressResponse, summary="Update student progress")
async def update_progress(
    payload: StudentProgressUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentProgressResponse:
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    updated = await upsert_student_progress(db, current_user.id, payload)
    return StudentProgressResponse.model_validate(updated)