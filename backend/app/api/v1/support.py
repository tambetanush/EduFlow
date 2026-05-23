from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

from app.api.deps import PaginationParams, get_db, require_role
from app.config import settings
from app.crud.crud_ai_generation import (get_ai_generation,
                                         list_ai_generations,
                                         update_ai_generation)
from app.crud.crud_audit import create_audit_log, list_audit_logs
from app.crud.crud_rate_limit_events import list_rate_limit_events
from app.models import (AIFeatureType, AIGeneration, AIGenerationStatus, User,
                        UserRole)
from app.schemas.ai import AIGenerationUpdate
from app.schemas.base import Page
from app.schemas.support import (AuditLogResponse, CacheStatsResponse,
                                 RateLimitEventResponse, SupportConfigResponse,
                                 SupportJobDetailResponse, SupportJobListItem,
                                 SupportRerunResponse)
from fastapi import (APIRouter, BackgroundTasks, Depends, HTTPException, Query,
                     status)
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/support", tags=["support"])


def _support_only():
    return require_role(UserRole.TECHNICAL_SUPPORT)


@router.get(
    "/config",
    response_model=SupportConfigResponse,
    summary="View runtime configuration (sanitized)",
)
async def get_support_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(_support_only()),
) -> SupportConfigResponse:
    await create_audit_log(
        db,
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        action="support.config.view",
    )
    return SupportConfigResponse(
        smtp_configured=bool(settings.SMTP_HOST.strip() and settings.SMTP_FROM_EMAIL.strip()),

        ai_max_retries=settings.AI_MAX_RETRIES,
        ai_retry_base_delay_seconds=settings.AI_RETRY_BASE_DELAY_SECONDS,
        admin_report_rate_limits={
            "user": {
                "max": settings.AI_ADMIN_REPORT_USER_RATE_LIMIT,
                "window_seconds": settings.AI_ADMIN_REPORT_RATE_LIMIT_WINDOW_SECONDS,
            },
            "institution": {
                "max": settings.AI_ADMIN_REPORT_INSTITUTION_RATE_LIMIT,
                "window_seconds": settings.AI_ADMIN_REPORT_RATE_LIMIT_WINDOW_SECONDS,
            },
        },
        student_explanation_rate_limits={
            "user": {
                "max": settings.AI_STUDENT_EXPLANATION_USER_RATE_LIMIT,
                "window_seconds": settings.AI_STUDENT_EXPLANATION_RATE_LIMIT_WINDOW_SECONDS,
            }
        },
    )


@router.get(
    "/jobs",
    response_model=Page[SupportJobListItem],
    summary="List async AI jobs (sanitized)",
)
async def list_jobs(
    page: PaginationParams = Depends(),
    status_filter: str | None = Query(default=None, alias="status"),
    feature_type: str | None = Query(default=None),
    institution_id: str | None = Query(default=None),
    requester_user_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(_support_only()),
) -> Page[SupportJobListItem]:
    await create_audit_log(
        db,
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        action="support.jobs.list",
        metadata_={
            "status": status_filter,
            "feature_type": feature_type,
            "institution_id": institution_id,
            "requester_user_id": requester_user_id,
        },
    )

    ft = None
    if feature_type:
        try:
            ft = AIFeatureType(feature_type)
        except Exception:
            ft = None

    rows, total = await list_ai_generations(
        db,
        feature_type=ft,
        institution_id=institution_id,
        requester_user_id=requester_user_id,
        offset=page.offset,
        limit=page.limit,
    )

    if status_filter:
        rows = [r for r in rows if r.status.value == status_filter]
        total = len(rows)

    items: list[SupportJobListItem] = []
    for r in rows:
        items.append(
            SupportJobListItem(
                id=r.id,
                feature_type=r.feature_type,
                status=r.status,
                requester_user_id=r.requester_user_id,
                institution_id=r.institution_id,
                source_entity_type=r.source_entity_type,
                source_entity_id=r.source_entity_id,
                prompt_version=r.prompt_version,
                model_name=r.model_name,
                retry_count=r.retry_count,
                error_details=r.error_details,
                created_at=r.created_at,
                updated_at=r.updated_at,
                progress=None,
            )
        )

    return Page(items=items, total=total, offset=page.offset, limit=page.limit)


