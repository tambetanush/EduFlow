from __future__ import annotations

from app.api.deps import get_current_user, get_db, require_role
from app.crud import (create_institution, delete_institution, get_institution,
                      get_institutions, update_institution)
from app.models import User, UserRole
from app.schemas.user import (InstitutionCreate, InstitutionResponse,
                              InstitutionStatusUpdate, InstitutionUpdate)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/institutions", tags=["institutions"])


# ---------------------------------------------------------------------------
# POST /institutions/
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=InstitutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create institution (admin or institution admin)",
)
async def create(
    payload: InstitutionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> InstitutionResponse:
    institution = await create_institution(db, payload)
    return InstitutionResponse.model_validate(institution)


# ---------------------------------------------------------------------------
# GET /institutions/
# ---------------------------------------------------------------------------


@router.get(
    "/",
    response_model=list[InstitutionResponse],
    summary="List institutions",
)
async def list_institutions(
    offset: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[InstitutionResponse]:
    institutions, _total = await get_institutions(db, offset=offset, limit=limit)
    return [InstitutionResponse.model_validate(i) for i in institutions]


# ---------------------------------------------------------------------------
# GET /institutions/{institution_id}
# ---------------------------------------------------------------------------


@router.get(
    "/{institution_id}",
    response_model=InstitutionResponse,
    summary="Get institution by ID",
)
async def get_one(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> InstitutionResponse:
    institution = await get_institution(db, institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found.")
    return InstitutionResponse.model_validate(institution)


# ---------------------------------------------------------------------------
# PATCH /institutions/{institution_id}
# ---------------------------------------------------------------------------


@router.patch(
    "/{institution_id}",
    response_model=InstitutionResponse,
    summary="Update institution (admin only)",
)
async def update_one(
    institution_id: str,
    payload: InstitutionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> InstitutionResponse:
    institution = await get_institution(db, institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found.")
    # Institution admins can only update their own institution
    if (
        current_user.role == UserRole.INSTITUTION_ADMIN
        and institution.id != current_user.institution_id
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    updated = await update_institution(db, institution, payload)
    return InstitutionResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# PATCH /institutions/{institution_id}/status
# ---------------------------------------------------------------------------


@router.patch(
    "/{institution_id}/status",
    response_model=InstitutionResponse,
    summary="Toggle institution active/inactive status (admin only)",
)
async def toggle_status(
    institution_id: str,
    payload: InstitutionStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
) -> InstitutionResponse:
    institution = await get_institution(db, institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found.")

    updated = await update_institution(
        db,
        institution,
        InstitutionUpdate(is_active=payload.is_active),
    )
    return InstitutionResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# DELETE /institutions/{institution_id}
# ---------------------------------------------------------------------------


@router.delete(
    "/{institution_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Delete institution (admin only)",
)
async def delete_one(
    institution_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> None:
    institution = await get_institution(db, institution_id)
    if not institution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found.")
    await delete_institution(db, institution)
