from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AIFeatureType, AIGeneration, AIGenerationStatus
from app.schemas.ai import AIGenerationCreate, AIGenerationUpdate


async def create_ai_generation(db: AsyncSession, data: AIGenerationCreate) -> AIGeneration:
    generation = AIGeneration(**data.model_dump())
    db.add(generation)
    await db.flush()
    await db.refresh(generation)
    return generation


async def get_ai_generation(db: AsyncSession, generation_id: str) -> AIGeneration | None:
    return await db.get(AIGeneration, generation_id)


async def update_ai_generation(
    db: AsyncSession,
    generation: AIGeneration,
    data: AIGenerationUpdate,
) -> AIGeneration:
    if data.status is not None:
        generation.status = data.status
    if data.raw_model_output is not None:
        generation.raw_model_output = data.raw_model_output
    if data.parsed_output_json is not None:
        generation.parsed_output_json = data.parsed_output_json
    if data.error_details is not None:
        generation.error_details = data.error_details
    if data.retry_count is not None:
        generation.retry_count = data.retry_count
    if data.cache_expires_at is not None:
        generation.cache_expires_at = data.cache_expires_at
    if data.token_usage is not None:
        generation.input_tokens = data.token_usage.input_tokens
        generation.output_tokens = data.token_usage.output_tokens
        generation.total_tokens = data.token_usage.total_tokens

    await db.flush()
    await db.refresh(generation)
    return generation


async def find_generation_by_idempotency_key(
    db: AsyncSession,
    *,
    user_id: str,
    feature_type: AIFeatureType,
    idempotency_key: str,
) -> AIGeneration | None:
    stmt = (
        select(AIGeneration)
        .where(AIGeneration.requester_user_id == user_id)
        .where(AIGeneration.feature_type == feature_type)
        .where(AIGeneration.idempotency_key == idempotency_key)
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def find_active_generation_by_fingerprint(
    db: AsyncSession,
    *,
    feature_type: AIFeatureType,
    request_fingerprint: str,
) -> AIGeneration | None:
    stmt = (
        select(AIGeneration)
        .where(AIGeneration.feature_type == feature_type)
        .where(AIGeneration.request_fingerprint == request_fingerprint)
        .where(AIGeneration.status.in_([AIGenerationStatus.PENDING, AIGenerationStatus.PROCESSING]))
        .order_by(AIGeneration.created_at.desc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def find_cached_completed_generation(
    db: AsyncSession,
    *,
    feature_type: AIFeatureType,
    request_fingerprint: str,
    now: datetime | None = None,
) -> AIGeneration | None:
    now = now or datetime.now(timezone.utc)
    stmt = (
        select(AIGeneration)
        .where(AIGeneration.feature_type == feature_type)
        .where(AIGeneration.request_fingerprint == request_fingerprint)
        .where(AIGeneration.status == AIGenerationStatus.COMPLETED)
        .where(AIGeneration.cache_expires_at.is_not(None))
        .where(AIGeneration.cache_expires_at > now)
        .order_by(AIGeneration.updated_at.desc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def list_ai_generations(
    db: AsyncSession,
    *,
    feature_type: AIFeatureType | None = None,
    institution_id: str | None = None,
    requester_user_id: str | None = None,
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[AIGeneration], int]:
    q = select(AIGeneration)
    if feature_type is not None:
        q = q.where(AIGeneration.feature_type == feature_type)
    if institution_id is not None:
        q = q.where(AIGeneration.institution_id == institution_id)
    if requester_user_id is not None:
        q = q.where(AIGeneration.requester_user_id == requester_user_id)

    q = q.order_by(AIGeneration.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return list(items), int(total or 0)


async def fail_stale_active_generations(
    db: AsyncSession,
    *,
    feature_type: AIFeatureType,
    stale_after_seconds: int,
    request_fingerprint: str | None = None,
    now: datetime | None = None,
) -> int:
    if stale_after_seconds <= 0:
        return 0

    now = now or datetime.now(timezone.utc)
    stale_cutoff = now - timedelta(seconds=stale_after_seconds)
    stmt = (
        update(AIGeneration)
        .where(AIGeneration.feature_type == feature_type)
        .where(AIGeneration.status.in_([AIGenerationStatus.PENDING, AIGenerationStatus.PROCESSING]))
        .where(AIGeneration.updated_at < stale_cutoff)
        .values(
            status=AIGenerationStatus.FAILED,
            error_details={
                "error_type": "StaleGenerationTimeout",
                "message": "Generation marked failed after exceeding stale timeout.",
            },
            updated_at=now,
        )
    )
    if request_fingerprint is not None:
        stmt = stmt.where(AIGeneration.request_fingerprint == request_fingerprint)

    result = await db.execute(stmt)
    return int(result.rowcount or 0)
