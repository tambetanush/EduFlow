from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.crud.crud_ai_generation import (
    create_ai_generation,
    find_active_generation_by_fingerprint,
    find_cached_completed_generation,
    update_ai_generation,
)
from app.models import (
    AIFeatureType,
    AIGenerationStatus,
    Base,
    Institution,
    User,
    UserRole,
)
from app.schemas.ai import AIGenerationCreate, AIGenerationUpdate, AITokenUsage
from app.services.ai.cache import (
    build_admin_report_request_fingerprint,
    compute_cache_expiry,
)
from app.services.ai.rate_limit import InMemorySlidingWindowRateLimiter, RateLimitRule
from app.services.ai.rate_limit import (
    DatabaseFixedWindowRateLimiter,
    RateLimitViolation,
    consume_rate_limit_or_raise,
)
from app.services.ai.validation import (
    StructuredOutputValidationError,
    validate_admin_report_output,
)


@pytest.fixture
async def db_session():
    db_path = Path("unit_testing") / f"ut_ai_infra_{uuid4().hex}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_local() as session:
        session.add(
            Institution(
                id="inst-1",
                name="Institution One",
                address="Address",
            )
        )
        session.add(
            User(
                id="admin-1",
                name="Admin User",
                email="admin1@example.com",
                password="hashed",
                role=UserRole.ADMIN,
                institution_id="inst-1",
            )
        )
        await session.commit()

    async with session_local() as session:
        yield session

    await engine.dispose()
    if db_path.exists():
        db_path.unlink()


@pytest.mark.asyncio
async def test_ai_generation_persistence_and_update(db_session):
    fingerprint = build_admin_report_request_fingerprint(
        institution_id="inst-1",
        source_entity_type="institution",
        source_entity_id="inst-1",
        prompt_version="v1",
        model_name="gemini-3.1-flash-lite-preview",
        raw_prompt_input={"date_from": "2026-01-01", "date_to": "2026-01-31"},
    )
    created = await create_ai_generation(
        db_session,
        AIGenerationCreate(
            feature_type=AIFeatureType.ADMIN_REPORT,
            requester_user_id="admin-1",
            institution_id="inst-1",
            source_entity_type="institution",
            source_entity_id="inst-1",
            prompt_version="v1",
            model_name="gemini-3.1-flash-lite-preview",
            raw_prompt_input={"scope": "monthly"},
            request_fingerprint=fingerprint,
            cache_expires_at=compute_cache_expiry(ttl_seconds=300),
        ),
    )
    assert created.status == AIGenerationStatus.PENDING
    assert created.feature_type == AIFeatureType.ADMIN_REPORT
    assert created.raw_prompt_input == {"scope": "monthly"}

    updated = await update_ai_generation(
        db_session,
        created,
        AIGenerationUpdate(
            status=AIGenerationStatus.COMPLETED,
            raw_model_output='{"summary":"Monthly report"}',
            parsed_output_json={"summary": "Monthly report"},
            token_usage=AITokenUsage(input_tokens=10, output_tokens=20, total_tokens=30),
            error_details={},
        ),
    )
    assert updated.status == AIGenerationStatus.COMPLETED
    assert updated.parsed_output_json == {"summary": "Monthly report"}
    assert updated.total_tokens == 30


@pytest.mark.asyncio
async def test_ai_generation_cache_and_dedupe_helpers(db_session):
    fingerprint = build_admin_report_request_fingerprint(
        institution_id="inst-1",
        source_entity_type="institution",
        source_entity_id="inst-1",
        prompt_version="v1",
        model_name="gemini-3.1-flash-lite-preview",
        raw_prompt_input={"period": "2026-Q1"},
    )

    pending = await create_ai_generation(
        db_session,
        AIGenerationCreate(
            feature_type=AIFeatureType.ADMIN_REPORT,
            requester_user_id="admin-1",
            institution_id="inst-1",
            source_entity_type="institution",
            source_entity_id="inst-1",
            prompt_version="v1",
            model_name="gemini-3.1-flash-lite-preview",
            raw_prompt_input={"period": "2026-Q1"},
            request_fingerprint=fingerprint,
            cache_expires_at=compute_cache_expiry(ttl_seconds=300),
        ),
    )

    active = await find_active_generation_by_fingerprint(
        db_session,
        feature_type=AIFeatureType.ADMIN_REPORT,
        request_fingerprint=fingerprint,
    )
    assert active is not None
    assert active.id == pending.id

    await update_ai_generation(
        db_session,
        pending,
        AIGenerationUpdate(
            status=AIGenerationStatus.COMPLETED,
            cache_expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        ),
    )

    cached = await find_cached_completed_generation(
        db_session,
        feature_type=AIFeatureType.ADMIN_REPORT,
        request_fingerprint=fingerprint,
    )
    assert cached is not None
    assert cached.status == AIGenerationStatus.COMPLETED


