from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import hashlib
from typing import Any
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.crud_ai_generation import create_ai_generation
from app.crud.crud_misc import create_notification
from app.models import (
    AIFeatureType,
    AIGenerationStatus,
    ScheduledAIReport,
    ScheduledAIReportRun,
    ScheduledReportFrequency,
    ScheduledReportRunStatus,
    ScheduledReportStatus,
    User,
)
from app.schemas.ai import AIGenerationCreate
from app.schemas.misc import NotificationCreate
from app.config import settings
from app.services.email import send_email


def _parse_time_of_day(value: str) -> time:
    raw = (value or "").strip()
    if not raw:
        return time(hour=9, minute=0)
    parts = raw.split(":")
    if len(parts) != 2:
        return time(hour=9, minute=0)
    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return time(hour=9, minute=0)
    hour = min(23, max(0, hour))
    minute = min(59, max(0, minute))
    return time(hour=hour, minute=minute)


def compute_next_run_at(schedule: ScheduledAIReport, *, from_dt: datetime) -> datetime:
    tz = ZoneInfo(schedule.timezone or "UTC")
    local_now = from_dt.astimezone(tz)
    tod = _parse_time_of_day(schedule.time_of_day)

    weekdays = schedule.weekdays or []
    weekdays = [int(v) for v in weekdays if isinstance(v, int) or (isinstance(v, str) and v.isdigit())]
    weekdays = [v for v in weekdays if 0 <= v <= 6]
    if schedule.frequency == ScheduledReportFrequency.WEEKLY and not weekdays:
        weekdays = [0]

    if schedule.frequency == ScheduledReportFrequency.DAILY:
        candidate_date = local_now.date()
        candidate = datetime.combine(candidate_date, tod, tzinfo=tz)
        if candidate <= local_now:
            candidate = datetime.combine(candidate_date + timedelta(days=1), tod, tzinfo=tz)
        return candidate.astimezone(timezone.utc)

    # weekly
    for offset in range(0, 14):
        d = local_now.date() + timedelta(days=offset)
        if d.weekday() not in weekdays:
            continue
        candidate = datetime.combine(d, tod, tzinfo=tz)
        if candidate <= local_now:
            continue
        return candidate.astimezone(timezone.utc)

    return (local_now + timedelta(days=7)).astimezone(timezone.utc)


def compute_window(*, schedule: ScheduledAIReport, now: datetime) -> tuple[date | None, date | None]:
    tz = ZoneInfo(schedule.timezone or "UTC")
    local_now = now.astimezone(tz)
    end = local_now.date()
    if schedule.window_days and schedule.window_days > 0:
        start = end - timedelta(days=int(schedule.window_days) - 1)
        return start, end
    return None, end


async def create_scheduled_report(db: AsyncSession, schedule: ScheduledAIReport) -> ScheduledAIReport:
    db.add(schedule)
    await db.flush()
    await db.refresh(schedule)
    return schedule


