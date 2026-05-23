from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def build_admin_report_request_fingerprint(
    *,
    institution_id: str | None,
    source_entity_type: str,
    source_entity_id: str,
    prompt_version: str,
    model_name: str,
    raw_prompt_input: dict[str, Any],
) -> str:
    payload = {
        "feature_type": "admin_report",
        "institution_id": institution_id,
        "source_entity_type": source_entity_type,
        "source_entity_id": source_entity_id,
        "prompt_version": prompt_version,
        "model_name": model_name,
        "raw_prompt_input": raw_prompt_input,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def build_student_explanation_request_fingerprint(
    *,
    student_id: str,
    submission_id: str,
    question_id: str,
    prompt_version: str,
    model_name: str,
    raw_prompt_input: dict[str, Any],
) -> str:
    payload = {
        "feature_type": "student_explanation",
        "student_id": student_id,
        "submission_id": submission_id,
        "question_id": question_id,
        "prompt_version": prompt_version,
        "model_name": model_name,
        "raw_prompt_input": raw_prompt_input,
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def compute_cache_expiry(*, ttl_seconds: int, now: datetime | None = None) -> datetime:
    now = now or datetime.now(timezone.utc)
    return now + timedelta(seconds=ttl_seconds)
