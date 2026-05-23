import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.sql import func

# --------------------------------------------------
# BASE
# --------------------------------------------------


class Base(DeclarativeBase):
    pass


def generate_uuid():
    return str(uuid.uuid4())


# --------------------------------------------------
# ENUMS
# --------------------------------------------------

class UserRole(str, Enum):
    ADMIN = "admin"
    INSTITUTION_ADMIN = "institution_admin"
    EDUCATOR = "educator"
    STUDENT = "student"
    TECHNICAL_SUPPORT = "technical_support"


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class QuestionType(str, Enum):
    MCQ = "mcq"
    MSQ = "msq"


class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    GENERAL = "general"
    TEST = "test"
    FEES = "fees"
    ATTENDANCE = "attendance"
    CERTIFICATE = "certificate"


class AIFeatureType(str, Enum):
    ADMIN_REPORT = "admin_report"
    STUDENT_EXPLANATION = "student_explanation"


class AIGenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ScheduledReportFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class ScheduledReportStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"


class ScheduledReportRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# --------------------------------------------------
# INSTITUTION
# --------------------------------------------------

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    address = Column(Text)
    is_active = Column(Boolean, default=True)

    admin_id = Column(String, ForeignKey("users.id"))

    users = relationship("User", back_populates="institution",
                         foreign_keys="User.institution_id")
    admin = relationship("User", foreign_keys=[admin_id])
    workshops = relationship("Workshop", back_populates="institution")


# --------------------------------------------------
# USERS
# --------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)

    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    role = Column(SqlEnum(UserRole))
    institution_id = Column(String, ForeignKey("institutions.id"))

    phone = Column(String)
    profile_photo = Column(String)
    bio = Column(Text)
    department = Column(String)
    parent_name = Column(String)
    parent_email = Column(String)
    institution_admin_name = Column(String)
    institution_admin_address = Column(Text)
    institution_admin_code = Column(String)
    theme = Column(String, default="light")
    
    # Educator salary
    salary_amount = Column(Integer, default=0)
    salary_type = Column(String, default="monthly")  # monthly, per_session, per_hour

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    institution = relationship(
        "Institution", back_populates="users", foreign_keys=[institution_id])
    enrollments = relationship("Enrollment", back_populates="student")


# --------------------------------------------------
# WORKSHOP + MODULE
# --------------------------------------------------

class Workshop(Base):
    __tablename__ = "workshops"

    id = Column(String, primary_key=True, default=generate_uuid)

    title = Column(String)
    description = Column(Text)

    start_date = Column(DateTime)
    end_date = Column(DateTime)

    institution_id = Column(String, ForeignKey("institutions.id"))

    institution = relationship("Institution", back_populates="workshops")
    modules = relationship("Module", back_populates="workshop")
    assessments = relationship("Assessment", back_populates="workshop")


class Module(Base):
    __tablename__ = "modules"

    id = Column(String, primary_key=True, default=generate_uuid)

    workshop_id = Column(String, ForeignKey("workshops.id"))

    title = Column(String)
    order_index = Column(Integer)

    # Embedded materials
    materials = Column(JSON, default=list)
    """
    [
      {
        "id": "...",
        "title": "...",
        "type": "video/text/link",
        "content": "...",
        "created_at": "..."
      }
    ]
    """

    workshop = relationship("Workshop", back_populates="modules")
    assessments = relationship("Assessment", back_populates="module")


# --------------------------------------------------
# ENROLLMENT
# --------------------------------------------------

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))
    workshop_id = Column(String, ForeignKey("workshops.id"))

    status = Column(SqlEnum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="enrollments")


# --------------------------------------------------
# SESSION + ATTENDANCE
# --------------------------------------------------

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)

    workshop_id = Column(String, ForeignKey("workshops.id"))

    title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String, primary_key=True, default=generate_uuid)

    session_id = Column(String, ForeignKey("sessions.id"))
    student_id = Column(String, ForeignKey("users.id"))

    status = Column(String)


