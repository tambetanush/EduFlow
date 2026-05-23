from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_current_user, get_db
from app.api.v1.ai_reports import get_ai_rate_limit_rules, get_ai_rate_limiter, get_gemini_client
from app.main import app
from app.config import settings
from app.models import AIFeatureType, AIGeneration, AIGenerationStatus, Base, Institution, User, UserRole
from app.services.ai.gemini_client import GeminiGenerationResult, GeminiUsage
from app.services.ai.cache import build_admin_report_request_fingerprint
from app.services.ai.rate_limit import InMemorySlidingWindowRateLimiter, RateLimitRule


class FakeGeminiClient:
    def __init__(self, payload: dict):
        self.payload = payload
        self.calls = 0

    async def generate_structured(self, *, prompt: str, response_json_schema: dict, temperature: float = 0.2):
        self.calls += 1
        return GeminiGenerationResult(
            raw_output=json.dumps(self.payload),
            parsed_output=self.payload,
            usage=GeminiUsage(input_tokens=12, output_tokens=34, total_tokens=46),
            retries_used=0,
        )


@pytest.fixture()
def client_state_and_mocks():
    db_path = Path("unit_testing") / f"ut_admin_ai_reports_{uuid4().hex}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_async_engine(f"sqlite+aiosqlite:///./{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    state = {"user_id": "admin-1"}

    good_payload = {
        "summary": "Institution outcomes are stable with moderate improvements.",
        "key_insights": ["Pass rate improved by 4%.", "Submission volume increased by 8%."],
        "risk_flags": ["Attendance dip observed in week 3."],
        "recommendations": [
            {
                "title": "Targeted remediation",
                "action": "Run weekly remediation sessions.",
                "rationale": "Lower scores in two workshops.",
                "priority": "high",
            }
        ],
        "trend_highlights": ["Average score is trending upward."],
        "data_window": {"start_date": "2026-01-01", "end_date": "2026-01-31", "scope": "institution"},
        "caveats": ["Attendance data excludes one archived session."],
    }
    fake_gemini = FakeGeminiClient(good_payload)
    limiter = InMemorySlidingWindowRateLimiter()

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session_local() as session:
            session.add_all(
                [
                    Institution(id="inst-1", name="Institution One", address="Address 1"),
                    Institution(id="inst-2", name="Institution Two", address="Address 2"),
                    User(
                        id="admin-1",
                        name="Platform Admin",
                        email="admin@example.com",
                        password="hashed",
                        role=UserRole.ADMIN,
                        institution_id="inst-1",
                    ),
                    User(
                        id="inst-admin-1",
                        name="Institution Admin 1",
                        email="instadmin1@example.com",
                        password="hashed",
                        role=UserRole.INSTITUTION_ADMIN,
                        institution_id="inst-1",
                    ),
                    User(
                        id="student-1",
                        name="Student One",
                        email="student@example.com",
                        password="hashed",
                        role=UserRole.STUDENT,
                        institution_id="inst-1",
                    ),
                    User(
                        id="educator-1",
                        name="Educator One",
                        email="educator@example.com",
                        password="hashed",
                        role=UserRole.EDUCATOR,
                        institution_id="inst-1",
                    ),
                ]
            )
            await session.commit()

    async def override_get_db():
        async with session_local() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def override_get_current_user():
        async with session_local() as session:
            return await session.get(User, state["user_id"])

    def override_get_gemini_client():
        return fake_gemini

    def override_get_rate_limiter():
        return limiter

    def override_get_rate_rules():
        return (RateLimitRule(max_requests=2, window_seconds=600), RateLimitRule(max_requests=3, window_seconds=600))

    asyncio.run(setup_db())
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_gemini_client] = override_get_gemini_client
    app.dependency_overrides[get_ai_rate_limiter] = override_get_rate_limiter
    app.dependency_overrides[get_ai_rate_limit_rules] = override_get_rate_rules

    original_lifespan_context = app.router.lifespan_context

    @asynccontextmanager
    async def _noop_lifespan(_: object):
        yield

    app.router.lifespan_context = _noop_lifespan

    with TestClient(app) as client:
        yield client, state, fake_gemini, session_local, limiter

    app.router.lifespan_context = original_lifespan_context
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
    if db_path.exists():
        db_path.unlink()


