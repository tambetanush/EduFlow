"""
app/crud/crud_analytics.py
--------------------------
Raw aggregation queries powering the analytics dashboard.
All functions return plain Python dicts/dataclasses — no ORM model re-fetch needed.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Assessment,
    Attendance,
    Enrollment,
    Session,
    Submission,
    Workshop,
)


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────


def _pct(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


# ────────────────────────────────────────────────────────────────────────────
# Student Analytics
# ────────────────────────────────────────────────────────────────────────────


async def get_student_analytics(
    db: AsyncSession, student_id: str
) -> dict[str, Any]:
    """Return performance trends, average scores and attendance % for a student."""

    # ── Submission stats ──────────────────────────────────────────────────
    sub_q = select(
        func.count(Submission.id).label("total_submissions"),
        func.coalesce(func.avg(Submission.score), 0).label("avg_score"),
        func.coalesce(func.avg(Submission.percentage), 0).label("avg_percentage"),
        func.sum(case((Submission.pass_fail == True, 1), else_=0)).label("passed"),  # noqa: E712
        func.sum(case((Submission.pass_fail == False, 1), else_=0)).label("failed"),  # noqa: E712
    ).where(Submission.student_id == student_id)

    sub_row = (await db.execute(sub_q)).one()

    # ── Per-assessment score trend (latest 20 submissions) ────────────────
    trend_q = (
        select(
            Submission.assessment_id,
            Submission.score,
            Submission.percentage,
            Submission.pass_fail,
            Submission.submitted_at,
        )
        .where(Submission.student_id == student_id)
        .order_by(Submission.submitted_at.asc())
        .limit(20)
    )
    trend_rows = (await db.execute(trend_q)).all()
    score_trend = [
        {
            "assessment_id": r.assessment_id,
            "score": r.score,
            "percentage": r.percentage,
            "pass_fail": r.pass_fail,
            "submitted_at": r.submitted_at.isoformat() if r.submitted_at else None,
        }
        for r in trend_rows
    ]

    # ── Attendance stats ──────────────────────────────────────────────────
    att_q = select(
        func.count(Attendance.id).label("total_sessions"),
        func.sum(
            case((Attendance.status == "present", 1), else_=0)
        ).label("present_count"),
        func.sum(
            case((Attendance.status == "late", 1), else_=0)
        ).label("late_count"),
    ).where(Attendance.student_id == student_id)

    att_row = (await db.execute(att_q)).one()
    total_sessions = att_row.total_sessions or 0
    present = att_row.present_count or 0
    late = att_row.late_count or 0

    # ── Enrollment stats ──────────────────────────────────────────────────
    enr_q = select(func.count(Enrollment.id)).where(
        Enrollment.student_id == student_id
    )
    enrolled_count = (await db.execute(enr_q)).scalar_one() or 0

    return {
        "student_id": student_id,
        "enrolled_workshops": enrolled_count,
        "assessment": {
            "total_submissions": sub_row.total_submissions,
            "avg_score": round(float(sub_row.avg_score), 2),
            "avg_percentage": round(float(sub_row.avg_percentage), 2),
            "passed": int(sub_row.passed or 0),
            "failed": int(sub_row.failed or 0),
            "score_trend": score_trend,
        },
        "attendance": {
            "total_sessions": total_sessions,
            "present": present,
            "late": late,
            "absent": total_sessions - present - late,
            "attendance_percentage": _pct(present + late, total_sessions),
        },
    }


# ────────────────────────────────────────────────────────────────────────────
# Student Attendance Detail
# ────────────────────────────────────────────────────────────────────────────


async def get_student_attendance(
    db: AsyncSession, student_id: str
) -> dict[str, Any]:
    """Return a chronological list of attendance records for a student."""
    q = (
        select(
            Attendance.id,
            Attendance.session_id,
            Attendance.status,
            Session.title.label("session_title"),
            Session.start_time,
            Workshop.id.label("workshop_id"),
            Workshop.title.label("workshop_title"),
        )
        .join(Session, Session.id == Attendance.session_id)
        .join(Workshop, Workshop.id == Session.workshop_id)
        .where(Attendance.student_id == student_id)
        .order_by(Session.start_time.asc())
    )
    rows = (await db.execute(q)).all()

    records = [
        {
            "attendance_id": r.id,
            "session_id": r.session_id,
            "session_title": r.session_title,
            "start_time": r.start_time.isoformat() if r.start_time else None,
            "workshop_id": r.workshop_id,
            "workshop_title": r.workshop_title,
            "status": r.status,
        }
        for r in rows
    ]

    # Summary counts
    present = sum(1 for r in records if r["status"] == "present")
    late = sum(1 for r in records if r["status"] == "late")
    total = len(records)

    return {
        "student_id": student_id,
        "total_sessions": total,
        "present": present,
        "late": late,
        "absent": total - present - late,
        "attendance_percentage": _pct(present + late, total),
        "records": records,
    }


# ────────────────────────────────────────────────────────────────────────────
# Workshop / Cohort Analytics
# ────────────────────────────────────────────────────────────────────────────


async def get_workshop_analytics(
    db: AsyncSession, workshop_id: str
) -> dict[str, Any]:
    """Return cohort-level averages for a workshop."""

    # ── Enrollment stats ──────────────────────────────────────────────────
    enr_q = select(
        func.count(Enrollment.id).label("total_enrolled"),
        func.sum(
            case((Enrollment.status == "completed", 1), else_=0)
        ).label("completed"),
        func.sum(
            case((Enrollment.status == "dropped", 1), else_=0)
        ).label("dropped"),
    ).where(Enrollment.workshop_id == workshop_id)
    enr_row = (await db.execute(enr_q)).one()

    # ── Assessment stats (all assessments in this workshop) ───────────────
    assess_q = select(Assessment.id).where(Assessment.workshop_id == workshop_id)
    assess_ids = [(r[0]) for r in (await db.execute(assess_q)).all()]

    sub_stats: dict[str, Any] = {
        "total_submissions": 0,
        "avg_score": 0.0,
        "avg_percentage": 0.0,
        "pass_rate_percentage": 0.0,
    }

    if assess_ids:
        sub_q = select(
            func.count(Submission.id).label("total"),
            func.coalesce(func.avg(Submission.score), 0).label("avg_score"),
            func.coalesce(func.avg(Submission.percentage), 0).label("avg_pct"),
            func.sum(case((Submission.pass_fail == True, 1), else_=0)).label("passed"),  # noqa: E712
        ).where(Submission.assessment_id.in_(assess_ids))
        sub_row = (await db.execute(sub_q)).one()
        total = sub_row.total or 0
        passed = int(sub_row.passed or 0)
        sub_stats = {
            "total_submissions": total,
            "avg_score": round(float(sub_row.avg_score), 2),
            "avg_percentage": round(float(sub_row.avg_pct), 2),
            "pass_rate_percentage": _pct(passed, total),
        }

    # ── Attendance stats (all sessions in this workshop) ──────────────────
    sess_q = select(Session.id).where(Session.workshop_id == workshop_id)
    sess_ids = [r[0] for r in (await db.execute(sess_q)).all()]

    att_stats: dict[str, Any] = {
        "total_attendance_records": 0,
        "avg_attendance_percentage": 0.0,
    }

    if sess_ids:
        att_q = select(
            func.count(Attendance.id).label("total"),
            func.sum(
                case((Attendance.status == "present", 1), else_=0)
            ).label("present"),
            func.sum(
                case((Attendance.status == "late", 1), else_=0)
            ).label("late"),
        ).where(Attendance.session_id.in_(sess_ids))
        att_row = (await db.execute(att_q)).one()
        total_att = att_row.total or 0
        present_att = (att_row.present or 0) + (att_row.late or 0)
        att_stats = {
            "total_attendance_records": total_att,
            "avg_attendance_percentage": _pct(present_att, total_att),
        }

    return {
        "workshop_id": workshop_id,
        "enrollment": {
            "total_enrolled": enr_row.total_enrolled or 0,
            "completed": int(enr_row.completed or 0),
            "dropped": int(enr_row.dropped or 0),
            "active": (enr_row.total_enrolled or 0)
            - int(enr_row.completed or 0)
            - int(enr_row.dropped or 0),
        },
        "assessment": sub_stats,
        "attendance": att_stats,
    }
