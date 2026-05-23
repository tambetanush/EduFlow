from __future__ import annotations

from app.api.deps import (PaginationParams,
                          ensure_user_can_read_assessments_for_workshop,
                          get_current_user, get_db, require_role)
from app.crud import (create_assessment, create_question, delete_assessment,
                      delete_question, get_assessment,
                      get_assessments_by_module, get_assessments_by_workshop,
                      get_module, get_question, get_questions_by_assessment,
                      update_assessment, update_question)
from app.models import User, UserRole
from app.schemas.assessment import (AssessmentCreate, AssessmentResponse,
                                    AssessmentUpdate, QuestionCreate,
                                    QuestionResponse, QuestionUpdate)
from app.schemas.base import Page
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/assessments", tags=["assessments"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ────────────────────────────────────────────────────────────────────────────
# Assessments CRUD
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an assessment (staff only)",
)
async def create(
    payload: AssessmentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> AssessmentResponse:
    obj = await create_assessment(db, payload)
    return AssessmentResponse.model_validate(obj)


@router.get(
    "/workshop/{workshop_id}",
    response_model=Page[AssessmentResponse],
    summary="List assessments for a workshop",
)
async def list_by_workshop(
    workshop_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[AssessmentResponse]:
    await ensure_user_can_read_assessments_for_workshop(db, current_user, workshop_id)
    items, total = await get_assessments_by_workshop(
        db, workshop_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[AssessmentResponse.model_validate(a) for a in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.get(
    "/module/{module_id}",
    response_model=Page[AssessmentResponse],
    summary="List assessments for a module",
)
async def list_by_module(
    module_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[AssessmentResponse]:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")
    await ensure_user_can_read_assessments_for_workshop(db, current_user, module.workshop_id)
    items, total = await get_assessments_by_module(
        db, module_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[AssessmentResponse.model_validate(a) for a in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.get(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Get an assessment by ID",
)
async def get_one(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentResponse:
    obj = await get_assessment(db, assessment_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    await ensure_user_can_read_assessments_for_workshop(db, current_user, obj.workshop_id)
    return AssessmentResponse.model_validate(obj)


@router.patch(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    summary="Update an assessment (staff only)",
)
async def update_one(
    assessment_id: str,
    payload: AssessmentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> AssessmentResponse:
    obj = await get_assessment(db, assessment_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    updated = await update_assessment(db, obj, payload)
    return AssessmentResponse.model_validate(updated)


@router.delete(
    "/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    summary="Delete an assessment (staff only)",
)
async def delete_one(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> None:
    obj = await get_assessment(db, assessment_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    await delete_assessment(db, obj)


# ────────────────────────────────────────────────────────────────────────────
# Questions — nested under assessment
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{assessment_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a question to an assessment (staff only)",
)
async def add_question(
    assessment_id: str,
    payload: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> QuestionResponse:
    if not await get_assessment(db, assessment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    if payload.assessment_id != assessment_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="assessment_id in body must match the path parameter.",
        )
    q = await create_question(db, payload)
    return QuestionResponse.model_validate(q)


@router.get(
    "/{assessment_id}/questions",
    response_model=Page[QuestionResponse],
    summary="List questions for an assessment (staff sees is_correct)",
)
async def list_questions(
    assessment_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> Page[QuestionResponse]:
    if not await get_assessment(db, assessment_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    items, total = await get_questions_by_assessment(
        db, assessment_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[QuestionResponse.model_validate(q) for q in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )
