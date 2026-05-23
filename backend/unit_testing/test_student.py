import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from app.api.deps import get_current_user, get_db
from app.core.security import hash_password
from app.main import app
from app.models import (Assessment, Base, Certificate, Enrollment, Institution,
                        Module, Notification, Question, Submission, User,
                        UserRole, Workshop)
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@pytest.fixture()
def client_and_state():
    db_path = Path("unit_testing") / f"ut_student_{uuid4().hex}.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///./{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    state = {"user_id": "student-1"}

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session_local() as session:
            institution = Institution(
                id="inst-1", name="IIT Delhi", address="Delhi")
            student = User(
                id="student-1",
                name="Student One",
                email="student1@eduflow.edu",
                password=hash_password("student123"),
                role=UserRole.STUDENT,
                institution_id="inst-1",
                parent_name="Parent One",
                parent_email="parent1@example.com",
            )
            student_two = User(
                id="student-2",
                name="Student Two",
                email="student2@eduflow.edu",
                password=hash_password("student123"),
                role=UserRole.STUDENT,
                institution_id="inst-1",
            )
            educator = User(
                id="educator-1",
                name="Educator One",
                email="educator@eduflow.edu",
                password=hash_password("educator123"),
                role=UserRole.EDUCATOR,
                institution_id="inst-1",
            )
            workshop = Workshop(
                id="workshop-1",
                title="Student Workshop",
                description="Workshop for students",
                institution_id="inst-1",
                start_date=datetime.now(timezone.utc) - timedelta(days=3),
                end_date=datetime.now(timezone.utc) + timedelta(days=7),
            )
            module = Module(
                id="module-1",
                workshop_id="workshop-1",
                title="Module One",
                order_index=1,
                materials=[{"id": "mat-1", "title": "Material",
                            "type": "text", "content": "Read me"}],
            )
            assessment = Assessment(
                id="assessment-1",
                workshop_id="workshop-1",
                module_id="module-1",
                title="Student Assessment",
                total_marks=20,
                pass_mark=10,
            )
            q1 = Question(
                id="question-1",
                assessment_id="assessment-1",
                text="What is React?",
                type="mcq",
                marks=10,
                options=[
                    {"id": "q1-a", "text": "Library", "is_correct": True},
                    {"id": "q1-b", "text": "OS", "is_correct": False},
                ],
            )
            q2 = Question(
                id="question-2",
                assessment_id="assessment-1",
                text="What is TypeScript?",
                type="mcq",
                marks=10,
                options=[
                    {"id": "q2-a", "text": "Typed JS", "is_correct": True},
                    {"id": "q2-b", "text": "Editor", "is_correct": False},
                ],
            )
            enrollment = Enrollment(
                id="enrollment-1",
                student_id="student-1",
                workshop_id="workshop-1",
                status="active",
            )
            certificate = Certificate(
                id="certificate-1",
                student_id="student-1",
                workshop_id="workshop-1",
                verification_code="VERIFY-123",
            )
            notification = Notification(
                id="notification-1",
                user_id="student-1",
                message="Welcome to workshop",
            )
            graded_submission = Submission(
                id="submission-graded",
                student_id="student-1",
                assessment_id="assessment-1",
                answers=[{"question_id": "question-1",
                          "selected_option_ids": ["q1-a"]}],
                score=10,
                percentage=50,
                pass_fail=True,
            )

            session.add_all(
                [
                    institution,
                    student,
                    student_two,
                    educator,
                    workshop,
                    module,
                    assessment,
                    q1,
                    q2,
                    enrollment,
                    certificate,
                    notification,
                    graded_submission,
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


def test_student_auth_register_and_login(client_and_state):
    client, _ = client_and_state

    register_response = client.post(
        "/api/v1/auth/register",
        json={"name": "New Student", "email": "newstudent@eduflow.edu",
              "password": "secret123", "role": "student"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "newstudent@eduflow.edu", "password": "secret123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "refresh_token" in login_response.json()


def test_student_dashboard_and_analytics(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    dashboard = client.get("/api/v1/dashboard/student/student-1")
    assert dashboard.status_code == 200
    assert "enrolled_workshops" in dashboard.json()

    analytics = client.get("/api/v1/analytics/student/student-1")
    assert analytics.status_code == 200
    payload = analytics.json()
    assert payload["student_id"] == "student-1"
    assert "assessment" in payload
    assert "avg_percentage" in payload["assessment"]
    assert "score_trend" in payload["assessment"]
    assert isinstance(payload["assessment"]["score_trend"], list)
    if payload["assessment"]["score_trend"]:
        first_point = payload["assessment"]["score_trend"][0]
        assert "percentage" in first_point
        assert "submitted_at" in first_point


def test_student_workshops_and_enrollments(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    workshops = client.get("/api/v1/workshops/")
    assert workshops.status_code == 200
    assert workshops.json()["total"] >= 1

    enrollments = client.get("/api/v1/enrollments/student/student-1")
    assert enrollments.status_code == 200
    assert enrollments.json()["total"] >= 1

    forbidden_enroll = client.post(
        "/api/v1/enrollments/", json={"student_id": "student-2", "workshop_id": "workshop-1"})
    assert forbidden_enroll.status_code == 403


def test_student_attempt_start_save_submit_flow(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    start_response = client.post("/api/v1/tests/assessment-1/start")
    assert start_response.status_code == 201
    start_payload = start_response.json()
    submission_id = start_payload["submission_id"]
    assert len(start_payload["questions"]) >= 2

    save_answers = client.post(
        f"/api/v1/submissions/{submission_id}/answers",
        json={
            "answers": [
                {"question_id": "question-1", "selected_option_ids": ["q1-a"]},
                {"question_id": "question-2", "selected_option_ids": ["q2-a"]},
            ]
        },
    )
    assert save_answers.status_code == 200

    submit = client.post(
        f"/api/v1/tests/assessment-1/submit?submission_id={submission_id}")
    assert submit.status_code == 200
    assert submit.json()["score"] == 100.0
    assert submit.json()["correct_count"] == 2
    assert submit.json()["total"] == 2
    assert len(submit.json()["per_question"]) == 2
    assert submit.json()["pass_fail"] is True

    re_submit = client.post(
        f"/api/v1/tests/assessment-1/submit?submission_id={submission_id}")
    assert re_submit.status_code == 409


def test_student_certificates_notifications_and_profile(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    certificates = client.get("/api/v1/certificates/student/student-1")
    assert certificates.status_code == 200
    assert certificates.json()["total"] >= 1

    verify = client.get("/api/v1/certificates/verify/VERIFY-123")
    assert verify.status_code == 200

    notifications = client.get("/api/v1/notifications/student-1")
    assert notifications.status_code == 200
    assert notifications.json()["total"] >= 1

    first_notification_id = notifications.json()["items"][0]["id"]
    mark_read = client.patch(
        f"/api/v1/notifications/{first_notification_id}/read")
    assert mark_read.status_code == 200
    assert mark_read.json()["status"] == "read"

    delete_notification = client.delete(
        f"/api/v1/notifications/{first_notification_id}")
    assert delete_notification.status_code == 204

    me = client.get("/api/v1/users/me")
    assert me.status_code == 200
    assert me.json()["id"] == "student-1"

    profile_update = client.patch(
        "/api/v1/users/student-1",
        json={"bio": "I love frontend engineering.",
              "department": "Computer Science"},
    )
    assert profile_update.status_code == 200
    assert profile_update.json()["bio"] == "I love frontend engineering."
    assert profile_update.json()["department"] == "Computer Science"

    profile_upload = client.post(
        "/api/v1/users/student-1/profile-photo",
        files={"file": ("avatar.png", b"avatar-bytes", "image/png")},
    )
    assert profile_upload.status_code == 200
    assert profile_upload.json()["profile_photo"].startswith("media/avatars/")

    certificate_download = client.get(
        "/api/v1/certificates/certificate-1/download")
    assert certificate_download.status_code == 200
    assert certificate_download.headers["content-type"].startswith("application/pdf")
    assert certificate_download.content.startswith(b"%PDF-")


def test_student_forbidden_from_other_student_data(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    other_profile = client.get("/api/v1/users/student-2")
    assert other_profile.status_code == 403

    other_dashboard = client.get("/api/v1/dashboard/student/student-2")
    assert other_dashboard.status_code == 403

    other_analytics = client.get("/api/v1/analytics/student/student-2")
    assert other_analytics.status_code == 403

    other_upload = client.post(
        "/api/v1/users/student-2/profile-photo",
        files={"file": ("avatar.png", b"avatar-bytes", "image/png")},
    )
    assert other_upload.status_code == 403


def test_student_leaderboard_access_and_staff_only_guards(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    assessment_lb = client.get(
        "/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"

    workshop_lb = client.get(
        "/api/v1/analytics/leaderboard/workshop/workshop-1")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-1"

    assessment_drilldown = client.get(
        "/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["student_id"] == "student-1"

    workshop_drilldown = client.get(
        "/api/v1/analytics/leaderboard/workshop/workshop-1/student/student-1")
    assert workshop_drilldown.status_code == 200
    assert workshop_drilldown.json()["context_type"] == "workshop"

    review_forbidden = client.get(
        "/api/v1/submissions/submission-graded/review")
    assert review_forbidden.status_code == 403

    grade_forbidden = client.post(
        "/api/v1/submissions/submission-graded/grade")
    assert grade_forbidden.status_code == 403

    communication_forbidden = client.post(
        "/api/v1/communication/parent-email",
        json={"student_ids": ["student-1"], "subject": "Hi", "body": "Test"},
    )
    assert communication_forbidden.status_code == 403

    parent_contacts_forbidden = client.get(
        "/api/v1/communication/parent-contacts?student_ids=student-1")
    assert parent_contacts_forbidden.status_code == 403

    institution_bulk_forbidden = client.post(
        "/api/v1/analytics/institution/students/bulk-action",
        json={"student_ids": ["student-1"], "action": "set_inactive"},
    )
    assert institution_bulk_forbidden.status_code == 403

    attendance_export_forbidden = client.get(
        "/api/v1/analytics/institution/attendance-report/export")
    assert attendance_export_forbidden.status_code == 403

    performance_export_forbidden = client.get(
        "/api/v1/analytics/reports/performance/export")
    assert performance_export_forbidden.status_code == 403


def test_student_cannot_access_admin_or_institution_dashboards(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    assert client.get("/api/v1/dashboard/admin").status_code == 403
    assert client.get("/api/v1/analytics/admin/insights").status_code == 403
    assert client.get("/api/v1/analytics/institution/dashboard").status_code == 403


def test_student_cannot_view_educator_dashboard(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 403


def test_student_invalid_certificate_verification_code(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.get("/api/v1/certificates/verify/INVALID-CODE")
    assert response.status_code == 404


def test_student_cannot_delete_workshop(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.delete("/api/v1/workshops/workshop-1")
    assert response.status_code == 403


def test_student_cannot_grade_submission(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.post("/api/v1/submissions/submission-graded/grade")
    assert response.status_code == 403


def test_student_assessment_submit_unknown_submission(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.post("/api/v1/tests/assessment-1/submit?submission_id=does-not-exist")
    assert response.status_code == 404
