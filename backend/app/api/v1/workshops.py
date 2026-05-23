from __future__ import annotations

from app.api.deps import (PaginationParams, get_current_user, get_db,
                          require_role, verify_workshop_access)
from app.crud import (create_workshop, delete_workshop,
                      get_modules_by_workshop, get_workshop, get_workshops,
                      update_workshop)
from app.models import Enrollment, Institution, User, UserRole
from app.schemas.base import Page
from app.schemas.workshop import (ModuleResponse, WorkshopCreate,
                                  WorkshopEducatorProfileResponse,
                                  WorkshopResponse, WorkshopUpdate)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/workshops", tags=["workshops"])

_WRITE_ROLES = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ---------------------------------------------------------------------------
# POST /workshops/
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=WorkshopResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workshop (admin / institution_admin / educator)",
)
async def create(
    payload: WorkshopCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_WRITE_ROLES)),
) -> WorkshopResponse:
    # Institution admins / educators may only create under their own institution
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        if payload.institution_id and payload.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create workshops for your own institution.",
            )
        # Auto-assign institution if not specified
        if not payload.institution_id:
            payload = payload.model_copy(
                update={"institution_id": current_user.institution_id}
            )
    workshop = await create_workshop(db, payload)
    return WorkshopResponse.model_validate(workshop)


# ---------------------------------------------------------------------------
# GET /workshops/
# ---------------------------------------------------------------------------


@router.get(
    "/",
    response_model=Page[WorkshopResponse],
    summary="List workshops (scoped by institution for non-admins)",
)
async def list_workshops(
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[WorkshopResponse]:
    # Non-admin staff see only their institution's workshops
    inst_filter: str | None = None
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        inst_filter = current_user.institution_id
    elif current_user.role == UserRole.STUDENT:
        # Students see all workshops (their enrollments restrict access further)
        inst_filter = None

    workshops, total = await get_workshops(
        db, offset=page.offset, limit=page.limit, institution_id=inst_filter
    )
    workshop_ids = [workshop.id for workshop in workshops]
    enrollment_counts: dict[str, int] = {}
    if workshop_ids:
        rows = (
            await db.execute(
                select(Enrollment.workshop_id, func.count(Enrollment.id))
                .where(Enrollment.workshop_id.in_(workshop_ids))
                .group_by(Enrollment.workshop_id)
            )
        ).all()
        enrollment_counts = {
            row[0]: int(row[1] or 0)
            for row in rows
            if row[0]
        }
    for workshop in workshops:
        setattr(workshop, "enrollment_count", enrollment_counts.get(workshop.id, 0))

    return Page(
        items=[WorkshopResponse.model_validate(w) for w in workshops],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ---------------------------------------------------------------------------
# GET /workshops/{workshop_id}
# ---------------------------------------------------------------------------


@router.get(
    "/{workshop_id}",
    response_model=WorkshopResponse,
    summary="Get a workshop by ID",
)
async def get_one(
    workshop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkshopResponse:
    workshop = await get_workshop(db, workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")
    # Institution admins / educators: must be same institution
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        if workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    enrollment_count = (
        await db.execute(
            select(func.count(Enrollment.id)).where(Enrollment.workshop_id == workshop.id)
        )
    ).scalar_one()
    setattr(workshop, "enrollment_count", int(enrollment_count or 0))
    return WorkshopResponse.model_validate(workshop)


@router.get(
    "/{workshop_id}/educator-profile",
    response_model=WorkshopEducatorProfileResponse,
    summary="Get primary educator profile for a workshop",
)
async def get_workshop_educator_profile(
    workshop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WorkshopEducatorProfileResponse:
    workshop = await get_workshop(db, workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        if workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    institution_name = (
        await db.execute(select(Institution.name).where(Institution.id == workshop.institution_id))
    ).scalar_one_or_none() or "Institution"
    educators = (
        await db.execute(
            select(User)
            .where(User.role == UserRole.EDUCATOR)
            .where(User.institution_id == workshop.institution_id)
            .order_by(User.created_at.asc())
        )
    ).scalars().all()
    if not educators:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No educator profile found for this workshop institution.",
        )
    primary_educator = educators[0]
    if current_user.role == UserRole.EDUCATOR:
        for educator in educators:
            if educator.id == current_user.id:
                primary_educator = educator
                break

    return WorkshopEducatorProfileResponse(
        workshop_id=workshop_id,
        educator_id=primary_educator.id,
        name=primary_educator.name or primary_educator.email,
        email=primary_educator.email,
        department=primary_educator.department or "Academics",
        institution=institution_name,
        bio=primary_educator.bio or f"{primary_educator.name or 'Educator'} supports this workshop from {institution_name}.",
    )


# ---------------------------------------------------------------------------
# GET /workshops/{workshop_id}/modules
# ---------------------------------------------------------------------------


@router.get(
    "/{workshop_id}/modules",
    response_model=Page[ModuleResponse],
    summary="List modules for a workshop",
)
async def list_modules(
    workshop_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[ModuleResponse]:
    workshop = await get_workshop(db, workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        if workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    modules, total = await get_modules_by_workshop(
        db, workshop_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[ModuleResponse.model_validate(m) for m in modules],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ---------------------------------------------------------------------------
# PATCH /workshops/{workshop_id}
# ---------------------------------------------------------------------------


@router.patch(
    "/{workshop_id}",
    response_model=WorkshopResponse,
    summary="Update a workshop",
)
async def update_one(
    workshop_id: str,
    payload: WorkshopUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_WRITE_ROLES)),
) -> WorkshopResponse:
    workshop = await get_workshop(db, workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        if workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        if payload.institution_id and payload.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only assign workshops to your own institution.",
            )
    updated = await update_workshop(db, workshop, payload)
    return WorkshopResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# DELETE /workshops/{workshop_id}
# ---------------------------------------------------------------------------


@router.delete(
    "/{workshop_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Delete a workshop (admin / institution_admin only)",
)
async def delete_one(
    workshop_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> None:
    workshop = await get_workshop(db, workshop_id)
    if not workshop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workshop not found.")
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    await delete_workshop(db, workshop)