def test_admin_ai_report_authorization(client_state_and_mocks):
    client, state, *_ = client_state_and_mocks

    state["user_id"] = "admin-1"
    seed_report = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1", "force_regenerate": True})
    assert seed_report.status_code == 200
    report_id = seed_report.json()["report_id"]

    state["user_id"] = "student-1"
    student_forbidden = client.post("/api/v1/ai/reports/", json={})
    assert student_forbidden.status_code == 403
    student_forbidden_status = client.get(f"/api/v1/ai/reports/{report_id}/status")
    assert student_forbidden_status.status_code == 403

    state["user_id"] = "educator-1"
    educator_forbidden_create = client.post("/api/v1/ai/reports/", json={})
    assert educator_forbidden_create.status_code == 403
    educator_forbidden_list = client.get("/api/v1/ai/reports/")
    assert educator_forbidden_list.status_code == 403
    educator_forbidden_result = client.get(f"/api/v1/ai/reports/{report_id}/result")
    assert educator_forbidden_result.status_code == 403

    state["user_id"] = "inst-admin-1"
    out_of_scope = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-2"})
    assert out_of_scope.status_code == 403


def test_admin_ai_report_success_persistence_and_endpoints(client_state_and_mocks):
    client, state, fake_gemini, session_local, _ = client_state_and_mocks
    state["user_id"] = "admin-1"

    create_resp = client.post(
        "/api/v1/ai/reports/",
        json={"institution_id": "inst-1", "date_from": "2026-01-01", "date_to": "2026-01-31"},
    )
    assert create_resp.status_code == 200
    create_payload = create_resp.json()
    assert create_payload["status"] == "completed"
    report_id = create_payload["report_id"]
    assert fake_gemini.calls == 1

    status_resp = client.get(f"/api/v1/ai/reports/{report_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "completed"

    result_resp = client.get(f"/api/v1/ai/reports/{report_id}/result")
    assert result_resp.status_code == 200
    result_payload = result_resp.json()
    assert "summary" in result_payload["result"]
    assert "recommendations" in result_payload["result"]

    list_resp = client.get("/api/v1/ai/reports/?limit=20")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    async def _assert_row():
        async with session_local() as session:
            row = (await session.execute(select(AIGeneration).where(AIGeneration.id == report_id))).scalar_one()
            assert row.feature_type == AIFeatureType.ADMIN_REPORT
            assert row.raw_model_output is not None
            assert isinstance(row.parsed_output_json, dict)
            assert row.total_tokens == 46

    asyncio.run(_assert_row())


def test_admin_ai_report_invalid_structured_output_marks_failed(client_state_and_mocks):
    client, state, fake_gemini, session_local, _ = client_state_and_mocks
    state["user_id"] = "admin-1"
    fake_gemini.payload = {"summary": "missing required fields"}

    create_resp = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1"})
    assert create_resp.status_code == 502
    detail = create_resp.json()["detail"]
    report_id = detail["report_id"]

    status_resp = client.get(f"/api/v1/ai/reports/{report_id}/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "failed"
    assert status_resp.json()["error_details"]["error_type"] in {"StructuredOutputValidationError", "ValidationError"}

    async def _assert_failed():
        async with session_local() as session:
            row = (await session.execute(select(AIGeneration).where(AIGeneration.id == report_id))).scalar_one()
            assert row.status == AIGenerationStatus.FAILED
            assert row.raw_model_output is None

    asyncio.run(_assert_failed())


def test_admin_ai_report_cached_response_reuse(client_state_and_mocks):
    client, state, fake_gemini, *_ = client_state_and_mocks
    state["user_id"] = "admin-1"
    payload = {"institution_id": "inst-1", "date_from": "2026-01-01", "date_to": "2026-01-31"}

    first = client.post("/api/v1/ai/reports/", json=payload)
    assert first.status_code == 200
    first_id = first.json()["report_id"]
    assert fake_gemini.calls == 1

    second = client.post("/api/v1/ai/reports/", json=payload)
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["report_id"] == first_id
    assert second_payload["from_cache"] is True
    assert second_payload["deduplicated"] is True
    assert fake_gemini.calls == 1


def test_admin_ai_report_rate_limiting(client_state_and_mocks):
    client, state, fake_gemini, _, _ = client_state_and_mocks
    state["user_id"] = "admin-1"

    app.dependency_overrides[get_ai_rate_limit_rules] = (
        lambda: (RateLimitRule(max_requests=1, window_seconds=3600), RateLimitRule(max_requests=1, window_seconds=3600))
    )

    first = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1", "force_regenerate": True})
    assert first.status_code == 200
    assert fake_gemini.calls == 1

    second = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1", "force_regenerate": True})
    assert second.status_code == 429
    assert second.json()["detail"] == "Rate limit exceeded for report generation."


def test_institution_admin_sees_only_own_institution_reports(client_state_and_mocks):
    client, state, fake_gemini, *_ = client_state_and_mocks

    state["user_id"] = "admin-1"
    inst2 = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-2", "force_regenerate": True})
    assert inst2.status_code == 200
    inst2_report_id = inst2.json()["report_id"]

    state["user_id"] = "inst-admin-1"
    inst1 = client.post("/api/v1/ai/reports/", json={"force_regenerate": True})
    assert inst1.status_code == 200
    inst1_report_id = inst1.json()["report_id"]

    history = client.get("/api/v1/ai/reports/?limit=20")
    assert history.status_code == 200
    report_ids = {item["report_id"] for item in history.json()["items"]}
    assert inst1_report_id in report_ids
    assert inst2_report_id not in report_ids
    assert all(item.get("institution_id") == "inst-1" for item in history.json()["items"])

    inst2_status = client.get(f"/api/v1/ai/reports/{inst2_report_id}/status")
    assert inst2_status.status_code == 403
    inst2_result = client.get(f"/api/v1/ai/reports/{inst2_report_id}/result")
    assert inst2_result.status_code == 403

    assert fake_gemini.calls >= 2


def test_platform_admin_can_see_global_and_institution_reports(client_state_and_mocks):
    client, state, *_ = client_state_and_mocks
    state["user_id"] = "admin-1"

    global_report = client.post("/api/v1/ai/reports/", json={"force_regenerate": True})
    assert global_report.status_code == 200
    global_id = global_report.json()["report_id"]

    inst_report = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-2", "force_regenerate": True})
    assert inst_report.status_code == 200
    inst_id = inst_report.json()["report_id"]

    all_history = client.get("/api/v1/ai/reports/?limit=20")
    assert all_history.status_code == 200
    ids = {item["report_id"] for item in all_history.json()["items"]}
    assert global_id in ids
    assert inst_id in ids

    filtered = client.get("/api/v1/ai/reports/?institution_id=inst-2&limit=20")
    assert filtered.status_code == 200
    assert filtered.json()["total"] >= 1
    assert all(item.get("institution_id") == "inst-2" for item in filtered.json()["items"])


def test_stale_processing_generation_is_failed_and_regenerated(client_state_and_mocks):
    client, state, fake_gemini, session_local, _ = client_state_and_mocks
    state["user_id"] = "admin-1"
    payload = {"institution_id": "inst-1"}
    fingerprint_payload = {
        "institution_id": "inst-1",
        "date_from": None,
        "date_to": None,
        "focus_areas": [],
        "force_regenerate": False,
        "source_entity_type": "institution",
        "source_entity_id": "inst-1",
    }
    fingerprint = build_admin_report_request_fingerprint(
        institution_id="inst-1",
        source_entity_type="institution",
        source_entity_id="inst-1",
        prompt_version=settings.AI_ADMIN_REPORT_PROMPT_VERSION,
        model_name=settings.GEMINI_MODEL_NAME,
        raw_prompt_input=fingerprint_payload,
    )
    stale_age = settings.AI_ADMIN_REPORT_STALE_AFTER_SECONDS + 5
    stale_time = datetime.now(timezone.utc) - timedelta(seconds=stale_age)

    async def _seed_stale_generation():
        async with session_local() as session:
            session.add(
                AIGeneration(
                    id="stale-report-1",
                    feature_type=AIFeatureType.ADMIN_REPORT,
                    requester_user_id="admin-1",
                    institution_id="inst-1",
                    source_entity_type="institution",
                    source_entity_id="inst-1",
                    request_fingerprint=fingerprint,
                    prompt_version=settings.AI_ADMIN_REPORT_PROMPT_VERSION,
                    model_name=settings.GEMINI_MODEL_NAME,
                    raw_prompt_input=fingerprint_payload,
                    status=AIGenerationStatus.PROCESSING,
                    created_at=stale_time,
                    updated_at=stale_time,
                )
            )
            await session.commit()

    asyncio.run(_seed_stale_generation())

    create_resp = client.post("/api/v1/ai/reports/", json=payload)
    assert create_resp.status_code == 200
    new_report_id = create_resp.json()["report_id"]
    assert new_report_id != "stale-report-1"
    assert fake_gemini.calls == 1

    async def _assert_stale_failed():
        async with session_local() as session:
            stale = await session.get(AIGeneration, "stale-report-1")
            assert stale is not None
            assert stale.status == AIGenerationStatus.FAILED
            assert stale.error_details["error_type"] == "StaleGenerationTimeout"

    asyncio.run(_assert_stale_failed())
