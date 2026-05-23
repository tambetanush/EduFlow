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
from app.api.v1.ai_student_explanations import (
    get_gemini_client,
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
            usage=GeminiUsage(input_tokens=15, output_tokens=25, total_tokens=40),
            retries_used=0,
        )


@pytest.fixture()
def student_explanation_client():
    db_path = Path("unit_testing") / f"ut_student_explanations_{uuid4().hex}.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_async_engine(f"sqlite+aiosqlite:///./{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    state = {"user_id": "student-1"}
    fake_payload = {
        "why_it_was_wrong": "Your choice matched a related concept but not the core definition.",
        "correct_reasoning": "Focus on the process that converts light energy into chemical energy.",
        "common_mistake": "Confusing two biological processes with similar wording.",
        "hint_for_retry": "Compare each option against the exact definition in your notes.",
        "confidence": 0.83,
        "follow_up_questions": ["What is the main input of this process?"],
    }
    fake_gemini = FakeGeminiClient(fake_payload)
    limiter = InMemorySlidingWindowRateLimiter()

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session_local() as session:
            session.add_all(
                [
                    Institution(id="inst-1", name="Institution One", address="Address 1"),
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
                    Assessment(
                        id="assessment-1",
                        workshop_id="workshop-1",
                        title="Biology Basics",
                        total_marks=10,
                        pass_mark=6,
                    ),
                    Question(
                        id="question-1",
                        assessment_id="assessment-1",
                        text="Which process converts light into chemical energy?",
                        type=QuestionType.MCQ,
                        marks=2,
                        options=[
                            {"id": "opt-a", "text": "Photosynthesis process", "is_correct": True},
                            {"id": "opt-b", "text": "Cell division process", "is_correct": False},
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

    def override_get_gemini_client():
        return fake_gemini

    def override_get_rate_limiter():
        return limiter

    def override_get_rate_rule():
        return RateLimitRule(max_requests=5, window_seconds=600)

    asyncio.run(setup_db())
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_gemini_client] = override_get_gemini_client
    app.dependency_overrides[get_student_explanation_rate_limiter] = override_get_rate_limiter
    app.dependency_overrides[get_student_explanation_rate_limit_rule] = override_get_rate_rule

    original_lifespan_context = app.router.lifespan_context

    @asynccontextmanager
    async def _noop_lifespan(_: object):
        yield

    app.router.lifespan_context = _noop_lifespan

    with TestClient(app) as client:
        yield client, state, fake_gemini, session_local

    app.router.lifespan_context = original_lifespan_context
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
    if db_path.exists():
        db_path.unlink()


def test_student_explanation_authorization_and_ownership(student_explanation_client):
    client, state, *_ = student_explanation_client

    state["user_id"] = "educator-1"
    educator_forbidden = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1"},
    )
    assert educator_forbidden.status_code == 403

    state["user_id"] = "student-1"
    out_of_scope = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-2", "question_id": "question-1"},
    )
    assert out_of_scope.status_code == 403


def test_student_explanation_success_and_persistence(student_explanation_client):
    client, state, fake_gemini, session_local = student_explanation_client
    state["user_id"] = "student-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["explanation"]["why_it_was_wrong"]
    assert fake_gemini.calls == 1

    explanation_id = payload["explanation_id"]

    async def _assert_generation_row():
        async with session_local() as session:
            row = (await session.execute(select(AIGeneration).where(AIGeneration.id == explanation_id))).scalar_one()
            assert row.feature_type == AIFeatureType.STUDENT_EXPLANATION
            assert row.status == AIGenerationStatus.COMPLETED
            assert row.raw_model_output is not None
            assert isinstance(row.parsed_output_json, dict)

    asyncio.run(_assert_generation_row())


def test_student_explanation_rate_limit(student_explanation_client):
    client, state, fake_gemini, _ = student_explanation_client
    state["user_id"] = "student-1"
    app.dependency_overrides[get_student_explanation_rate_limit_rule] = (
        lambda: RateLimitRule(max_requests=1, window_seconds=3600)
    )

    first = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1", "force_regenerate": True},
    )
    assert first.status_code == 200
    assert fake_gemini.calls == 1

    second = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1", "force_regenerate": True},
    )
    assert second.status_code == 429


def test_student_explanation_blocks_answer_key_leak(student_explanation_client):
    client, state, fake_gemini, session_local = student_explanation_client
    state["user_id"] = "student-1"
    fake_gemini.payload = {
        "why_it_was_wrong": "You picked the wrong process.",
        "correct_reasoning": "The correct answer is Photosynthesis process.",
        "common_mistake": "Mixing up concepts.",
        "hint_for_retry": "Read definitions carefully.",
        "confidence": 0.6,
        "follow_up_questions": [],
    }

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1", "force_regenerate": True},
    )
    assert response.status_code == 502
    detail = response.json()["detail"]
    explanation_id = detail["explanation_id"]

    async def _assert_failed_row():
        async with session_local() as session:
            row = (await session.execute(select(AIGeneration).where(AIGeneration.id == explanation_id))).scalar_one()
            assert row.status == AIGenerationStatus.FAILED
            assert row.error_details["error_type"] == "StructuredOutputValidationError"

    asyncio.run(_assert_failed_row())
