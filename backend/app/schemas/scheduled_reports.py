from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models import ScheduledReportFrequency, ScheduledReportRunStatus, ScheduledReportStatus


class ScheduledReportCreateRequest(BaseModel):
    institution_id: str | None = None
    report_type: str = Field(default="admin_report")
    frequency: ScheduledReportFrequency = ScheduledReportFrequency.DAILY
    status: ScheduledReportStatus = ScheduledReportStatus.ACTIVE

    window_days: int = 7
    focus_areas: list[str] = Field(default_factory=list)
    recipients: list[str] = Field(default_factory=list)

    timezone: str = "UTC"
    time_of_day: str = "09:00"  # HH:MM
    weekdays: list[int] = Field(default_factory=list)  # weekly only, Mon=0


class ScheduledReportUpdateRequest(BaseModel):
    status: ScheduledReportStatus | None = None
    frequency: ScheduledReportFrequency | None = None
    window_days: int | None = None
    focus_areas: list[str] | None = None
    recipients: list[str] | None = None
    timezone: str | None = None
    time_of_day: str | None = None
    weekdays: list[int] | None = None


class ScheduledReportResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    created_by_user_id: str
    institution_id: str | None = None
    report_type: str
    frequency: ScheduledReportFrequency
    status: ScheduledReportStatus
    window_days: int
    focus_areas: list[str]
    recipients: list[str]
    timezone: str
    time_of_day: str
    weekdays: list[int]
    last_run_at: datetime | None = None
    next_run_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ScheduledReportRunResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    schedule_id: str
    ai_generation_id: str
    due_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: ScheduledReportRunStatus
    error_details: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

