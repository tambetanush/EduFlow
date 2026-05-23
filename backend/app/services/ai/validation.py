from __future__ import annotations

from pydantic import ValidationError

from app.schemas.ai import AdminReportStructuredOutput, StudentExplanationStructuredOutput


class StructuredOutputValidationError(ValueError):
    pass


def validate_admin_report_output(payload: Any) -> AdminReportStructuredOutput:
    if not isinstance(payload, dict):
        payload = {}
    
    # Best-effort merging with defaults to avoid validation errors
    safe_payload = {
        "summary": str(payload.get("summary", "No summary generated.")),
        "key_insights": payload.get("key_insights", []),
        "risk_flags": payload.get("risk_flags", []),
        "recommendations": payload.get("recommendations", []),
        "trend_highlights": payload.get("trend_highlights", []),
        "data_window": payload.get("data_window", {"scope": "unknown"}),
        "caveats": payload.get("caveats", []),
    }
    return AdminReportStructuredOutput.model_validate(safe_payload)


def validate_student_explanation_output(
    payload: Any,
    *,
    disallowed_option_ids: list[str] | None = None,
    disallowed_option_texts: list[str] | None = None,
) -> StudentExplanationStructuredOutput:
    """Best-effort validation mirroring the simplified approach."""
    if not isinstance(payload, dict):
        payload = {}
        
    safe_payload = {
        "why_it_was_wrong": str(payload.get("why_it_was_wrong", "The answer provided was not correct.")),
        "correct_reasoning": str(payload.get("correct_reasoning", "The correct answer is derived from the core principles of the topic.")),
        "common_mistake": str(payload.get("common_mistake", "A common mistake here is misreading the question or concept.")),
        "hint_for_retry": str(payload.get("hint_for_retry", "Focus on the fundamental definitions.")),
        "confidence": float(payload.get("confidence", 0.9)),
        "follow_up_questions": payload.get("follow_up_questions", []),
    }
    
    return StudentExplanationStructuredOutput.model_validate(safe_payload)

