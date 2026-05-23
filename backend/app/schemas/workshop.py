from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_validator

from app.models import EnrollmentStatus


# ---------------------------------------------------------------------------
# Material (embedded in Module.materials JSON column)
# ---------------------------------------------------------------------------


class MaterialItem(BaseModel):
    id: str
    title: str
    type: Literal["video", "pdf", "text", "link"]
    content: str
    created_at: Optional[str] = None


class MaterialItemCreate(BaseModel):
    title: str
    type: Literal["video", "pdf", "text", "link"]
    content: str


class MaterialItemUpdate(BaseModel):
    """Partial update schema for a single material embedded in Module.materials."""
    title: Optional[str] = None
    type: Optional[Literal["video", "pdf", "text", "link"]] = None
    content: Optional[str] = None


class ModuleReorderItem(BaseModel):
    """Single entry in a batch reorder request."""
    module_id: str
    order_index: int


class ModuleReorderRequest(BaseModel):
    """Body for PATCH /modules/reorder — batch set order_index."""
    items: list[ModuleReorderItem]


# ---------------------------------------------------------------------------
# Workshop
# ---------------------------------------------------------------------------


class WorkshopCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    institution_id: Optional[str] = None


class WorkshopUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    institution_id: Optional[str] = None


class WorkshopResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    title: Optional[str]
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    institution_id: Optional[str]
    enrollment_count: int = 0


class WorkshopEducatorProfileResponse(BaseModel):
    workshop_id: str
    educator_id: Optional[str] = None
    name: str
    email: str
    department: str
    institution: str
    bio: str


# ---------------------------------------------------------------------------
# Module
# ---------------------------------------------------------------------------


class ModuleCreate(BaseModel):
    workshop_id: str
    title: str
    order_index: int = 0
    materials: list[MaterialItem] = []


class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    order_index: Optional[int] = None
    materials: Optional[list[MaterialItem]] = None


class ModuleResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    workshop_id: Optional[str]
    title: Optional[str]
    order_index: Optional[int]
    materials: list[MaterialItem] = []

    @field_validator("materials", mode="before")
    @classmethod
    def coerce_materials(cls, v: object) -> list[MaterialItem]:
        if v is None:
            return []
        if isinstance(v, list):
            return [MaterialItem(**item) if isinstance(item, dict) else item for item in v]
        return v  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------


class EnrollmentCreate(BaseModel):
    student_id: str
    workshop_id: str


class EnrollmentUpdate(BaseModel):
    status: Optional[EnrollmentStatus] = None


class EnrollmentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    student_id: Optional[str]
    workshop_id: Optional[str]
    status: Optional[EnrollmentStatus]
    enrolled_at: Optional[datetime]


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------


class SessionCreate(BaseModel):
    workshop_id: str
    title: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class SessionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    workshop_id: Optional[str]
    title: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]


# ---------------------------------------------------------------------------
# Attendance
# ---------------------------------------------------------------------------


class AttendanceCreate(BaseModel):
    session_id: str
    student_id: str
    status: str  # "present" | "absent" | "late" — kept flexible


class AttendanceUpdate(BaseModel):
    status: Optional[str] = None


class AttendanceResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    session_id: Optional[str]
    student_id: Optional[str]
    status: Optional[str]
