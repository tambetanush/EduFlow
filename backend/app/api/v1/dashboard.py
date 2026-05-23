from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.models import (
    Assessment,
    Certificate,
    Enrollment,
    Institution,
    Module,
    Submission,
    User,
    UserRole,
    Workshop,
)
from app.schemas.misc import (
    AdminDashboardStats,
    EducatorDashboardStats,
    StudentDashboardStats,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


@router.get(
    "/admin",
    response_model=AdminDashboardStats,
    summary="Admin dashboard summary stats (admin only)",
)
async def admin_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> AdminDashboardStats:
    total_institutions = (await db.execute(select(func.count()).select_from(Institution))).scalar_one()
    total_workshops = (await db.execute(select(func.count()).select_from(Workshop))).scalar_one()
    total_educators = (
        await db.execute(select(func.count()).select_from(User).where(User.role == UserRole.EDUCATOR))
    ).scalar_one()
    total_students = (
        await db.execute(select(func.count()).select_from(User).where(User.role == UserRole.STUDENT))
    ).scalar_one()
    certificates_issued = (await db.execute(select(func.count()).select_from(Certificate))).scalar_one()

    now = datetime.now(tz=timezone.utc)
    active_workshops = (
        await db.execute(
            select(func.count()).select_from(Workshop).where(
                and_(
                    func.coalesce(Workshop.start_date, now) <= now,
                    func.coalesce(Workshop.end_date, now) >= now,
                )
            )
        )
    ).scalar_one()

    return AdminDashboardStats(
        total_institutions=int(total_institutions or 0),
        total_workshops=int(total_workshops or 0),
        total_educators=int(total_educators or 0),
        total_students=int(total_students or 0),
        certificates_issued=int(certificates_issued or 0),
        active_workshops=int(active_workshops or 0),
    )


@router.get(
    "/student/{student_id}",
    response_model=StudentDashboardStats,
    summary="Student dashboard summary stats",
)
async def student_stats(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StudentDashboardStats:
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    enrolled_workshops = (
        await db.execute(select(func.count()).select_from(Enrollment).where(Enrollment.student_id == student_id))
    ).scalar_one()

    completed_assessments = (
        await db.execute(
            select(func.count()).select_from(Submission).where(
                and_(Submission.student_id == student_id, Submission.pass_fail.is_not(None))
            )
        )
    ).scalar_one()

    avg_percentage = (
        await db.execute(
            select(func.coalesce(func.avg(Submission.percentage), 0.0)).where(Submission.student_id == student_id)
        )
    ).scalar_one()

    certificates_earned = (
        await db.execute(select(func.count()).select_from(Certificate).where(Certificate.student_id == student_id))
    ).scalar_one()

    return StudentDashboardStats(
        enrolled_workshops=int(enrolled_workshops or 0),
        completed_assessments=int(completed_assessments or 0),
        average_score=float(round(float(avg_percentage or 0.0), 2)),
        certificates_earned=int(certificates_earned or 0),
    )


@router.get(
    "/educator",
    response_model=EducatorDashboardStats,
    summary="Educator/institution dashboard summary stats (staff)",
)
async def educator_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_STAFF)),
) -> EducatorDashboardStats:
    # We do not model explicit educator->workshop assignment; use institution scoping.
    inst_id = current_user.institution_id

    workshop_q = select(Workshop.id)
    if current_user.role != UserRole.ADMIN and inst_id:
        workshop_q = workshop_q.where(Workshop.institution_id == inst_id)

    workshop_ids = [row[0] for row in (await db.execute(workshop_q)).all()]
    assigned_workshops = len(workshop_ids)

    if not workshop_ids:
        return EducatorDashboardStats(
            assigned_workshops=0,
            materials_uploaded=0,
            active_assessments=0,
            pending_submissions=0,
        )

    module_rows = (
        await db.execute(select(Module.materials).where(Module.workshop_id.in_(workshop_ids)))
    ).all()
    materials_uploaded = 0
    for (materials,) in module_rows:
        if isinstance(materials, list):
            materials_uploaded += len(materials)

    active_assessments = (
        await db.execute(select(func.count()).select_from(Assessment).where(Assessment.workshop_id.in_(workshop_ids)))
    ).scalar_one()

    pending_submissions = (
        await db.execute(
            select(func.count())
            .select_from(Submission)
            .join(Assessment, Assessment.id == Submission.assessment_id)
            .where(and_(Assessment.workshop_id.in_(workshop_ids), Submission.pass_fail.is_(None)))
        )
    ).scalar_one()

    return EducatorDashboardStats(
        assigned_workshops=int(assigned_workshops),
        materials_uploaded=int(materials_uploaded),
        active_assessments=int(active_assessments or 0),
        pending_submissions=int(pending_submissions or 0),
    )