def test_admin_report_structured_validation():
    valid_payload = {
        "summary": "Overall outcomes improved.",
        "key_insights": ["Pass rate increased by 6%."],
        "risk_flags": ["Drop in attendance for two workshops."],
        "recommendations": [
            {
                "title": "Strengthen mentoring",
                "action": "Add weekly mentoring",
                "rationale": "Low completion in beginner cohort",
                "priority": "high",
            }
        ],
        "trend_highlights": ["Average score rising steadily in the last 4 weeks."],
        "data_window": {"start_date": "2026-01-01", "end_date": "2026-01-31", "scope": "institution"},
        "caveats": ["Attendance data missing for one workshop."],
    }
    validated = validate_admin_report_output(valid_payload)
    assert validated.summary == "Overall outcomes improved."
    assert validated.recommendations[0].priority == "high"

    with pytest.raises(StructuredOutputValidationError):
        validate_admin_report_output({"summary": "Missing fields"})


def test_admin_report_fingerprint_is_deterministic():
    payload_a = {"date_from": "2026-01-01", "date_to": "2026-01-31", "group_by": "workshop"}
    payload_b = {"group_by": "workshop", "date_to": "2026-01-31", "date_from": "2026-01-01"}
    key_a = build_admin_report_request_fingerprint(
        institution_id="inst-1",
        source_entity_type="institution",
        source_entity_id="inst-1",
        prompt_version="v1",
        model_name="gemini-3.1-flash-lite-preview",
        raw_prompt_input=payload_a,
    )
    key_b = build_admin_report_request_fingerprint(
        institution_id="inst-1",
        source_entity_type="institution",
        source_entity_id="inst-1",
        prompt_version="v1",
        model_name="gemini-3.1-flash-lite-preview",
        raw_prompt_input=payload_b,
    )
    key_c = build_admin_report_request_fingerprint(
        institution_id="inst-1",
        source_entity_type="institution",
        source_entity_id="inst-1",
        prompt_version="v2",
        model_name="gemini-3.1-flash-lite-preview",
        raw_prompt_input=payload_b,
    )
    assert key_a == key_b
    assert key_a != key_c


def test_in_memory_rate_limiter_enforces_window():
    limiter = InMemorySlidingWindowRateLimiter()
    rule = RateLimitRule(max_requests=2, window_seconds=60)
    now = datetime(2026, 4, 8, 10, 0, 0, tzinfo=timezone.utc)

    first = limiter.consume(key="admin:report:admin-1", rule=rule, now=now)
    second = limiter.consume(key="admin:report:admin-1", rule=rule, now=now + timedelta(seconds=1))
    third = limiter.consume(key="admin:report:admin-1", rule=rule, now=now + timedelta(seconds=2))
    after_window = limiter.consume(key="admin:report:admin-1", rule=rule, now=now + timedelta(seconds=61))

    assert first.allowed is True
    assert second.allowed is True
    assert third.allowed is False
    assert third.retry_after_seconds > 0
    assert after_window.allowed is True


@pytest.mark.asyncio
async def test_database_rate_limiter_is_shared_across_sessions(db_session):
    session_local = async_sessionmaker(bind=db_session.bind, expire_on_commit=False)
    limiter_a = DatabaseFixedWindowRateLimiter(retention_seconds=3600)
    limiter_b = DatabaseFixedWindowRateLimiter(retention_seconds=3600)
    rule = RateLimitRule(max_requests=2, window_seconds=60)
    now = datetime(2026, 4, 8, 10, 5, 0, tzinfo=timezone.utc)

    async with session_local() as session:
        first = await consume_rate_limit_or_raise(
            limiter=limiter_a,
            db=session,
            key="ai_report:user:admin-1",
            rule=rule,
            now=now,
        )
        await session.commit()
    assert first.allowed is True
    assert first.remaining == 1

    async with session_local() as session:
        second = await consume_rate_limit_or_raise(
            limiter=limiter_b,
            db=session,
            key="ai_report:user:admin-1",
            rule=rule,
            now=now + timedelta(seconds=1),
        )
        await session.commit()
    assert second.allowed is True
    assert second.remaining == 0

    async with session_local() as session:
        with pytest.raises(RateLimitViolation):
            await consume_rate_limit_or_raise(
                limiter=limiter_a,
                db=session,
                key="ai_report:user:admin-1",
                rule=rule,
                now=now + timedelta(seconds=2),
            )