@router.get(
    "/jobs/{generation_id}",
    response_model=SupportJobDetailResponse,
    summary="Get async AI job details (sanitized)",
)
async def get_job_detail(
    generation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(_support_only()),
) -> SupportJobDetailResponse:
    await create_audit_log(
        db,
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        action="support.jobs.get",
        target_type="ai_generation",
        target_id=generation_id,
    )

    row = await get_ai_generation(db, generation_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")

    return SupportJobDetailResponse(
        id=row.id,
        feature_type=row.feature_type,
        status=row.status,
        requester_user_id=row.requester_user_id,
        institution_id=row.institution_id,
        source_entity_type=row.source_entity_type,
        source_entity_id=row.source_entity_id,
        prompt_version=row.prompt_version,
        model_name=row.model_name,
        retry_count=row.retry_count,
        error_details=row.error_details,
        created_at=row.created_at,
        updated_at=row.updated_at,
        progress=None,
        error_trace=None,
    )


@router.post(
    "/jobs/{generation_id}/rerun",
    response_model=SupportRerunResponse,
    summary="Re-run a failed AI generation task",
)
async def rerun_job(
    generation_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(_support_only()),
) -> SupportRerunResponse:
    row = await get_ai_generation(db, generation_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    if row.status != AIGenerationStatus.FAILED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only FAILED jobs can be re-run.")

    await create_audit_log(
        db,
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        action="support.jobs.rerun",
        target_type="ai_generation",
        target_id=generation_id,
        metadata_={"previous_error_type": (row.error_details or {}).get("error_type")},
    )

    await update_ai_generation(
        db,
        row,
        AIGenerationUpdate(
            status=AIGenerationStatus.PENDING,
            error_details={},
        ),
    )

    if row.feature_type == AIFeatureType.ADMIN_REPORT:
        from app.jobs.tasks import generate_admin_ai_report
        background_tasks.add_task(generate_admin_ai_report, generation_id=row.id)
    elif row.feature_type == AIFeatureType.STUDENT_EXPLANATION:
        from app.jobs.tasks import generate_student_explanation
        background_tasks.add_task(generate_student_explanation, generation_id=row.id)

    return SupportRerunResponse(
        generation_id=row.id,
        status=AIGenerationStatus.PENDING,
        queued=True,
        message="Job re-queued in background.",
    )


@router.get(
    "/audit-logs",
    response_model=Page[AuditLogResponse],
    summary="View audit logs",
)
async def get_audit_logs(
    page: PaginationParams = Depends(),
    action: str | None = Query(default=None),
    since_hours: int = Query(default=24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(_support_only()),
) -> Page[AuditLogResponse]:
    since = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    rows, total = await list_audit_logs(
        db,
        action=action,
        since=since,
        offset=page.offset,
        limit=page.limit,
    )
    await create_audit_log(
        db,
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        action="support.audit.list",
        metadata_={"since_hours": since_hours, "action": action},
    )
    return Page(
        items=[AuditLogResponse.model_validate(r) for r in rows],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.get(
    "/rate-limit-events",
    response_model=Page[RateLimitEventResponse],
    summary="View rate-limit events",
)
async def get_rate_limit_events(
    page: PaginationParams = Depends(),
    key_prefix: str | None = Query(default=None),
    allowed: bool | None = Query(default=None),
    since_hours: int = Query(default=24, ge=1, le=720),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(_support_only()),
) -> Page[RateLimitEventResponse]:
    since = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    rows, total = await list_rate_limit_events(
        db,
        key_prefix=key_prefix,
        allowed=allowed,
        since=since,
        offset=page.offset,
        limit=page.limit,
    )
    await create_audit_log(
        db,
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        action="support.rate_limits.list",
        metadata_={"key_prefix": key_prefix, "allowed": allowed, "since_hours": since_hours},
    )
    return Page(
        items=[RateLimitEventResponse.model_validate(r) for r in rows],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.get(
    "/cache-stats",
    response_model=CacheStatsResponse,
    summary="View cache stats",
)
async def get_cache_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(_support_only()),
) -> CacheStatsResponse:
    await create_audit_log(
        db,
        actor_user_id=current_user.id,
        actor_role=current_user.role.value,
        action="support.cache_stats.view",
    )
    now = datetime.now(timezone.utc)

    total_generations = (
        await db.execute(select(func.count()).select_from(AIGeneration))
    ).scalar_one()

    cached_admin = (
        await db.execute(
            select(func.count())
            .select_from(AIGeneration)
            .where(AIGeneration.feature_type == AIFeatureType.ADMIN_REPORT)
            .where(AIGeneration.status == AIGenerationStatus.COMPLETED)
            .where(AIGeneration.cache_expires_at.is_not(None))
            .where(AIGeneration.cache_expires_at > now)
        )
    ).scalar_one()

    cached_expl = (
        await db.execute(
            select(func.count())
            .select_from(AIGeneration)
            .where(AIGeneration.feature_type == AIFeatureType.STUDENT_EXPLANATION)
            .where(AIGeneration.status == AIGenerationStatus.COMPLETED)
            .where(AIGeneration.cache_expires_at.is_not(None))
            .where(AIGeneration.cache_expires_at > now)
        )
    ).scalar_one()

    return CacheStatsResponse(
        now=now.isoformat(),
        ai_generations={
            "total": int(total_generations or 0),
            "cached_completed": {
                "admin_report": int(cached_admin or 0),
                "student_explanation": int(cached_expl or 0),
            },
        },
    )

