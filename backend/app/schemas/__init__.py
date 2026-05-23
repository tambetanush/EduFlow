from app.schemas.base import Page
from app.schemas.user import (
    InstitutionCreate,
    InstitutionResponse,
    InstitutionUpdate,
    LoginRequest,
    Token,
    TokenPayload,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.schemas.workshop import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
    EnrollmentCreate,
    EnrollmentResponse,
    EnrollmentUpdate,
    MaterialItem,
    ModuleCreate,
    ModuleResponse,
    ModuleUpdate,
    SessionCreate,
    SessionResponse,
    SessionUpdate,
    WorkshopCreate,
    WorkshopResponse,
    WorkshopUpdate,
)
from app.schemas.assessment import (
    AnswerItem,
    AssessmentCreate,
    AssessmentResponse,
    AssessmentUpdate,
    OptionItem,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    SubmissionCreate,
    SubmissionResponse,
    SubmissionUpdate,
)
from app.schemas.misc import (
    CertificateCreate,
    CertificateResponse,
    FeePlanCreate,
    FeePlanResponse,
    FeePlanUpdate,
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
    PaymentCreate,
    PaymentResponse,
    StudentFeeCreate,
    StudentFeeResponse,
    StudentFeeUpdate,
)
from app.schemas.ai import (
    AIGenerationCreate,
    AIGenerationUpdate,
    AITokenUsage,
    AdminReportStructuredOutput,
    ADMIN_REPORT_RESPONSE_JSON_SCHEMA,
    StudentExplanationStructuredOutput,
    STUDENT_EXPLANATION_RESPONSE_JSON_SCHEMA,
    StudentExplanationCreateRequest,
    StudentExplanationCreateResponse,
)

__all__ = [
    # pagination
    "Page",
    # user
    "Token", "TokenPayload", "LoginRequest",
    "UserCreate", "UserUpdate", "UserResponse",
    "InstitutionCreate", "InstitutionUpdate", "InstitutionResponse",
    # workshop
    "MaterialItem",
    "WorkshopCreate", "WorkshopUpdate", "WorkshopResponse",
    "ModuleCreate", "ModuleUpdate", "ModuleResponse",
    "EnrollmentCreate", "EnrollmentUpdate", "EnrollmentResponse",
    "SessionCreate", "SessionUpdate", "SessionResponse",
    "AttendanceCreate", "AttendanceUpdate", "AttendanceResponse",
    # assessment
    "OptionItem", "AnswerItem",
    "AssessmentCreate", "AssessmentUpdate", "AssessmentResponse",
    "QuestionCreate", "QuestionUpdate", "QuestionResponse",
    "SubmissionCreate", "SubmissionUpdate", "SubmissionResponse",
    # misc
    "CertificateCreate", "CertificateResponse",
    "FeePlanCreate", "FeePlanUpdate", "FeePlanResponse",
    "StudentFeeCreate", "StudentFeeUpdate", "StudentFeeResponse",
    "PaymentCreate", "PaymentResponse",
    "NotificationCreate", "NotificationUpdate", "NotificationResponse",
    # ai
    "AIGenerationCreate", "AIGenerationUpdate", "AITokenUsage",
    "AdminReportStructuredOutput", "ADMIN_REPORT_RESPONSE_JSON_SCHEMA",
    "StudentExplanationStructuredOutput", "STUDENT_EXPLANATION_RESPONSE_JSON_SCHEMA",
    "StudentExplanationCreateRequest", "StudentExplanationCreateResponse",
]
