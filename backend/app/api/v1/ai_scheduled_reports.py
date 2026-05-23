from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db, require_role
from app.config import settings
from app.crud.crud_scheduled_reports import (
    compute_next_run_at,
    get_scheduled_report,
    list_scheduled_report_runs,
    list_scheduled_reports,
    update_scheduled_report,
)
from app.models import ScheduledAIReport, ScheduledReportStatus, User, UserRole
from app.schemas.base import Page
from app.schemas.scheduled_reports import (
    ScheduledReportCreateRequest,
    ScheduledReportResponse,
    ScheduledReportRunResponse,
    ScheduledReportUpdateRequest,
)

router = APIRouter(prefix="/ai/scheduled-reports", tags=["ai-scheduled-reports"])


def _resolve_institution_id(payload_institution_id: str | None, current_user: User) -> str | None:
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Institution admin has no institution.")
        if payload_institution_id and payload_institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot schedule outside your institution scope.")
        return current_user.institution_id

    if current_user.role == UserRole.ADMIN:
        return payload_institution_id

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")


@router.post(
    "/",
    response_model=ScheduledReportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a scheduled AI report (admin / institution_admin)",
)
async def create_scheduled_report(
    payload: ScheduledReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> ScheduledReportResponse:
    institution_id = _resolve_institution_id(payload.institution_id, current_user)

    schedule = ScheduledAIReport(
        created_by_user_id=current_user.id,
        institution_id=institution_id,
        report_type=payload.report_type,
        frequency=payload.frequency,
        status=payload.status,
        window_days=max(0, int(payload.window_days or 0)),
        focus_areas=payload.focus_areas or [],
        recipients=payload.recipients or [],
        timezone=(payload.timezone or "UTC").strip() or "UTC",
        time_of_day=(payload.time_of_day or "09:00").strip() or "09:00",
        weekdays=payload.weekdays or [],
    )

    now = datetime.now(timezone.utc)
    schedule.next_run_at = compute_next_run_at(schedule, from_dt=now)

    db.add(schedule)
    await db.flush()
    await db.refresh(schedule)
    return ScheduledReportResponse.model_validate(schedule)


@router.get(
    "/",
    response_model=Page[ScheduledReportResponse],
    summary="List scheduled AI reports (scoped)",
)
async def list_schedules(
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> Page[ScheduledReportResponse]:
    institution_id = None
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Institution admin has no institution.")
        institution_id = current_user.institution_id
    rows, total = await list_scheduled_reports(
        db,
        institution_id=institution_id,
        offset=page.offset,
        limit=page.limit,
    )
    return Page(
        items=[ScheduledReportResponse.model_validate(r) for r in rows],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.patch(
    "/{schedule_id}",
    response_model=ScheduledReportResponse,
    summary="Update a scheduled AI report (pause/resume/update)",
)
async def patch_schedule(
    schedule_id: str,
    payload: ScheduledReportUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> ScheduledReportResponse:
    schedule = await get_scheduled_report(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found.")

    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id or schedule.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    updates = payload.model_dump(exclude_unset=True)
    schedule = await update_scheduled_report(db, schedule, updates=updates)

    if schedule.status == ScheduledReportStatus.ACTIVE and not schedule.next_run_at:
        schedule.next_run_at = compute_next_run_at(schedule, from_dt=datetime.now(timezone.utc))
        await db.flush()
        await db.refresh(schedule)

    return ScheduledReportResponse.model_validate(schedule)


@router.get(
    "/{schedule_id}/runs",
    response_model=Page[ScheduledReportRunResponse],
    summary="List runs for a scheduled AI report",
)
async def list_runs(
    schedule_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> Page[ScheduledReportRunResponse]:
    schedule = await get_scheduled_report(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schedule not found.")
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id or schedule.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    rows, total = await list_scheduled_report_runs(
        db,
        schedule_id=schedule_id,
        offset=page.offset,
        limit=page.limit,
    )
    return Page(
        items=[ScheduledReportRunResponse.model_validate(r) for r in rows],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )

