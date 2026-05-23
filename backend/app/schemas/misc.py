from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models import NotificationStatus, NotificationType


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------


class CertificateCreate(BaseModel):
    student_id: str
    workshop_id: str


class CertificateResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    student_id: Optional[str]
    workshop_id: Optional[str]
    issue_date: Optional[datetime]
    verification_code: Optional[str]
    qr_url: Optional[str] = None      # verification URL / QR payload
    pdf_path: Optional[str] = None    # relative path to the mock PDF

    # Extra convenience fields for the integrated frontend.
    student_name: Optional[str] = None
    workshop_title: Optional[str] = None


# ---------------------------------------------------------------------------
# FeePlan
# ---------------------------------------------------------------------------


class FeePlanCreate(BaseModel):
    name: str
    amount: int
    billing_cycle: str


class FeePlanUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[int] = None
    billing_cycle: Optional[str] = None


class FeePlanResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: Optional[str]
    amount: Optional[int]
    billing_cycle: Optional[str]


# ---------------------------------------------------------------------------
# StudentFee
# ---------------------------------------------------------------------------


class StudentFeeAssign(BaseModel):
    """Body for POST /fees/assign — assign a fee-plan to a student."""

    student_id: str
    fee_plan_id: str
    initial_balance: int = 0         # pre-paid / remaining balance


class StudentFeeCreate(BaseModel):
    student_id: str
    fee_plan_id: str
    balance: int = 0


class StudentFeeUpdate(BaseModel):
    balance: Optional[int] = None


class StudentFeeResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    student_id: Optional[str]
    fee_plan_id: Optional[str]
    balance: Optional[int]
    # Nested fee plan summary (populated in router, not from ORM directly)
    fee_plan: Optional[FeePlanResponse] = None


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------


class PaymentCreate(BaseModel):
    student_id: str
    amount: int
    method: str                     # e.g. "upi", "card", "bank_transfer", "cash"
    reference: Optional[str] = None
    # Optional: credit payment against a specific student_fee row
    student_fee_id: Optional[str] = None


class PaymentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    student_id: Optional[str]
    amount: Optional[int]
    method: Optional[str]
    reference: Optional[str]
    created_at: Optional[datetime]


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------


class NotificationCreate(BaseModel):
    user_id: str
    title: Optional[str] = None
    message: str
    notification_type: NotificationType = NotificationType.GENERAL


class NotificationBulkCreate(BaseModel):
    user_ids: list[str]
    title: Optional[str] = None
    message: str
    notification_type: NotificationType = NotificationType.GENERAL


class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None


class NotificationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    user_id: Optional[str]
    title: Optional[str] = None
    message: Optional[str]
    status: Optional[NotificationStatus]
    notification_type: Optional[NotificationType]
    created_at: Optional[datetime]


class StudentProgressCreate(BaseModel):
    workshop_id: str
    current_module_index: int = 0


class StudentProgressUpdate(BaseModel):
    workshop_id: str
    current_module_index: int


class StudentProgressResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    student_id: str
    workshop_id: str
    current_module_index: int
    updated_at: Optional[datetime]


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


class AdminDashboardStats(BaseModel):
    total_institutions: int
    total_workshops: int
    total_educators: int
    total_students: int
    certificates_issued: int
    active_workshops: int


class StudentDashboardStats(BaseModel):
    enrolled_workshops: int
    completed_assessments: int
    average_score: float
    certificates_earned: int


class EducatorDashboardStats(BaseModel):
    assigned_workshops: int
    materials_uploaded: int
    active_assessments: int
    pending_submissions: int

# ---------------------------------------------------------------------------
# Approvals + Salary (Admin Panels)
# ---------------------------------------------------------------------------


class ApprovalRequestCreate(BaseModel):
    request_type: str
    payload: dict = {}


class ApprovalRequestResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    request_type: str
    status: str
    payload: dict
    requested_by: Optional[str]
    created_at: Optional[datetime]
    resolved_at: Optional[datetime]


class SalaryPaymentCreate(BaseModel):
    educator_id: str
    month: str
    amount: int = 0


class SalaryPaymentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    educator_id: str
    month: str
    amount: int
    status: str
    created_at: Optional[datetime]


class ParentMessageRequest(BaseModel):
    student_ids: list[str]
    subject: str
    body: str


class ParentMessageResponse(BaseModel):
    accepted: int
    failed: int
    message: str


class ParentContactItem(BaseModel):
    student_id: str
    parent_name: Optional[str] = None
    parent_email: Optional[str] = None


class ParentContactDirectoryResponse(BaseModel):
    items: list[ParentContactItem]
    total: int


class CertificateRecommendationRequest(BaseModel):
    student_id: str
    workshop_id: str
    note: Optional[str] = None


class CertificateRecommendationResponse(BaseModel):
    accepted: int
    failed: int
    message: str


class CertificateDownloadResponse(BaseModel):
    certificate_id: str
    download_url: str


class MaterialDownloadResponse(BaseModel):
    module_id: str
    material_id: str
    download_url: str
