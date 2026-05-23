from __future__ import annotations

from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Attendance, Enrollment, Session, Workshop, Module
from app.schemas.workshop import (
    AttendanceCreate,
    AttendanceUpdate,
    EnrollmentCreate,
    EnrollmentUpdate,
    ModuleCreate,
    ModuleUpdate,
    SessionCreate,
    SessionUpdate,
    WorkshopCreate,
    WorkshopUpdate,
)


# ---------------------------------------------------------------------------
# Workshop CRUD
# ---------------------------------------------------------------------------


async def create_workshop(db: AsyncSession, data: WorkshopCreate) -> Workshop:
    workshop = Workshop(**data.model_dump())
    db.add(workshop)
    await db.flush()
    await db.refresh(workshop)
    return workshop


async def get_workshop(db: AsyncSession, workshop_id: str) -> Optional[Workshop]:
    return await db.get(Workshop, workshop_id)


async def get_workshops(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 100,
    institution_id: Optional[str] = None,
) -> Tuple[Sequence[Workshop], int]:
    """Return (workshops, total_count). Optionally filter by institution."""
    q = select(Workshop)
    if institution_id is not None:
        q = q.where(Workshop.institution_id == institution_id)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def get_workshops_by_institution(
    db: AsyncSession, institution_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Workshop], int]:
    """Return (workshops, total_count) for a given institution."""
    q = select(Workshop).where(Workshop.institution_id == institution_id)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def update_workshop(
    db: AsyncSession, workshop: Workshop, data: WorkshopUpdate
) -> Workshop:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(workshop, field, value)
    await db.flush()
    await db.refresh(workshop)
    return workshop


async def delete_workshop(db: AsyncSession, workshop: Workshop) -> None:
    await db.delete(workshop)
    await db.flush()


# ---------------------------------------------------------------------------
# Module CRUD
# ---------------------------------------------------------------------------


async def create_module(db: AsyncSession, data: ModuleCreate) -> Module:
    payload = data.model_dump()
    # Serialise MaterialItem sub-models to plain dicts for the JSON column
    payload["materials"] = [m.model_dump() for m in data.materials]
    module = Module(**payload)
    db.add(module)
    await db.flush()
    await db.refresh(module)
    return module


async def get_module(db: AsyncSession, module_id: str) -> Optional[Module]:
    return await db.get(Module, module_id)


async def get_modules_by_workshop(
    db: AsyncSession, workshop_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Module], int]:
    """Return (modules, total_count) ordered by order_index."""
    q = select(Module).where(Module.workshop_id == workshop_id).order_by(Module.order_index)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def update_module(
    db: AsyncSession, module: Module, data: ModuleUpdate
) -> Module:
    payload = data.model_dump(exclude_unset=True)
    if "materials" in payload and payload["materials"] is not None:
        payload["materials"] = [
            m.model_dump() if hasattr(m, "model_dump") else m
            for m in payload["materials"]
        ]
    for field, value in payload.items():
        setattr(module, field, value)
    await db.flush()
    await db.refresh(module)
    return module


async def delete_module(db: AsyncSession, module: Module) -> None:
    await db.delete(module)
    await db.flush()


# ---------------------------------------------------------------------------
# Enrollment CRUD
# ---------------------------------------------------------------------------


async def create_enrollment(
    db: AsyncSession, data: EnrollmentCreate
) -> Enrollment:
    enrollment = Enrollment(**data.model_dump())
    db.add(enrollment)
    await db.flush()
    await db.refresh(enrollment)
    return enrollment


async def get_enrollment(
    db: AsyncSession, enrollment_id: str
) -> Optional[Enrollment]:
    return await db.get(Enrollment, enrollment_id)


async def get_enrollments_by_student(
    db: AsyncSession, student_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Enrollment], int]:
    """Return (enrollments, total_count) for a student."""
    q = select(Enrollment).where(Enrollment.student_id == student_id)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def get_enrollments_by_workshop(
    db: AsyncSession, workshop_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Enrollment], int]:
    """Return (enrollments, total_count) for a workshop."""
    q = select(Enrollment).where(Enrollment.workshop_id == workshop_id)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def update_enrollment(
    db: AsyncSession, enrollment: Enrollment, data: EnrollmentUpdate
) -> Enrollment:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(enrollment, field, value)
    await db.flush()
    await db.refresh(enrollment)
    return enrollment


async def delete_enrollment(db: AsyncSession, enrollment: Enrollment) -> None:
    await db.delete(enrollment)
    await db.flush()


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------


async def create_session(db: AsyncSession, data: SessionCreate) -> Session:
    session_obj = Session(**data.model_dump())
    db.add(session_obj)
    await db.flush()
    await db.refresh(session_obj)
    return session_obj


async def get_session(db: AsyncSession, session_id: str) -> Optional[Session]:
    return await db.get(Session, session_id)


async def get_sessions_by_workshop(
    db: AsyncSession, workshop_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Session], int]:
    """Return (sessions, total_count) for a workshop."""
    q = select(Session).where(Session.workshop_id == workshop_id)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def update_session(
    db: AsyncSession, session_obj: Session, data: SessionUpdate
) -> Session:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(session_obj, field, value)
    await db.flush()
    await db.refresh(session_obj)
    return session_obj


async def delete_session(db: AsyncSession, session_obj: Session) -> None:
    await db.delete(session_obj)
    await db.flush()


# ---------------------------------------------------------------------------
# Attendance CRUD
# ---------------------------------------------------------------------------


async def create_attendance(
    db: AsyncSession, data: AttendanceCreate
) -> Attendance:
    record = Attendance(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_attendance(
    db: AsyncSession, attendance_id: str
) -> Optional[Attendance]:
    return await db.get(Attendance, attendance_id)


async def get_attendance_by_session(
    db: AsyncSession, session_id: str, *, offset: int = 0, limit: int = 200
) -> Tuple[Sequence[Attendance], int]:
    """Return (attendance_records, total_count) for a session."""
    q = select(Attendance).where(Attendance.session_id == session_id)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def update_attendance(
    db: AsyncSession, record: Attendance, data: AttendanceUpdate
) -> Attendance:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


async def delete_attendance(db: AsyncSession, record: Attendance) -> None:
    await db.delete(record)
    await db.flush()
