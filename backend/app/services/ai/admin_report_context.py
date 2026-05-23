from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any

from app.models import (Assessment, Enrollment, Submission, User, UserRole,
                        Workshop)
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession


def _window_bounds(date_from: date | None, date_to: date | None) -> tuple[datetime | None, datetime | None]:
    start = datetime.combine(date_from, time.min, tzinfo=timezone.utc) if date_from else None
    end = datetime.combine(date_to, time.max, tzinfo=timezone.utc) if date_to else None
    return start, end


async def build_admin_report_context(
    db: AsyncSession,
    *,
    institution_id: str | None,
    date_from: date | None,
    date_to: date | None,
) -> dict[str, Any]:
    start_dt, end_dt = _window_bounds(date_from, date_to)

    workshop_q = select(Workshop.id, Workshop.title)
    if institution_id:
        workshop_q = workshop_q.where(Workshop.institution_id == institution_id)
    workshop_rows = (await db.execute(workshop_q)).all()
    workshop_ids = [row.id for row in workshop_rows]
    workshop_titles = {row.id: row.title or "Workshop" for row in workshop_rows}

    users_q = select(
        func.sum(case((User.role == UserRole.STUDENT, 1), else_=0)).label("students"),
        func.sum(case((User.role == UserRole.EDUCATOR, 1), else_=0)).label("educators"),
        func.sum(case((User.role == UserRole.INSTITUTION_ADMIN, 1), else_=0)).label("institution_admins"),
    )
    if institution_id:
        users_q = users_q.where(User.institution_id == institution_id)
    user_counts = (await db.execute(users_q)).one()

    if not workshop_ids:
        return {
            "scope": "institution" if institution_id else "platform",
            "institution_id": institution_id,
            "data_window": {
                "start_date": date_from.isoformat() if date_from else None,
                "end_date": date_to.isoformat() if date_to else None,
            },
            "totals": {
                "workshops": 0,
                "students": int(user_counts.students or 0),
                "educators": int(user_counts.educators or 0),
                "institution_admins": int(user_counts.institution_admins or 0),
                "submissions": 0,
                "pass_rate_percentage": 0.0,
                "average_percentage": 0.0,
            },
            "top_workshops": [],
        }

    submissions_q = (
        select(
            func.count(Submission.id).label("submissions"),
            func.coalesce(func.avg(Submission.percentage), 0).label("avg_percentage"),
            func.sum(case((Submission.pass_fail == True, 1), else_=0)).label("passed"),  # noqa: E712
        )
        .join(Assessment, Assessment.id == Submission.assessment_id)
        .where(Assessment.workshop_id.in_(workshop_ids))
    )
    if start_dt:
        submissions_q = submissions_q.where(Submission.submitted_at >= start_dt)
    if end_dt:
        submissions_q = submissions_q.where(Submission.submitted_at <= end_dt)
    submissions_row = (await db.execute(submissions_q)).one()
    total_submissions = int(submissions_row.submissions or 0)
    passed = int(submissions_row.passed or 0)
    pass_rate = round((passed / total_submissions) * 100, 2) if total_submissions else 0.0

    top_workshops_q = (
        select(
            Assessment.workshop_id,
            func.coalesce(func.avg(Submission.percentage), 0).label("avg_percentage"),
            func.count(Submission.id).label("submissions"),
        )
        .join(Assessment, Assessment.id == Submission.assessment_id)
        .where(Assessment.workshop_id.in_(workshop_ids))
        .group_by(Assessment.workshop_id)
        .order_by(func.coalesce(func.avg(Submission.percentage), 0).desc())
        .limit(3)
    )
    if start_dt:
        top_workshops_q = top_workshops_q.where(Submission.submitted_at >= start_dt)
    if end_dt:
        top_workshops_q = top_workshops_q.where(Submission.submitted_at <= end_dt)
    top_rows = (await db.execute(top_workshops_q)).all()

    enrollments_q = select(
        func.count(Enrollment.id).label("total"),
        func.sum(case((Enrollment.status == "active", 1), else_=0)).label("active"),
        func.sum(case((Enrollment.status == "completed", 1), else_=0)).label("completed"),
        func.sum(case((Enrollment.status == "dropped", 1), else_=0)).label("dropped"),
    ).where(Enrollment.workshop_id.in_(workshop_ids))
    enrollment_row = (await db.execute(enrollments_q)).one()

    return {
        "scope": "institution" if institution_id else "platform",
        "institution_id": institution_id,
        "data_window": {
            "start_date": date_from.isoformat() if date_from else None,
            "end_date": date_to.isoformat() if date_to else None,
        },
        "totals": {
            "workshops": len(workshop_ids),
            "students": int(user_counts.students or 0),
            "educators": int(user_counts.educators or 0),
            "institution_admins": int(user_counts.institution_admins or 0),
            "submissions": total_submissions,
            "pass_rate_percentage": pass_rate,
            "average_percentage": round(float(submissions_row.avg_percentage or 0), 2),
            "enrollments_total": int(enrollment_row.total or 0),
            "enrollments_active": int(enrollment_row.active or 0),
            "enrollments_completed": int(enrollment_row.completed or 0),
            "enrollments_dropped": int(enrollment_row.dropped or 0),
        },
        "top_workshops": [
            {
                "workshop_id": row.workshop_id,
                "title": workshop_titles.get(row.workshop_id, "Workshop"),
                "average_percentage": round(float(row.avg_percentage or 0), 2),
                "submissions": int(row.submissions or 0),
            }
            for row in top_rows
        ],
    }
