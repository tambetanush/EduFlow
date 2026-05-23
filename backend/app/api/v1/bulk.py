from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.crud.crud_user import create_user
from app.crud.crud_workshop import create_attendance, create_enrollment, get_session
from app.models import User, UserRole
from app.schemas.user import UserCreate
from app.schemas.workshop import AttendanceCreate, EnrollmentCreate, EnrollmentResponse

router = APIRouter(tags=["bulk"])


_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)
_ADMIN = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)


# ────────────────────────────────────────────────────────────────────────────
# Pydantic schemas for bulk request/response
# ────────────────────────────────────────────────────────────────────────────


class BulkEnrollmentItem(BaseModel):
    student_id: str
    workshop_id: str


class BulkEnrollmentRequest(BaseModel):
    enrollments: list[BulkEnrollmentItem]


class BulkEnrollmentResponse(BaseModel):
    created: int
    errors: list[dict]


class BulkAttendanceItem(BaseModel):
    session_id: str
    student_id: str
    status: str = "present"


class BulkAttendanceRequest(BaseModel):
    records: list[BulkAttendanceItem]


class BulkAttendanceResponse(BaseModel):
    created: int
    errors: list[dict]


class BulkStudentRow(BaseModel):
    """Schema for a single row from the CSV upload."""
    name: str
    email: str
    password: str = "ChangeMe@1234"
    phone: Optional[str] = None
    institution_id: Optional[str] = None


class BulkStudentUploadResponse(BaseModel):
    created: int
    skipped: int
    errors: list[dict]


# ────────────────────────────────────────────────────────────────────────────
# POST /students/bulk-upload   — CSV → create student accounts
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/students/bulk-upload",
    response_model=BulkStudentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a CSV to bulk-create student accounts (admin / institution_admin only)",
)
async def bulk_upload_students(
    file: UploadFile = File(..., description="CSV with columns: name, email, password (opt), phone (opt), institution_id (opt)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_ADMIN)),
) -> BulkStudentUploadResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted.",
        )

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")  # handle BOM-encoded CSVs too
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.DictReader(io.StringIO(text))
    required = {"name", "email"}
    if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="CSV must contain at minimum: name, email",
        )

    created = 0
    skipped = 0
    errors: list[dict] = []

    for row_num, raw_row in enumerate(reader, start=2):  # row 1 = header
        row: dict[str, Any] = {k.strip(): (v or "").strip() for k, v in raw_row.items()}

        # Basic validation
        if not row.get("name") or not row.get("email"):
            errors.append({"row": row_num, "reason": "Missing name or email", "data": row})
            continue

        # Institution admins can only create students in their own institution
        inst_id = row.get("institution_id") or None
        if current_user.role == UserRole.INSTITUTION_ADMIN:
            inst_id = current_user.institution_id

        data = UserCreate(
            name=row["name"],
            email=row["email"],
            password=row.get("password") or "ChangeMe@1234",
            role=UserRole.STUDENT,
            phone=row.get("phone") or None,
            institution_id=inst_id,
        )

        try:
            from app.crud.crud_user import get_user_by_email
            existing = await get_user_by_email(db, data.email)
            if existing:
                skipped += 1
                errors.append({"row": row_num, "reason": "Email already exists", "email": data.email})
                continue
            await create_user(db, data)
            created += 1
        except Exception as exc:
            errors.append({"row": row_num, "reason": str(exc), "email": row.get("email")})

    return BulkStudentUploadResponse(created=created, skipped=skipped, errors=errors)


# ────────────────────────────────────────────────────────────────────────────
# POST /enrollments/bulk
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/enrollments/bulk",
    response_model=BulkEnrollmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk enrol students in workshops (staff only)",
)
async def bulk_enroll(
    payload: BulkEnrollmentRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> BulkEnrollmentResponse:
    created = 0
    errors: list[dict] = []

    for i, item in enumerate(payload.enrollments):
        try:
            data = EnrollmentCreate(
                student_id=item.student_id,
                workshop_id=item.workshop_id,
            )
            await create_enrollment(db, data)
            created += 1
        except Exception as exc:
            errors.append({"index": i, "reason": str(exc), "item": item.model_dump()})

    return BulkEnrollmentResponse(created=created, errors=errors)


# ────────────────────────────────────────────────────────────────────────────
# POST /attendance/bulk
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/attendance/bulk",
    response_model=BulkAttendanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Bulk mark attendance for a session (staff only)",
)
async def bulk_attendance(
    payload: BulkAttendanceRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> BulkAttendanceResponse:
    created = 0
    errors: list[dict] = []

    for i, item in enumerate(payload.records):
        # Validate session exists once per unique session id (light optimisation)
        session_obj = await get_session(db, item.session_id)
        if not session_obj:
            errors.append({"index": i, "reason": f"Session {item.session_id} not found", "item": item.model_dump()})
            continue
        try:
            data = AttendanceCreate(
                session_id=item.session_id,
                student_id=item.student_id,
                status=item.status,
            )
            await create_attendance(db, data)
            created += 1
        except Exception as exc:
            errors.append({"index": i, "reason": str(exc), "item": item.model_dump()})

    return BulkAttendanceResponse(created=created, errors=errors)
