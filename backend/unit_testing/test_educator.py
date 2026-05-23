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
    Assessment,
    Base,
    Certificate,
    Enrollment,
    Institution,
    Module,
    Notification,
    Question,
    Submission,
    User,
    UserRole,
    Workshop,
)


@pytest.fixture()
def client_and_state():
    db_path = Path("unit_testing") / f"ut_educator_{uuid4().hex}.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///./{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    state = {"user_id": "educator-1"}

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session_local() as session:
            inst_one = Institution(id="inst-1", name="IIT Delhi", address="Delhi")
            inst_two = Institution(id="inst-2", name="IIT Kanpur", address="Kanpur")
            admin = User(
                id="admin-1",
                name="Platform Admin",
                email="admin@eduflow.edu",
                password="hashed",
                role=UserRole.ADMIN,
                institution_id="inst-1",
            )
            institution_admin = User(
                id="inst-admin-1",
                name="Institution Admin",
                email="inst-admin@eduflow.edu",
                password="hashed",
                role=UserRole.INSTITUTION_ADMIN,
                institution_id="inst-1",
            )
            educator = User(
                id="educator-1",
                name="Educator One",
                email="educator@eduflow.edu",
                password="hashed",
                role=UserRole.EDUCATOR,
                institution_id="inst-1",
            )
            student = User(
                id="student-1",
                name="Student One",
                email="student1@eduflow.edu",
                password="hashed",
                role=UserRole.STUDENT,
                institution_id="inst-1",
                parent_name="Parent One",
                parent_email="parent1@example.com",
            )
            own_workshop = Workshop(
                id="workshop-own",
                title="Educator Workshop",
                description="Owned by educator institution",
                institution_id="inst-1",
                start_date=datetime.now(timezone.utc) - timedelta(days=20),
                end_date=datetime.now(timezone.utc) + timedelta(days=10),
            )
            other_workshop = Workshop(
                id="workshop-other",
                title="External Workshop",
                description="Different institution",
                institution_id="inst-2",
                start_date=datetime.now(timezone.utc) - timedelta(days=20),
                end_date=datetime.now(timezone.utc) + timedelta(days=10),
            )
            module = Module(
                id="module-1",
                workshop_id="workshop-own",
                title="Module One",
                order_index=1,
                materials=[{"id": "mat-1", "title": "Slide deck", "type": "link", "content": "https://example.com"}],
            )
            assessment = Assessment(
                id="assessment-1",
                workshop_id="workshop-own",
                module_id="module-1",
                title="Assessment One",
                total_marks=100,
                pass_mark=40,
            )
            question = Question(
                id="question-1",
                assessment_id="assessment-1",
                text="What is TypeScript?",
                type="mcq",
                marks=10,
                options=[
                    {"id": "opt-a", "text": "Typed JS", "is_correct": True},
                    {"id": "opt-b", "text": "Database", "is_correct": False},
                ],
            )
            enrollment = Enrollment(
                id="enrollment-1",
                student_id="student-1",
                workshop_id="workshop-own",
                status="active",
            )
            submission = Submission(
                id="submission-1",
                student_id="student-1",
                assessment_id="assessment-1",
                score=None,
                percentage=None,
                pass_fail=None,
                answers=[],
            )
            graded_submission = Submission(
                id="submission-graded",
                student_id="student-1",
                assessment_id="assessment-1",
                score=10,
                percentage=100,
                pass_fail=True,
                answers=[{"question_id": "question-1", "selected_option_ids": ["opt-a"]}],
            )
            notification = Notification(
                id="notification-1",
                user_id="educator-1",
                message="New submission pending",
            )
            certificate = Certificate(
                id="certificate-1",
                student_id="student-1",
                workshop_id="workshop-own",
                verification_code="VERIFY-EDU-1",
            )
            module_other = Module(
                id="module-other",
                workshop_id="workshop-other",
                title="Other Institution Module",
                order_index=1,
                materials=[],
            )
            assessment_other = Assessment(
                id="assessment-other",
                workshop_id="workshop-other",
                module_id="module-other",
                title="Other Institution Assessment",
                total_marks=100,
                pass_mark=40,
            )
            question_other = Question(
                id="question-other",
                assessment_id="assessment-other",
                text="Cross-tenant probe question",
                type="mcq",
                marks=10,
                options=[{"id": "opt-o", "text": "Answer", "is_correct": True}],
            )
            submission_other_graded = Submission(
                id="submission-other-graded",
                student_id="student-1",
                assessment_id="assessment-other",
                score=10,
                percentage=100,
                pass_fail=True,
                answers=[{"question_id": "question-other", "selected_option_ids": ["opt-o"]}],
            )

            session.add_all(
                [
                    inst_one,
                    inst_two,
                    admin,
                    institution_admin,
                    educator,
                    student,
                    own_workshop,
                    other_workshop,
                    module,
                    module_other,
                    assessment,
                    assessment_other,
                    question,
                    question_other,
                    enrollment,
                    submission,
                    graded_submission,
                    submission_other_graded,
                    notification,
                    certificate,
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


def test_educator_dashboard_stats(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assigned_workshops"] >= 1
    assert payload["active_assessments"] >= 1


def test_educator_workshop_list_is_scoped(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/workshops/")
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert "workshop-own" in ids
    assert "workshop-other" not in ids


def test_educator_can_view_assessments_and_submissions(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    assessments_response = client.get("/api/v1/assessments/workshop/workshop-own")
    assert assessments_response.status_code == 200
    assert assessments_response.json()["total"] >= 1

    submissions_response = client.get("/api/v1/submissions/assessment/assessment-1")
    assert submissions_response.status_code == 200
    assert submissions_response.json()["total"] >= 1


def test_educator_cannot_read_assessments_or_submissions_other_institution(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    assert client.get("/api/v1/assessments/workshop/workshop-other").status_code == 403
    assert client.get("/api/v1/assessments/module/module-other").status_code == 403
    assert client.get("/api/v1/assessments/assessment-other").status_code == 403
    assert client.get("/api/v1/submissions/assessment/assessment-other").status_code == 403
    assert client.get("/api/v1/submissions/submission-other-graded/review").status_code == 403


def test_educator_material_upload_and_delete(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    upload_response = client.post(
        "/api/v1/modules/module-1/materials/upload",
        files={"file": ("lecture-notes.txt", b"hello materials", "text/plain")},
    )
    assert upload_response.status_code == 200
    materials = upload_response.json()["materials"]
    uploaded = next((item for item in materials if item["title"] == "lecture-notes.txt"), None)
    assert uploaded is not None

    download_response = client.get(f"/api/v1/materials/module-1/{uploaded['id']}/download")
    assert download_response.status_code == 200
    assert "/media/modules/module-1/" in download_response.json()["download_url"]

    delete_response = client.delete(f"/api/v1/materials/module-1/{uploaded['id']}")
    assert delete_response.status_code == 200
    remaining_ids = {item["id"] for item in delete_response.json()["materials"]}
    assert uploaded["id"] not in remaining_ids


def test_educator_can_fetch_workshop_analytics(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/workshop/workshop-own")
    assert response.status_code == 200
    payload = response.json()
    assert payload["workshop_id"] == "workshop-own"
    assert "assessment" in payload
    assert "pass_rate_percentage" in payload["assessment"]


def test_educator_notifications_success(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/notifications/educator-1")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_educator_can_view_review_and_dispatch_parent_message(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    review = client.get("/api/v1/submissions/submission-graded/review")
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload["submission_id"] == "submission-graded"
    assert len(review_payload["questions"]) >= 1

    message = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["student-1"],
            "subject": "Submission Reviewed",
            "body": "Please check updated breakdown.",
        },
    )
    assert message.status_code == 200
    assert message.json()["accepted"] == 1

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200

    assessment_drilldown = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["student_id"] == "student-1"

    workshop_drilldown = client.get("/api/v1/analytics/leaderboard/workshop/workshop-own/student/student-1")
    assert workshop_drilldown.status_code == 200
    assert workshop_drilldown.json()["context_id"] == "workshop-own"


def test_educator_can_grade_pending_submission(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.post("/api/v1/submissions/submission-1/grade")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "submission-1"
    assert payload["pass_fail"] is False

    repeat = client.post("/api/v1/submissions/submission-1/grade")
    assert repeat.status_code == 409


def test_educator_workshop_educator_profile_contract(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    own_profile = client.get("/api/v1/workshops/workshop-own/educator-profile")
    assert own_profile.status_code == 200
    payload = own_profile.json()
    assert payload["workshop_id"] == "workshop-own"
    assert payload["email"] == "educator@eduflow.edu"

    cross_institution = client.get("/api/v1/workshops/workshop-other/educator-profile")
    assert cross_institution.status_code == 403


def test_educator_certificate_recommend_and_download(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    recommend = client.post(
        "/api/v1/certificates/recommend",
        json={"student_id": "student-1", "workshop_id": "workshop-own", "note": "Ready for certificate."},
    )
    assert recommend.status_code == 200
    assert recommend.json()["accepted"] >= 1

    download = client.get("/api/v1/certificates/certificate-1/download")
    assert download.status_code == 200
    assert download.headers["content-type"].startswith("application/pdf")
    assert download.content.startswith(b"%PDF-")


def test_educator_performance_export_available(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/reports/performance/export")
    assert response.status_code == 200
    payload = response.json()
    assert payload["file_type"] == "csv"
    assert "/media/exports/" in payload["download_url"]


def test_educator_forbidden_admin_and_delete_routes(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    admin_dashboard = client.get("/api/v1/dashboard/admin")
    assert admin_dashboard.status_code == 403

    delete_workshop = client.delete("/api/v1/workshops/workshop-own")
    assert delete_workshop.status_code == 403


def test_educator_forbidden_from_salary_routes(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    pay = client.post(
        "/api/v1/salaries/pay",
        json={"educator_id": "educator-1", "month": "2026-04", "amount": 55000},
    )
    assert pay.status_code == 403

    listing = client.get("/api/v1/salaries/?month=2026-04")
    assert listing.status_code == 403


def test_educator_cannot_approve_requests(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    list_response = client.get("/api/v1/approvals/requests")
    assert list_response.status_code == 403

    approve_response = client.post("/api/v1/approvals/requests/approval-1/approve")
    assert approve_response.status_code == 403


def test_educator_cannot_access_admin_insights(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/admin/insights")
    assert response.status_code == 403


def test_educator_rejects_non_owned_enrollment_queries(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    own_enrollments = client.get("/api/v1/enrollments/student/student-1")
    assert own_enrollments.status_code == 200


def test_educator_grading_unknown_submission_returns_not_found(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.post("/api/v1/submissions/submission-missing/grade")
    assert response.status_code == 404


def test_educator_notification_collection_forbidden_for_other_user(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/notifications/student-1")
    assert response.status_code == 200
    assert isinstance(response.json().get("items"), list)
