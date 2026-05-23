from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_current_user, get_db
from app.api.v1.ai_reports import get_ai_rate_limit_rules, get_ai_rate_limiter, get_gemini_client as get_report_gemini
from app.api.v1.ai_student_explanations import (
    get_gemini_client as get_explanation_gemini,
    get_student_explanation_rate_limit_rule,
    get_student_explanation_rate_limiter,
)
from app.main import app
from app.models import (
    AIFeatureType,
    AIGeneration,
    AIGenerationStatus,
    Assessment,
    Base,
    Institution,
    Question,
    QuestionType,
    Submission,
    User,
    UserRole,
)
from app.services.ai.gemini_client import GeminiGenerationResult, GeminiUsage
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
            usage=GeminiUsage(input_tokens=20, output_tokens=30, total_tokens=50),
            retries_used=0,
        )


@pytest.fixture()
def genai_client_and_state():
    db_path = Path("unit_testing") / f"ut_genai_{uuid4().hex}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_async_engine(f"sqlite+aiosqlite:///./{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    state = {"user_id": "admin-1"}

    report_payload = {
        "summary": "Strong progress with small attendance dips.",
        "key_insights": ["Assessment outcomes are improving."],
        "risk_flags": ["One workshop has lower completion rate."],
        "recommendations": [
            {
                "title": "Follow-up sessions",
                "action": "Run targeted weekly sessions.",
                "rationale": "Close identified learning gaps.",
                "priority": "high",
            }
        ],
        "trend_highlights": ["Scores up by 5%."],
        "data_window": {"start_date": "2026-01-01", "end_date": "2026-01-31", "scope": "institution"},
        "caveats": ["Data excludes archived content."],
    }
    explanation_payload = {
        "why_it_was_wrong": "The selected option does not match the definition.",
        "correct_reasoning": "Pick the option aligned with typed JavaScript semantics.",
        "common_mistake": "Confusing tooling with language features.",
        "hint_for_retry": "Re-read the language basics and compare options.",
        "confidence": 0.87,
        "follow_up_questions": ["What advantage does static typing provide?"],
    }
    report_gemini = FakeGeminiClient(report_payload)
    explanation_gemini = FakeGeminiClient(explanation_payload)
    report_limiter = InMemorySlidingWindowRateLimiter()
    explanation_limiter = InMemorySlidingWindowRateLimiter()

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
                        name="Institution Admin",
                        email="instadmin@example.com",
                        password="hashed",
                        role=UserRole.INSTITUTION_ADMIN,
                        institution_id="inst-1",
                    ),
                    User(
                        id="student-1",
                        name="Student One",
                        email="student1@example.com",
                        password="hashed",
                        role=UserRole.STUDENT,
                        institution_id="inst-1",
                    ),
                    User(
                        id="student-2",
                        name="Student Two",
                        email="student2@example.com",
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
                    Assessment(id="assessment-1", workshop_id="workshop-1", title="TypeScript Basics", total_marks=10, pass_mark=6),
                    Question(
                        id="question-1",
                        assessment_id="assessment-1",
                        text="What is TypeScript?",
                        type=QuestionType.MCQ,
                        marks=2,
                        options=[
                            {"id": "opt-a", "text": "A typed superset of JavaScript", "is_correct": True},
                            {"id": "opt-b", "text": "A relational database", "is_correct": False},
                        ],
                    ),
                    Submission(
                        id="submission-1",
                        student_id="student-1",
                        assessment_id="assessment-1",
                        score=0,
                        percentage=0,
                        pass_fail=False,
                        answers=[{"question_id": "question-1", "selected_option_ids": ["opt-b"]}],
                    ),
                    Submission(
                        id="submission-2",
                        student_id="student-2",
                        assessment_id="assessment-1",
                        score=0,
                        percentage=0,
                        pass_fail=False,
                        answers=[{"question_id": "question-1", "selected_option_ids": ["opt-b"]}],
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

    def override_report_gemini():
        return report_gemini

    def override_explanation_gemini():
        return explanation_gemini

    def override_report_limiter():
        return report_limiter

    def override_explanation_limiter():
        return explanation_limiter

    def override_report_rules():
        return (RateLimitRule(max_requests=3, window_seconds=600), RateLimitRule(max_requests=4, window_seconds=600))

    def override_explanation_rule():
        return RateLimitRule(max_requests=4, window_seconds=600)

    asyncio.run(setup_db())
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_report_gemini] = override_report_gemini
    app.dependency_overrides[get_explanation_gemini] = override_explanation_gemini
    app.dependency_overrides[get_ai_rate_limiter] = override_report_limiter
    app.dependency_overrides[get_ai_rate_limit_rules] = override_report_rules
    app.dependency_overrides[get_student_explanation_rate_limiter] = override_explanation_limiter
    app.dependency_overrides[get_student_explanation_rate_limit_rule] = override_explanation_rule

    original_lifespan_context = app.router.lifespan_context

    @asynccontextmanager
    async def _noop_lifespan(_: object):
        yield

    app.router.lifespan_context = _noop_lifespan

    with TestClient(app) as client:
        yield client, state, report_gemini, explanation_gemini, session_local

    app.router.lifespan_context = original_lifespan_context
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
    if db_path.exists():
        db_path.unlink()


def test_genai_admin_report_success(genai_client_and_state):
    client, state, report_gemini, _, _ = genai_client_and_state
    state["user_id"] = "admin-1"

    response = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert report_gemini.calls == 1


def test_genai_admin_report_forbidden_for_student(genai_client_and_state):
    client, state, *_ = genai_client_and_state
    state["user_id"] = "student-1"

    response = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1"})
    assert response.status_code == 403


def test_genai_admin_report_cross_institution_blocked_for_institution_admin(genai_client_and_state):
    client, state, *_ = genai_client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-2"})
    assert response.status_code == 403


def test_genai_admin_report_result_roundtrip(genai_client_and_state):
    client, state, _, _, _ = genai_client_and_state
    state["user_id"] = "admin-1"

    created = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1"})
    assert created.status_code == 200
    report_id = created.json()["report_id"]

    status = client.get(f"/api/v1/ai/reports/{report_id}/status")
    assert status.status_code == 200
    assert status.json()["status"] == "completed"

    result = client.get(f"/api/v1/ai/reports/{report_id}/result")
    assert result.status_code == 200
    assert "summary" in result.json()["result"]


def test_genai_student_explanation_success(genai_client_and_state):
    client, state, _, explanation_gemini, _ = genai_client_and_state
    state["user_id"] = "student-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert explanation_gemini.calls == 1


def test_genai_student_explanation_forbidden_for_educator(genai_client_and_state):
    client, state, *_ = genai_client_and_state
    state["user_id"] = "educator-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1"},
    )
    assert response.status_code == 403


def test_genai_student_explanation_requires_ownership(genai_client_and_state):
    client, state, *_ = genai_client_and_state
    state["user_id"] = "student-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-2", "question_id": "question-1"},
    )
    assert response.status_code == 403


def test_genai_persists_generation_metadata(genai_client_and_state):
    client, state, _, _, session_local = genai_client_and_state
    state["user_id"] = "student-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1"},
    )
    assert response.status_code == 200
    explanation_id = response.json()["explanation_id"]

    async def _check():
        async with session_local() as session:
            row = (await session.execute(select(AIGeneration).where(AIGeneration.id == explanation_id))).scalar_one()
            assert row.feature_type == AIFeatureType.STUDENT_EXPLANATION
            assert row.status == AIGenerationStatus.COMPLETED
            assert row.total_tokens == 50

    asyncio.run(_check())
