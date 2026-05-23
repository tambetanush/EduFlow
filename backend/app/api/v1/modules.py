from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.api.deps import get_current_user, get_db, require_role
from app.crud import create_module, delete_module, get_module, update_module
from app.crud.crud_misc import create_notification
from app.models import Enrollment, User, UserRole
from app.schemas.misc import NotificationCreate
from app.schemas.workshop import (MaterialItem, ModuleCreate,
                                  ModuleReorderRequest, ModuleResponse,
                                  ModuleUpdate)
from app.services.storage import save_upload
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/modules", tags=["modules"])

_WRITE_ROLES = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ---------------------------------------------------------------------------
# POST /modules/
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a module",
)
async def create(
    payload: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> ModuleResponse:
    module = await create_module(db, payload)
    return ModuleResponse.model_validate(module)


# ---------------------------------------------------------------------------
# PATCH /modules/reorder   — batch reorder (must be BEFORE /{module_id})
# ---------------------------------------------------------------------------


@router.patch(
    "/reorder",
    response_model=list[ModuleResponse],
    summary="Batch-reorder modules by setting their order_index values",
)
async def batch_reorder(
    payload: ModuleReorderRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> list[ModuleResponse]:
    results: list[ModuleResponse] = []
    for entry in payload.items:
        module = await get_module(db, entry.module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Module '{entry.module_id}' not found.",
            )
        updated = await update_module(db, module, ModuleUpdate(order_index=entry.order_index))
        results.append(ModuleResponse.model_validate(updated))
    return results


# ---------------------------------------------------------------------------
# GET /modules/{module_id}
# ---------------------------------------------------------------------------


@router.get(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Get a module by ID",
)
async def get_one(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ModuleResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")
    return ModuleResponse.model_validate(module)


# ---------------------------------------------------------------------------
# PATCH /modules/{module_id}
# ---------------------------------------------------------------------------


@router.patch(
    "/{module_id}",
    response_model=ModuleResponse,
    summary="Update a module",
)
async def update_one(
    module_id: str,
    payload: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> ModuleResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")
    updated = await update_module(db, module, payload)
    return ModuleResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# DELETE /modules/{module_id}
# ---------------------------------------------------------------------------


@router.delete(
    "/{module_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Delete a module",
)
async def delete_one(
    module_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> None:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")
    await delete_module(db, module)


# ---------------------------------------------------------------------------
# POST /modules/{module_id}/materials/upload
# ---------------------------------------------------------------------------


@router.post(
    "/{module_id}/materials/upload",
    response_model=ModuleResponse,
    summary="Upload a material file and append it to the module's materials list",
)
async def upload_material(
    module_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> ModuleResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    content = await file.read()
    relative_path = await save_upload(
        content=content,
        filename=file.filename,
        subfolder=f"modules/{module_id}",
    )

    # Detect media type from content_type / extension
    ct = (file.content_type or "").lower()
    filename = (file.filename or "").lower()
    if "video" in ct or filename.endswith((".mp4", ".webm", ".mov", ".m4v")):
        mat_type = "video"
    elif "pdf" in ct or filename.endswith(".pdf"):
        mat_type = "pdf"
    elif "text" in ct or filename.endswith((".md", ".txt", ".html")):
        mat_type = "text"
    else:
        mat_type = "link"

    new_material = MaterialItem(
        id=str(uuid.uuid4()),
        title=file.filename,
        type=mat_type,
        content=relative_path,
        created_at=datetime.now(tz=timezone.utc).isoformat(),
    )

    existing: list = list(module.materials or [])
    existing_items = [
        MaterialItem(**m) if isinstance(m, dict) else m for m in existing
    ]
    existing_items.append(new_material)

    patch = ModuleUpdate(materials=existing_items)
    updated = await update_module(db, module, patch)

    enrolled_rows = (
        await db.execute(
            select(Enrollment.student_id).where(Enrollment.workshop_id == module.workshop_id)
        )
    ).all()
    student_ids = sorted({row[0] for row in enrolled_rows if row[0]})
    for student_id in student_ids:
        await create_notification(
            db,
            NotificationCreate(
                user_id=student_id,
                title="New material available",
                message=f"New material available in module {module.title or module.id}",
                notification_type="info",
            ),
        )

    return ModuleResponse.model_validate(updated)