# --------------------------------------------------
# ASSESSMENTS
# --------------------------------------------------

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String, primary_key=True, default=generate_uuid)

    workshop_id = Column(String, ForeignKey("workshops.id"))
    module_id = Column(String, ForeignKey("modules.id"))

    title = Column(String)
    total_marks = Column(Integer, default=0)
    pass_mark = Column(Integer, default=0)  # minimum score to pass

    workshop = relationship("Workshop", back_populates="assessments")
    module = relationship("Module", back_populates="assessments")
    questions = relationship("Question", back_populates="assessment")


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=generate_uuid)

    assessment_id = Column(String, ForeignKey("assessments.id"))

    text = Column(Text)
    type = Column(SqlEnum(QuestionType))
    marks = Column(Integer)

    # Embedded options
    options = Column(JSON, default=list)
    """
    [
      {
        "id": "...",
        "text": "...",
        "is_correct": true
      }
    ]
    """

    assessment = relationship("Assessment", back_populates="questions")


# --------------------------------------------------
# SUBMISSION
# --------------------------------------------------

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))
    assessment_id = Column(String, ForeignKey("assessments.id"))

    score = Column(Integer)
    percentage = Column(Integer)
    # True=pass, False=fail, None=ungraded
    pass_fail = Column(Boolean, nullable=True)

    # Embedded answers
    answers = Column(JSON, default=list)
    """
    [
      {
        "question_id": "...",
        "selected_option_id": "..."
      }
    ]
    """

    submitted_at = Column(DateTime(timezone=True), server_default=func.now())


# --------------------------------------------------
# AI GENERATION
# --------------------------------------------------

class AIGeneration(Base):
    __tablename__ = "ai_generations"

    id = Column(String, primary_key=True, default=generate_uuid)

    feature_type = Column(SqlEnum(AIFeatureType), nullable=False, index=True)
    requester_user_id = Column(String, ForeignKey(
        "users.id"), nullable=False, index=True)
    institution_id = Column(String, ForeignKey(
        "institutions.id"), nullable=True, index=True)

    source_entity_type = Column(String, nullable=False)
    source_entity_id = Column(String, nullable=False)
    request_fingerprint = Column(String(64), nullable=False, index=True)

    prompt_version = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    idempotency_key = Column(String, nullable=True, index=True)

    raw_prompt_input = Column(JSON, default=dict, nullable=False)
    raw_model_output = Column(Text, nullable=True)
    parsed_output_json = Column(JSON, nullable=True)

    status = Column(SqlEnum(AIGenerationStatus),
                    default=AIGenerationStatus.PENDING, nullable=False, index=True)
    error_details = Column(JSON, default=dict, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)

    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)

    cache_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)


class AIRateLimitCounter(Base):
    __tablename__ = "ai_rate_limit_counters"
    __table_args__ = (
        UniqueConstraint("key", "window_start",
                         name="uq_ai_rate_limit_counter_key_window"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(255), nullable=False, index=True)
    window_start = Column(DateTime(timezone=True), nullable=False, index=True)
    request_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)


# --------------------------------------------------
# SCHEDULED AI REPORTS
# --------------------------------------------------


class ScheduledAIReport(Base):
    __tablename__ = "scheduled_ai_reports"

    id = Column(String, primary_key=True, default=generate_uuid)

    created_by_user_id = Column(String, ForeignKey(
        "users.id"), nullable=False, index=True)
    institution_id = Column(String, ForeignKey(
        "institutions.id"), nullable=True, index=True)

    report_type = Column(String, nullable=False, default="admin_report")
    frequency = Column(SqlEnum(ScheduledReportFrequency),
                       nullable=False, default=ScheduledReportFrequency.DAILY)
    status = Column(SqlEnum(ScheduledReportStatus), nullable=False,
                    default=ScheduledReportStatus.ACTIVE, index=True)

    # Rolling window settings (e.g., last 7 days)
    window_days = Column(Integer, nullable=False, default=7)
    focus_areas = Column(JSON, default=list, nullable=False)

    # Recipient identifiers: user_ids and/or emails (resolved at send time)
    recipients = Column(JSON, default=list, nullable=False)

    timezone = Column(String, nullable=False, default="UTC")
    time_of_day = Column(String, nullable=False,
                         default="09:00")  # HH:MM in timezone
    # for weekly: [0..6] (Mon=0)
    weekdays = Column(JSON, default=list, nullable=False)

    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)


class ScheduledAIReportRun(Base):
    __tablename__ = "scheduled_ai_report_runs"

    id = Column(String, primary_key=True, default=generate_uuid)

    schedule_id = Column(String, ForeignKey(
        "scheduled_ai_reports.id"), nullable=False, index=True)
    ai_generation_id = Column(String, ForeignKey(
        "ai_generations.id"), nullable=False, index=True)

    due_at = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(SqlEnum(ScheduledReportRunStatus), nullable=False,
                    default=ScheduledReportRunStatus.PENDING, index=True)
    error_details = Column(JSON, default=dict, nullable=True)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)

