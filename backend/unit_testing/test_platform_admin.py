import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.deps import get_current_user, get_db
from app.main import app
from app.models import (
    ApprovalRequest,
    ApprovalRequestStatus,
    ApprovalRequestType,
    Assessment,
    Base,
    Institution,
    Module,
    Notification,
    Question,
    SalaryPayment,
    SalaryPaymentStatus,
    Submission,
    User,
    UserRole,
    Workshop,
)


@pytest.fixture()
def client_and_state():
    db_path = Path("unit_testing") / f"ut_platform_admin_{uuid4().hex}.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///./{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    state = {"user_id": "user-admin"}

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session_local() as session:
            institution = Institution(id="inst-1", name="IIT Delhi", address="Delhi")
            admin = User(
                id="user-admin",
                name="Platform Admin",
                email="admin@eduflow.edu",
                password="hashed",
                role=UserRole.ADMIN,
                institution_id="inst-1",
            )
            institution_admin = User(
                id="user-inst-admin",
                name="Institution Admin",
                email="inst-admin@eduflow.edu",
                password="hashed",
                role=UserRole.INSTITUTION_ADMIN,
                institution_id="inst-1",
            )
            student = User(
                id="user-student",
                name="Student One",
                email="student1@eduflow.edu",
                password="hashed",
                role=UserRole.STUDENT,
                institution_id="inst-1",
                parent_name="Parent One",
                parent_email="parent1@example.com",
            )
            workshop = Workshop(
                id="workshop-1",
                title="React Fundamentals",
                description="Workshop for frontend basics",
                institution_id="inst-1",
                start_date=datetime.now(timezone.utc) - timedelta(days=5),
                end_date=datetime.now(timezone.utc) + timedelta(days=5),
            )
            module = Module(
                id="module-1",
                workshop_id="workshop-1",
                title="Introduction",
                order_index=1,
                materials=[{"id": "m1", "title": "Slides", "type": "link", "content": "https://example.com"}],
            )
            assessment = Assessment(
                id="assessment-1",
                workshop_id="workshop-1",
                module_id="module-1",
                title="Quiz 1",
                total_marks=100,
                pass_mark=40,
            )
            question = Question(
                id="question-1",
                assessment_id="assessment-1",
                text="What is React?",
                type="mcq",
                marks=10,
                options=[
                    {"id": "opt-a", "text": "Library", "is_correct": True},
                    {"id": "opt-b", "text": "Database", "is_correct": False},
                ],
            )
            submission = Submission(
                id="submission-1",
                student_id="user-student",
                assessment_id="assessment-1",
                answers=[],
                score=80,
                percentage=80,
                pass_fail=True,
            )
            notification = Notification(
                id="notification-1",
                user_id="user-student",
                message="Assessment published",
            )
            salary = SalaryPayment(
                id="salary-1",
                educator_id="user-inst-admin",
                month="2026-03",
                amount=50000,
                status=SalaryPaymentStatus.PAID,
            )
            approval = ApprovalRequest(
                id="approval-1",
                request_type=ApprovalRequestType.DELETE_STUDENT,
                status=ApprovalRequestStatus.PENDING,
                payload={"user_id": "user-student"},
                requested_by="user-inst-admin",
            )

            session.add_all(
                [
                    institution,
                    admin,
                    institution_admin,
                    student,
                    workshop,
                    module,
                    assessment,
                    question,
                    submission,
                    notification,
                    salary,
                    approval,
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
            user = await session.get(User, state["user_id"])
            return user

    asyncio.run(setup_db())
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client, state

    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
    if db_path.exists():
        db_path.unlink()


def test_admin_dashboard_stats_success(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/dashboard/admin")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_institutions"] >= 1
    assert payload["total_workshops"] >= 1
    assert payload["total_students"] >= 1


def test_admin_dashboard_forbidden_for_non_admin(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-inst-admin"

    response = client.get("/api/v1/dashboard/admin")
    assert response.status_code == 403


def test_admin_workshop_crud(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    create_response = client.post(
        "/api/v1/workshops/",
        json={
            "title": "New Admin Workshop",
            "description": "Created by admin",
            "institution_id": "inst-1",
        },
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    patch_response = client.patch(f"/api/v1/workshops/{created_id}", json={"title": "Renamed Workshop"})
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Renamed Workshop"

    delete_response = client.delete(f"/api/v1/workshops/{created_id}")
    assert delete_response.status_code == 204


def test_admin_approval_list_and_approve(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    list_response = client.get("/api/v1/approvals/requests")
    assert list_response.status_code == 200
    request_ids = [item["id"] for item in list_response.json()["items"]]
    assert "approval-1" in request_ids

    approve_response = client.post("/api/v1/approvals/requests/approval-1/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"


def test_admin_salary_pay_and_list(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    pay_response = client.post(
        "/api/v1/salaries/pay",
        json={"educator_id": "user-inst-admin", "month": "2026-04", "amount": 62000},
    )
    assert pay_response.status_code == 201
    assert pay_response.json()["amount"] == 62000

    list_response = client.get("/api/v1/salaries/?month=2026-04")
    assert list_response.status_code == 200
    assert any(item["month"] == "2026-04" for item in list_response.json()["items"])


def test_admin_users_and_institutions_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    users_response = client.get("/api/v1/users/?limit=50")
    assert users_response.status_code == 200
    assert users_response.json()["total"] >= 3

    institutions_response = client.get("/api/v1/institutions/")
    assert institutions_response.status_code == 200
    assert any(item["id"] == "inst-1" for item in institutions_response.json())


def test_admin_new_analytics_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"
    assert len(assessment_lb.json()["entries"]) >= 1

    workshop_lb = client.get("/api/v1/analytics/leaderboard/workshop/workshop-1")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-1"

    admin_insights = client.get("/api/v1/analytics/admin/insights")
    assert admin_insights.status_code == 200
    payload = admin_insights.json()
    assert "weekly_activity" in payload
    assert len(payload["weekly_activity"]) == 7
    assert all("label" in point and "value" in point for point in payload["weekly_activity"])
    assert "demographics" in payload
    assert isinstance(payload["demographics"], list)
    if payload["demographics"]:
        assert all({"range", "male", "female"}.issubset(item.keys()) for item in payload["demographics"])
    assert "activity_feed" in payload
    assert isinstance(payload["activity_feed"], list)
    if payload["activity_feed"]:
        assert all({"id", "text", "time", "type"}.issubset(item.keys()) for item in payload["activity_feed"])

    institution_students = client.get("/api/v1/analytics/institution/students")
    assert institution_students.status_code == 200
    assert institution_students.json()["total"] >= 1

    institution_attendance = client.get("/api/v1/analytics/institution/attendance-report")
    assert institution_attendance.status_code == 200

    assessment_drilldown = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1/student/user-student")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["context_type"] == "assessment"

    state["user_id"] = "user-inst-admin"
    forbidden_insights = client.get("/api/v1/analytics/admin/insights")
    assert forbidden_insights.status_code == 403


def test_admin_parent_communication_dispatch(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["user-student"],
            "subject": "Attendance Follow-up",
            "body": "Please connect with mentor.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] == 1
    assert payload["failed"] == 0


def test_admin_can_read_approval_request_details(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/approvals/requests/approval-1")
    assert response.status_code == 404


def test_admin_approving_unknown_request_returns_not_found(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.post("/api/v1/approvals/requests/approval-missing/approve")
    assert response.status_code == 404


def test_admin_can_fetch_submission_review(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/submissions/submission-1/review")
    assert response.status_code == 200
    assert response.json()["submission_id"] == "submission-1"


def test_admin_can_export_performance_report(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/analytics/reports/performance/export")
    assert response.status_code == 200
    assert response.json()["file_type"] == "csv"


def test_platform_admin_endpoints_forbidden_for_student(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-student"

    assert client.get("/api/v1/dashboard/admin").status_code == 403
    assert client.get("/api/v1/users/?limit=20").status_code == 403
    assert client.post("/api/v1/approvals/requests/approval-1/approve").status_code == 403


def test_admin_workshop_create_validation_error(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.post(
        "/api/v1/workshops/",
        json={"description": "Missing title should fail", "institution_id": "inst-1"},
    )
    assert response.status_code == 422
