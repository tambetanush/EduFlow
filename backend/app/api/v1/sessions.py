from __future__ import annotations

from app.api.deps import (PaginationParams, get_current_user, get_db,
                          require_role)
from app.crud import (create_attendance, create_session, delete_session,
                      get_attendance_by_session, get_session,
                      get_sessions_by_workshop, update_attendance,
                      update_session)
from app.models import User, UserRole
from app.schemas.base import Page
from app.schemas.workshop import (AttendanceCreate, AttendanceResponse,
                                  AttendanceUpdate, SessionCreate,
                                  SessionResponse, SessionUpdate)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/sessions", tags=["sessions"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


# ---------------------------------------------------------------------------
# POST /sessions/
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a session (staff only)",
)
async def create(
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> SessionResponse:
    session_obj = await create_session(db, payload)
    return SessionResponse.model_validate(session_obj)


# ---------------------------------------------------------------------------
# GET /sessions/workshop/{workshop_id}
# ---------------------------------------------------------------------------


@router.get(
    "/workshop/{workshop_id}",
    response_model=Page[SessionResponse],
    summary="List sessions for a workshop",
)
async def list_by_workshop(
    workshop_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Page[SessionResponse]:
    items, total = await get_sessions_by_workshop(
        db, workshop_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[SessionResponse.model_validate(s) for s in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ---------------------------------------------------------------------------
# GET /sessions/{session_id}
# ---------------------------------------------------------------------------


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get a session by ID",
)
async def get_one(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> SessionResponse:
    session_obj = await get_session(db, session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return SessionResponse.model_validate(session_obj)


# ---------------------------------------------------------------------------
# PATCH /sessions/{session_id}
# ---------------------------------------------------------------------------


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Update a session (staff only)",
)
async def update_one(
    session_id: str,
    payload: SessionUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> SessionResponse:
    session_obj = await get_session(db, session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    updated = await update_session(db, session_obj, payload)
    return SessionResponse.model_validate(updated)


# ---------------------------------------------------------------------------
# DELETE /sessions/{session_id}
# ---------------------------------------------------------------------------


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Delete a session (staff only)",
)
async def delete_one(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> None:
    session_obj = await get_session(db, session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    await delete_session(db, session_obj)


# ---------------------------------------------------------------------------
# POST /sessions/{session_id}/attendance
# ---------------------------------------------------------------------------


@router.post(
    "/{session_id}/attendance",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark attendance for a session (staff only)",
)
async def mark_attendance(
    session_id: str,
    payload: AttendanceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> AttendanceResponse:
    session_obj = await get_session(db, session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    if payload.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="session_id in body must match the path parameter.",
        )
    record = await create_attendance(db, payload)
    return AttendanceResponse.model_validate(record)


# ---------------------------------------------------------------------------
# GET /sessions/{session_id}/attendance
# ---------------------------------------------------------------------------


@router.get(
    "/{session_id}/attendance",
    response_model=Page[AttendanceResponse],
    summary="Get attendance records for a session (staff only)",
)
async def list_attendance(
    session_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> Page[AttendanceResponse]:
    session_obj = await get_session(db, session_id)
    if not session_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    items, total = await get_attendance_by_session(
        db, session_id, offset=page.offset, limit=page.limit
    )
    return Page(
        items=[AttendanceResponse.model_validate(r) for r in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ---------------------------------------------------------------------------
# PATCH /sessions/{session_id}/attendance/{attendance_id}
# ---------------------------------------------------------------------------


@router.patch(
    "/{session_id}/attendance/{attendance_id}",
    response_model=AttendanceResponse,
    summary="Update an attendance record (staff only)",
)
async def update_attendance_record(
    session_id: str,
    attendance_id: str,
    payload: AttendanceUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> AttendanceResponse:
    from app.crud import get_attendance  # local to avoid circular
    record = await get_attendance(db, attendance_id)
    if not record or record.session_id != session_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance record not found.",
        )
    updated = await update_attendance(db, record, payload)
    return AttendanceResponse.model_validate(updated)
