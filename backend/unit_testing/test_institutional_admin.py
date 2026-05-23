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
    Attendance,
    Base,
    Enrollment,
    Institution,
    Module,
    Session,
    Submission,
    User,
    UserRole,
    Workshop,
)


@pytest.fixture()
def client_and_state():
    db_path = Path("unit_testing") / f"ut_institution_admin_{uuid4().hex}.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///./{db_path.as_posix()}")
    session_local = async_sessionmaker(bind=engine, expire_on_commit=False)
    state = {"user_id": "inst-admin-1"}

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with session_local() as session:
            inst_one = Institution(id="inst-1", name="IIT Delhi", address="Delhi")
            inst_two = Institution(id="inst-2", name="IIT Bombay", address="Mumbai")
            admin = User(
                id="platform-admin",
                name="Platform Admin",
                email="admin@eduflow.edu",
                password="hashed",
                role=UserRole.ADMIN,
                institution_id="inst-1",
            )
            inst_admin = User(
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
            external_student = User(
                id="student-2",
                name="Student Two",
                email="student2@eduflow.edu",
                password="hashed",
                role=UserRole.STUDENT,
                institution_id="inst-2",
            )
            own_workshop = Workshop(
                id="workshop-own",
                title="Institution Workshop",
                description="Owned by institution 1",
                institution_id="inst-1",
                start_date=datetime.now(timezone.utc) - timedelta(days=10),
                end_date=datetime.now(timezone.utc) + timedelta(days=15),
            )
            other_workshop = Workshop(
                id="workshop-other",
                title="External Workshop",
                description="Owned by institution 2",
                institution_id="inst-2",
                start_date=datetime.now(timezone.utc) - timedelta(days=5),
                end_date=datetime.now(timezone.utc) + timedelta(days=5),
            )
            module = Module(
                id="module-1",
                workshop_id="workshop-own",
                title="Module One",
                order_index=1,
                materials=[],
            )
            assessment = Assessment(
                id="assessment-1",
                workshop_id="workshop-own",
                module_id="module-1",
                title="Assessment One",
                total_marks=100,
                pass_mark=40,
            )
            submission = Submission(
                id="submission-1",
                student_id="student-1",
                assessment_id="assessment-1",
                score=70,
                percentage=70,
                pass_fail=True,
                answers=[],
            )
            enrollment = Enrollment(
                id="enrollment-1",
                student_id="student-1",
                workshop_id="workshop-own",
                status="active",
            )
            session_one = Session(
                id="session-1",
                workshop_id="workshop-own",
                title="Session One",
                start_time=datetime.now(timezone.utc) - timedelta(days=1),
                end_time=datetime.now(timezone.utc) - timedelta(days=1) + timedelta(hours=1),
            )
            attendance_one = Attendance(
                id="attendance-1",
                session_id="session-1",
                student_id="student-1",
                status="present",
            )
            approval = ApprovalRequest(
                id="approval-existing",
                request_type=ApprovalRequestType.DELETE_STUDENT,
                status=ApprovalRequestStatus.PENDING,
                payload={"user_id": "student-1"},
                requested_by="inst-admin-1",
            )

            session.add_all(
                [
                    inst_one,
                    inst_two,
                    admin,
                    inst_admin,
                    educator,
                    student,
                    external_student,
                    own_workshop,
                    other_workshop,
                    module,
                    assessment,
                    submission,
                    enrollment,
                    session_one,
                    attendance_one,
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


def test_institution_admin_dashboard_stats(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assigned_workshops"] >= 1
    assert "pending_submissions" in payload


def test_institution_admin_workshop_scope_and_create(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    list_response = client.get("/api/v1/workshops/")
    assert list_response.status_code == 200
    returned_ids = {item["id"] for item in list_response.json()["items"]}
    assert "workshop-own" in returned_ids
    assert "workshop-other" not in returned_ids

    create_response = client.post(
        "/api/v1/workshops/",
        json={"title": "Created by Institution Admin", "description": "Scoped create"},
    )
    assert create_response.status_code == 201
    assert create_response.json()["institution_id"] == "inst-1"


def test_institution_admin_cannot_update_other_institution_workshop(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.patch("/api/v1/workshops/workshop-other", json={"title": "Illegal update"})
    assert response.status_code == 403


def test_institution_admin_users_list_is_scoped(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/users/?limit=200")
    assert response.status_code == 200
    users = response.json()["items"]
    assert all(item["institution_id"] == "inst-1" for item in users)


def test_institution_admin_can_fetch_student_enrollments(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/enrollments/student/student-1")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_institution_admin_can_create_approval_request(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post(
        "/api/v1/approvals/requests",
        json={"request_type": "delete_student", "payload": {"user_id": "student-1"}},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"


def test_institution_admin_dashboard_aggregate_and_leaderboards(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    aggregate = client.get("/api/v1/analytics/institution/dashboard")
    assert aggregate.status_code == 200
    payload = aggregate.json()
    assert "kpis" in payload
    assert "alerts" in payload
    assert "attendance_trend" in payload

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"

    workshop_lb = client.get("/api/v1/analytics/leaderboard/workshop/workshop-own")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-own"

    assessment_drilldown = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["student_id"] == "student-1"

    workshop_drilldown = client.get("/api/v1/analytics/leaderboard/workshop/workshop-own/student/student-1")
    assert workshop_drilldown.status_code == 200
    assert workshop_drilldown.json()["context_type"] == "workshop"


def test_institution_admin_student_roster_and_attendance_report(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    students = client.get("/api/v1/analytics/institution/students")
    assert students.status_code == 200
    payload = students.json()
    assert payload["total"] >= 1
    assert any(item["id"] == "student-1" for item in payload["items"])

    attendance = client.get("/api/v1/analytics/institution/attendance-report")
    assert attendance.status_code == 200
    attendance_payload = attendance.json()
    assert attendance_payload["total"] >= 1
    assert any(item["student"] == "Student One" for item in attendance_payload["rows"])


def test_institution_admin_parent_message_dispatch(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["student-1"],
            "subject": "Progress Update",
            "body": "Please review the latest grades.",
        },
    )
    assert response.status_code == 200
    assert response.json()["accepted"] == 1


def test_institution_admin_bulk_and_export_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    bulk_action = client.post(
        "/api/v1/analytics/institution/students/bulk-action",
        json={"student_ids": ["student-1"], "action": "set_inactive"},
    )
    assert bulk_action.status_code == 200
    payload = bulk_action.json()
    assert payload["requested_students"] == 1
    assert payload["updated_enrollments"] >= 1

    students = client.get("/api/v1/analytics/institution/students")
    assert students.status_code == 200
    student_row = next(item for item in students.json()["items"] if item["id"] == "student-1")
    assert student_row["status"] == "Inactive"

    students_export = client.get("/api/v1/analytics/institution/students/export?student_ids=student-1")
    assert students_export.status_code == 200
    assert "/media/exports/" in students_export.json()["download_url"]

    attendance_export = client.get("/api/v1/analytics/institution/attendance-report/export")
    assert attendance_export.status_code == 200
    assert attendance_export.json()["file_type"] == "csv"

    dashboard_export = client.get("/api/v1/analytics/institution/dashboard/export")
    assert dashboard_export.status_code == 200
    assert dashboard_export.json()["file_type"] == "csv"

def test_institution_admin_parent_contact_lookup(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/communication/parent-contacts?student_ids=student-1&student_ids=student-2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["student_id"] == "student-1"
    assert payload["items"][0]["parent_email"] == "parent1@example.com"


def test_institution_admin_profile_metadata_update_self_only(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    update_self = client.patch(
        "/api/v1/users/inst-admin-1",
        json={
            "bio": "Leads institutional operations.",
            "department": "Administration",
            "institution_admin_name": "IIT Delhi South Campus",
            "institution_admin_address": "Hauz Khas, New Delhi",
            "institution_admin_code": "IITD-SA",
        },
    )
    assert update_self.status_code == 200
    payload = update_self.json()
    assert payload["bio"] == "Leads institutional operations."
    assert payload["department"] == "Administration"
    assert payload["institution_admin_code"] == "IITD-SA"

    update_other = client.patch(
        "/api/v1/users/student-1",
        json={"bio": "Should fail"},
    )
    assert update_other.status_code == 403


def test_institution_admin_cannot_access_platform_admin_dashboard(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/dashboard/admin")
    assert response.status_code == 403


def test_institution_admin_cannot_approve_requests(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post("/api/v1/approvals/requests/approval-existing/approve")
    assert response.status_code == 403


def test_institution_admin_dashboard_export_available(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/analytics/institution/dashboard/export")
    assert response.status_code == 200
    assert "/media/exports/" in response.json()["download_url"]


def test_institution_admin_cannot_read_other_student_enrollments(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/enrollments/student/student-2")
    assert response.status_code == 200
    assert "items" in response.json()


def test_institution_admin_workshop_patch_own_workshop(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.patch("/api/v1/workshops/workshop-own", json={"title": "Institution Workshop Updated"})
    assert response.status_code == 200
    assert response.json()["title"] == "Institution Workshop Updated"


def test_institution_admin_cannot_process_salary(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post(
        "/api/v1/salaries/pay",
        json={"educator_id": "educator-1", "month": "2026-04", "amount": 60000},
    )
    assert response.status_code == 403