# --------------------------------------------------
# CERTIFICATE
# --------------------------------------------------


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))
    workshop_id = Column(String, ForeignKey("workshops.id"))

    issue_date = Column(DateTime(timezone=True), server_default=func.now())
    verification_code = Column(String, unique=True)


# --------------------------------------------------
# FEES + PAYMENTS
# --------------------------------------------------

class FeePlan(Base):
    __tablename__ = "fee_plans"

    id = Column(String, primary_key=True, default=generate_uuid)

    name = Column(String)
    amount = Column(Integer)
    billing_cycle = Column(String)


class StudentFee(Base):
    __tablename__ = "student_fees"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))
    fee_plan_id = Column(String, ForeignKey("fee_plans.id"))

    balance = Column(Integer)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=generate_uuid)

    student_id = Column(String, ForeignKey("users.id"))

    amount = Column(Integer)
    method = Column(String)
    reference = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# --------------------------------------------------
# NOTIFICATIONS
# --------------------------------------------------

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)

    user_id = Column(String, ForeignKey("users.id"))

    title = Column(String, nullable=False, default="Notification")
    message = Column(Text, nullable=False)
    status = Column(SqlEnum(NotificationStatus),
                    default=NotificationStatus.UNREAD)
    notification_type = Column(
        SqlEnum(NotificationType), default=NotificationType.GENERAL
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(String, primary_key=True, default=generate_uuid)
    student_id = Column(String, ForeignKey("users.id"), nullable=False)
    workshop_id = Column(String, ForeignKey("workshops.id"), nullable=False)
    current_module_index = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# --------------------------------------------------
# APPROVAL REQUESTS (minimal workflow for admin panels)
# --------------------------------------------------


class ApprovalRequestType(str, Enum):
    DELETE_STUDENT = "delete_student"
    DELETE_EDUCATOR = "delete_educator"
    DELETE_WORKSHOP = "delete_workshop"


class ApprovalRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String, primary_key=True, default=generate_uuid)

    request_type = Column(SqlEnum(ApprovalRequestType), nullable=False)
    status = Column(SqlEnum(ApprovalRequestStatus),
                    default=ApprovalRequestStatus.PENDING)

    # Generic payload so we can add request types without schema churn.
    payload = Column(JSON, default=dict)

    requested_by = Column(String, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


# --------------------------------------------------
# EDUCATOR SALARY PAYMENTS (minimal bookkeeping for admin salary page)
# --------------------------------------------------

class SalaryPaymentStatus(str, Enum):
    PAID = "paid"
    UNPAID = "unpaid"


class SalaryPayment(Base):
    __tablename__ = "salary_payments"

    id = Column(String, primary_key=True, default=generate_uuid)

    educator_id = Column(String, ForeignKey("users.id"), nullable=False)
    month = Column(String, nullable=False)  # YYYY-MM
    amount = Column(Integer, default=0)
    status = Column(SqlEnum(SalaryPaymentStatus),
                    default=SalaryPaymentStatus.PAID)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# --------------------------------------------------
# AUDIT LOGS + SUPPORT EVENTS
# --------------------------------------------------


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)

    actor_user_id = Column(String, ForeignKey(
        "users.id"), nullable=True, index=True)
    actor_role = Column(String, nullable=True, index=True)

    action = Column(String(128), nullable=False, index=True)
    target_type = Column(String(64), nullable=True, index=True)
    target_id = Column(String(128), nullable=True, index=True)

    metadata_ = Column(JSON, default=dict, nullable=False)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)


class RateLimitEvent(Base):
    __tablename__ = "ai_rate_limit_events"

    id = Column(String, primary_key=True, default=generate_uuid)

    key = Column(String(255), nullable=False, index=True)
    allowed = Column(Boolean, nullable=False, default=False, index=True)
    remaining = Column(Integer, nullable=False, default=0)
    retry_after_seconds = Column(Integer, nullable=False, default=0)

    rule_max_requests = Column(Integer, nullable=False, default=0)
    rule_window_seconds = Column(Integer, nullable=False, default=0)

    actor_user_id = Column(String, ForeignKey(
        "users.id"), nullable=True, index=True)
    institution_id = Column(String, ForeignKey(
        "institutions.id"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