async def list_scheduled_reports(
    db: AsyncSession,
    *,
    institution_id: str | None,
    created_by_user_id: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[ScheduledAIReport], int]:
    q = select(ScheduledAIReport)
    if institution_id is not None:
        q = q.where(ScheduledAIReport.institution_id == institution_id)
    if created_by_user_id is not None:
        q = q.where(ScheduledAIReport.created_by_user_id == created_by_user_id)
    q = q.order_by(ScheduledAIReport.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(rows), int(total or 0)


async def get_scheduled_report(db: AsyncSession, schedule_id: str) -> ScheduledAIReport | None:
    return await db.get(ScheduledAIReport, schedule_id)


async def update_scheduled_report(
    db: AsyncSession,
    schedule: ScheduledAIReport,
    *,
    updates: dict[str, Any],
) -> ScheduledAIReport:
    for key, value in updates.items():
        setattr(schedule, key, value)
    await db.flush()
    await db.refresh(schedule)
    return schedule


async def list_scheduled_report_runs(
    db: AsyncSession,
    *,
    schedule_id: str,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[ScheduledAIReportRun], int]:
    q = select(ScheduledAIReportRun).where(ScheduledAIReportRun.schedule_id == schedule_id)
    q = q.order_by(ScheduledAIReportRun.due_at.desc())
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(rows), int(total or 0)


@dataclass(frozen=True)
class ClaimedRun:
    id: str
    ai_generation_id: str


async def claim_due_scheduled_runs(
    db: AsyncSession,
    *,
    now: datetime,
    lookahead_seconds: int,
) -> list[ClaimedRun]:
    lookahead_cutoff = now + timedelta(seconds=max(0, lookahead_seconds))

    q = (
        select(ScheduledAIReport)
        .where(ScheduledAIReport.status == ScheduledReportStatus.ACTIVE)
        .where(ScheduledAIReport.next_run_at.is_not(None))
        .where(ScheduledAIReport.next_run_at <= lookahead_cutoff)
        .order_by(ScheduledAIReport.next_run_at.asc())
        .limit(25)
    )
    schedules = (await db.execute(q)).scalars().all()
    claimed: list[ClaimedRun] = []
    if not schedules:
        return claimed

    for schedule in schedules:
        due_at = schedule.next_run_at or now
        date_from, date_to = compute_window(schedule=schedule, now=now)
        raw_prompt_input = {
            "institution_id": schedule.institution_id,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "focus_areas": schedule.focus_areas or [],
            "scheduled_report_id": schedule.id,
            "scheduled_due_at": (due_at.astimezone(timezone.utc).isoformat() if isinstance(due_at, datetime) else None),
        }

        fingerprint_source = f"scheduled:{schedule.id}:{due_at.astimezone(timezone.utc).isoformat()}"
        fingerprint = hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest()

        generation = await create_ai_generation(
            db,
            AIGenerationCreate(
                feature_type=AIFeatureType.ADMIN_REPORT,
                requester_user_id=schedule.created_by_user_id,
                institution_id=schedule.institution_id,
                source_entity_type="scheduled_report",
                source_entity_id=schedule.id,
                prompt_version=settings.AI_ADMIN_REPORT_PROMPT_VERSION,
                model_name=settings.GEMINI_MODEL_NAME,
                raw_prompt_input=raw_prompt_input,
                request_fingerprint=fingerprint,
                cache_expires_at=None,
            ),
        )

        run = ScheduledAIReportRun(
            schedule_id=schedule.id,
            ai_generation_id=generation.id,
            due_at=due_at,
            status=ScheduledReportRunStatus.PENDING,
        )
        db.add(run)

        schedule.last_run_at = due_at
        schedule.next_run_at = compute_next_run_at(schedule, from_dt=due_at + timedelta(seconds=1))

        await db.flush()
        await db.refresh(run)
        claimed.append(ClaimedRun(id=run.id, ai_generation_id=generation.id))

    return claimed


async def mark_scheduled_run_completed(
    db: AsyncSession,
    *,
    run_id: str,
    generation_id: str,
) -> None:
    run = await db.get(ScheduledAIReportRun, run_id)
    if not run:
        return
    run.status = ScheduledReportRunStatus.COMPLETED
    run.completed_at = datetime.now(timezone.utc)
    await db.flush()

    schedule = await db.get(ScheduledAIReport, run.schedule_id)
    if not schedule:
        return

    recipients = schedule.recipients or []
    resolved_user_ids: set[str] = set()
    resolved_emails: set[str] = set()
    for item in recipients:
        if not item:
            continue
        s = str(item).strip()
        if not s:
            continue
        if "@" in s:
            resolved_emails.add(s.lower())
        else:
            resolved_user_ids.add(s)

    if resolved_emails:
        users = (
            await db.execute(select(User).where(User.email.in_(list(resolved_emails))))
        ).scalars().all()
        for u in users:
            if u.id:
                resolved_user_ids.add(u.id)

    link = f"/reports/ai?report_id={generation_id}"
    message = f"Scheduled AI report is ready (run {run_id}). View: {link}"

    for uid in resolved_user_ids:
        try:
            await create_notification(
                db,
                NotificationCreate(user_id=uid, message=message),
            )
        except Exception:
            continue

    for email in resolved_emails:
        try:
            send_email(
                to_email=email,
                subject="Scheduled AI report is ready",
                body=f"{message}\n\nReport id: {generation_id}",
            )
        except Exception:
            continue


async def mark_scheduled_run_failed(
    db: AsyncSession,
    *,
    run_id: str,
    error_details: dict[str, Any],
) -> None:
    run = await db.get(ScheduledAIReportRun, run_id)
    if not run:
        return
    run.status = ScheduledReportRunStatus.FAILED
    run.error_details = error_details
    run.completed_at = datetime.now(timezone.utc)
    await db.flush()
