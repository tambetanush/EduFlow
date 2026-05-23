from __future__ import annotations

from app.api.deps import get_current_user, get_db, require_role
from app.crud import delete_question, get_question, update_question
from app.models import User, UserRole
from app.schemas.assessment import QuestionResponse, QuestionUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/questions", tags=["questions"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


@router.patch(
    "/{question_id}",
    response_model=QuestionResponse,
    summary="Update a question (staff only)",
)
async def update_one(
    question_id: str,
    payload: QuestionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> QuestionResponse:
    q = await get_question(db, question_id)
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    updated = await update_question(db, q, payload)
    return QuestionResponse.model_validate(updated)


@router.delete(
    "/{question_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Delete a question (staff only)",
)
async def delete_one(
    question_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> None:
    q = await get_question(db, question_id)
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")
    await delete_question(db, q)
