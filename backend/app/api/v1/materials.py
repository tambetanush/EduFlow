"""
app/api/v1/materials.py
-----------------------
Endpoints to manipulate individual material entries embedded in Module.materials
(a JSON column containing a list of MaterialItem dictionaries).

Routes:
  PATCH  /materials/{module_id}/{material_id}   – update one material field
  DELETE /materials/{module_id}/{material_id}   – delete one material from the list
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.config import settings
from app.crud import get_module, update_module
from app.models import Enrollment, User, UserRole, Workshop
from app.schemas.misc import MaterialDownloadResponse
from app.schemas.workshop import (
    MaterialItem,
    MaterialItemCreate,
    MaterialItemUpdate,
    ModuleResponse,
    ModuleUpdate,
)

router = APIRouter(prefix="/materials", tags=["materials"])

_WRITE_ROLES = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


@router.post(
    "/{module_id}",
    response_model=ModuleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a material item to a module (staff only)",
)
async def create_material(
    module_id: str,
    payload: MaterialItemCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> ModuleResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    existing: list = list(module.materials or [])
    existing_items = [
        MaterialItem(**entry) if isinstance(entry, dict) else entry for entry in existing
    ]

    new_item = MaterialItem(
        id=str(uuid.uuid4()),
        title=payload.title,
        type=payload.type,
        content=payload.content,
        created_at=datetime.now(tz=timezone.utc).isoformat(),
    )
    existing_items.append(new_item)

    updated_module = await update_module(db, module, ModuleUpdate(materials=existing_items))
    return ModuleResponse.model_validate(updated_module)


# ────────────────────────────────────────────────────────────────────────────
# PATCH /materials/{module_id}/{material_id}
# ────────────────────────────────────────────────────────────────────────────


@router.patch(
    "/{module_id}/{material_id}",
    response_model=ModuleResponse,
    summary="Update a single material item inside a module (staff only)",
)
async def patch_material(
    module_id: str,
    material_id: str,
    payload: MaterialItemUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> ModuleResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    materials: list[dict] = list(module.materials or [])
    updated_any = False
    new_materials: list[MaterialItem] = []

    for raw in materials:
        item = MaterialItem(**raw) if isinstance(raw, dict) else raw
        if item.id == material_id:
            # Apply partial update
            patch = payload.model_dump(exclude_unset=True)
            if "type" in patch and isinstance(patch["type"], str):
                patch["type"] = patch["type"].lower()
            item = item.model_copy(update=patch)
            updated_any = True
        new_materials.append(item)

    if not updated_any:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{material_id}' not found in module '{module_id}'.",
        )

    updated_module = await update_module(db, module, ModuleUpdate(materials=new_materials))
    return ModuleResponse.model_validate(updated_module)


# ────────────────────────────────────────────────────────────────────────────
# DELETE /materials/{module_id}/{material_id}
# ────────────────────────────────────────────────────────────────────────────


@router.delete(
    "/{module_id}/{material_id}",
    response_model=ModuleResponse,
    summary="Remove a single material item from a module (staff only)",
)
async def delete_material(
    module_id: str,
    material_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_WRITE_ROLES)),
) -> ModuleResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    materials: list[dict] = list(module.materials or [])
    original_count = len(materials)

    filtered: list[MaterialItem] = [
        MaterialItem(**m) if isinstance(m, dict) else m
        for m in materials
        if (m.get("id") if isinstance(m, dict) else m.id) != material_id
    ]

    if len(filtered) == original_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{material_id}' not found in module '{module_id}'.",
        )

    updated_module = await update_module(db, module, ModuleUpdate(materials=filtered))
    return ModuleResponse.model_validate(updated_module)


@router.get(
    "/{module_id}/{material_id}/download",
    response_model=MaterialDownloadResponse,
    summary="Get a download URL for one module material",
)
async def download_material(
    module_id: str,
    material_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MaterialDownloadResponse:
    module = await get_module(db, module_id)
    if not module:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Module not found.")

    # ── Authorization ────────────────────────────────────────────────────────
    if current_user.role == UserRole.ADMIN:
        pass  # ADMIN: unrestricted
    elif current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        # Staff must belong to the same institution as the workshop.
        workshop = await db.get(Workshop, module.workshop_id)
        if not workshop or workshop.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    elif current_user.role == UserRole.STUDENT:
        # Students must be enrolled in the workshop that owns this module.
        enrolled = (
            await db.execute(
                select(Enrollment.id).where(
                    Enrollment.student_id == current_user.id,
                    Enrollment.workshop_id == module.workshop_id,
                ).limit(1)
            )
        ).scalar_one_or_none()
        if enrolled is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    material: MaterialItem | None = None
    for entry in list(module.materials or []):
        item = MaterialItem(**entry) if isinstance(entry, dict) else entry
        if item.id == material_id:
            material = item
            break

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material '{material_id}' not found in module '{module_id}'.",
        )

    content = (material.content or "").strip()
    if content.startswith("http://") or content.startswith("https://"):
        return MaterialDownloadResponse(
            module_id=module_id,
            material_id=material_id,
            download_url=content,
        )

    normalized = content.lstrip("/")
    file_path = Path(normalized)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material file not found.")

    normalized_url_path = normalized.replace("\\", "/")
    return MaterialDownloadResponse(
        module_id=module_id,
        material_id=material_id,
        download_url=f"{settings.BASE_URL}/{normalized_url_path}",
    )
