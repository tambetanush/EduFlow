from __future__ import annotations

from datetime import datetime
from typing import Any

from app.models import AIFeatureType, AIGenerationStatus
from app.schemas.base import Page
from pydantic import BaseModel, Field


class SupportConfigResponse(BaseModel):
    # celery_queue and redis_configured removed
    smtp_configured: bool


    ai_max_retries: int
    ai_retry_base_delay_seconds: float

    admin_report_rate_limits: dict[str, Any]
    student_explanation_rate_limits: dict[str, Any]


class SupportJobListItem(BaseModel):
    id: str
    feature_type: AIFeatureType
    status: AIGenerationStatus
    requester_user_id: str
    institution_id: str | None = None
    source_entity_type: str
    source_entity_id: str
    prompt_version: str
    model_name: str
    retry_count: int
    error_details: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    progress: dict[str, Any] | None = None


class SupportJobDetailResponse(SupportJobListItem):
    error_trace: str | None = None


class SupportRerunResponse(BaseModel):
    generation_id: str
    status: AIGenerationStatus
    queued: bool
    message: str


class AuditLogResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    actor_user_id: str | None = None
    actor_role: str | None = None
    action: str
    target_type: str | None = None
    target_id: str | None = None
    metadata_: dict[str, Any]
    created_at: datetime | None = None


class RateLimitEventResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    key: str
    allowed: bool
    remaining: int
    retry_after_seconds: int
    rule_max_requests: int
    rule_window_seconds: int
    actor_user_id: str | None = None
    institution_id: str | None = None
    created_at: datetime | None = None


class CacheStatsResponse(BaseModel):
    now: str
    ai_generations: dict[str, Any]
    # redis field removed



class JobQueryParams(BaseModel):
    status: str | None = None
    feature_type: str | None = None
    institution_id: str | None = None
    requester_user_id: str | None = None
