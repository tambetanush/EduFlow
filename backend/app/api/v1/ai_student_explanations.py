from __future__ import annotations

import asyncio
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.config import settings
from app.crud.crud_ai_generation import (
    create_ai_generation,
    fail_stale_active_generations,
    find_active_generation_by_fingerprint,
    find_cached_completed_generation,
    get_ai_generation,
    find_generation_by_idempotency_key,
)
from app.crud.crud_assessment import get_question, get_submission
from app.models import AIFeatureType, AIGenerationStatus, User, UserRole
from app.schemas.ai import (
    AIGenerationCreate,
    StudentExplanationCreateRequest,
    StudentExplanationCreateResponse,
    StudentExplanationResultResponse,
    StudentExplanationStatusResponse,
)
from app.services.ai.cache import (
    build_student_explanation_request_fingerprint,
    compute_cache_expiry,
)

router = APIRouter(prefix="/ai/student-explanations", tags=["ai-student-explanations"])

# Rate limits removed as requested by user to eliminate bottlenecks

@router.post(
    "/",
    response_model=StudentExplanationCreateResponse,
    summary="Generate student-facing explanation for an incorrect answer",
)
async def create_student_explanation(
    payload: StudentExplanationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> StudentExplanationCreateResponse:
    submission = await get_submission(db, payload.submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
    if submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    if submission.pass_fail is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submission is not graded yet.",
        )

    question = await get_question(db, payload.question_id)
    if not question or question.assessment_id != submission.assessment_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found in this submission.")

    answers = submission.answers or []
    answer_row = next(
        (
            item
            for item in answers
            if isinstance(item, dict) and item.get("question_id") == payload.question_id
        ),
        None,
    )
    selected_option_ids = (
        answer_row.get("selected_option_ids", [])
        if isinstance(answer_row, dict)
        else []
    )
    if not isinstance(selected_option_ids, list):
        selected_option_ids = []
    selected_option_ids = [str(value) for value in selected_option_ids if value]
    if not selected_option_ids:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Question has no submitted answer for explanation.",
        )

    options = question.options or []
    option_lookup = {
        str(item.get("id")): str(item.get("text", ""))
        for item in options
        if isinstance(item, dict) and item.get("id")
    }
    correct_option_ids = [
        str(item.get("id"))
        for item in options
        if isinstance(item, dict) and item.get("id") and item.get("is_correct")
    ]
    selected_option_texts = [option_lookup.get(option_id, "") for option_id in selected_option_ids]
    correct_option_texts = [option_lookup.get(option_id, "") for option_id in correct_option_ids]

    if sorted(selected_option_ids) == sorted(correct_option_ids):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Explanation is available only for incorrect answers.",
        )

    prompt_payload = {
        "question_id": question.id,
        "question_text": question.text or "",
        "question_type": question.type.value if hasattr(question.type, "value") else str(question.type or ""),
        "student_selected_option_texts": selected_option_texts,
        "student_selected_option_ids": selected_option_ids,
        "correct_option_texts_internal_only": correct_option_texts,
    }
    raw_prompt_input = {
        "prompt_payload": prompt_payload,
        "correct_option_ids": correct_option_ids,
        "correct_option_texts": correct_option_texts,
    }
    request_fingerprint = build_student_explanation_request_fingerprint(
        student_id=current_user.id,
        submission_id=submission.id,
        question_id=question.id,
        prompt_version=settings.AI_STUDENT_EXPLANATION_PROMPT_VERSION,
        model_name=settings.GEMINI_MODEL_NAME,
        raw_prompt_input=raw_prompt_input,
    )

    # Simple Database-based idempotency check
    if idempotency_key:
        existing = await find_generation_by_idempotency_key(
            db,
            user_id=current_user.id,
            feature_type=AIFeatureType.STUDENT_EXPLANATION,
            idempotency_key=idempotency_key
        )
        if existing:
            return StudentExplanationCreateResponse(
                explanation_id=existing.id,
                status=existing.status,
                from_cache=False,
                explanation=None,
            )

    await fail_stale_active_generations(
        db,
        feature_type=AIFeatureType.STUDENT_EXPLANATION,
        stale_after_seconds=settings.AI_STUDENT_EXPLANATION_STALE_AFTER_SECONDS,
        request_fingerprint=request_fingerprint,
    )

    if not payload.force_regenerate:
        active = await find_active_generation_by_fingerprint(
            db,
            feature_type=AIFeatureType.STUDENT_EXPLANATION,
            request_fingerprint=request_fingerprint,
        )
        if active:
            return StudentExplanationCreateResponse(
                explanation_id=active.id,
                status=active.status,
                from_cache=False,
                explanation=None,
            )

        cached = await find_cached_completed_generation(
            db,
            feature_type=AIFeatureType.STUDENT_EXPLANATION,
            request_fingerprint=request_fingerprint,
        )
        if cached and isinstance(cached.parsed_output_json, dict):
            from app.services.ai.validation import validate_student_explanation_output
            validated_cached = validate_student_explanation_output(
                cached.parsed_output_json,
                disallowed_option_ids=correct_option_ids,
                disallowed_option_texts=correct_option_texts,
            )
            return StudentExplanationCreateResponse(
                explanation_id=cached.id,
                status=cached.status,
                from_cache=True,
                explanation=validated_cached,
            )

    generation = await create_ai_generation(
        db,
        AIGenerationCreate(
            feature_type=AIFeatureType.STUDENT_EXPLANATION,
            requester_user_id=current_user.id,
            institution_id=current_user.institution_id,
            source_entity_type="submission_question",
            source_entity_id=f"{submission.id}:{question.id}",
            prompt_version=settings.AI_STUDENT_EXPLANATION_PROMPT_VERSION,
            model_name=settings.GEMINI_MODEL_NAME,
            raw_prompt_input=raw_prompt_input,
            request_fingerprint=request_fingerprint,
            idempotency_key=idempotency_key,
            cache_expires_at=compute_cache_expiry(ttl_seconds=settings.AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS),
        ),
    )

    # Directly call AI synchronously/inline
    from app.services.ai.student_explanation_prompt import build_student_explanation_prompt
    from app.services.ai.gemini_client import GeminiClient
    from app.crud.crud_ai_generation import update_ai_generation
    from app.schemas.ai import AIGenerationUpdate
    import json
    import re

    # 1. Update status
    await update_ai_generation(db, generation, AIGenerationUpdate(status=AIGenerationStatus.PROCESSING))
    await db.commit()  # Release DB lock while processing AI
    
    # 2. Build prompt
    prompt = build_student_explanation_prompt(prompt_payload=prompt_payload)
    
    # 3. Call AI simply
    try:
        gemini = GeminiClient.from_settings()
        raw_text = await gemini.generate_simple(prompt=prompt)
        
        # 4. Extract and parse JSON (Best-Effort)
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1))
            else:
                raise Exception("Fail to parse AI output as JSON")
        
        # 5. Persist
        generation = await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.COMPLETED,
                raw_model_output=raw_text,
                parsed_output_json=parsed,
                cache_expires_at=compute_cache_expiry(ttl_seconds=settings.AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS),
            ),
        )
    except Exception as e:
        await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.FAILED,
                error_details={"message": str(e)},
            ),
        )

    # Refetch correctly formatted generation
    generation = await get_ai_generation(db, generation.id)

    validated_explanation = None
    if generation and generation.status == AIGenerationStatus.COMPLETED and isinstance(generation.parsed_output_json, dict):
        from app.services.ai.validation import validate_student_explanation_output
        validated_explanation = validate_student_explanation_output(
            generation.parsed_output_json,
            disallowed_option_ids=correct_option_ids,
            disallowed_option_texts=correct_option_texts,
        )

    return StudentExplanationCreateResponse(
        explanation_id=generation.id,
        status=generation.status if generation else AIGenerationStatus.FAILED,
        from_cache=False,
        explanation=validated_explanation,
    )


@router.get(
    "/{explanation_id}/status",
    response_model=StudentExplanationStatusResponse,
    summary="Get student explanation generation status",
)
async def get_student_explanation_status(
    explanation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> StudentExplanationStatusResponse:
    report = await get_ai_generation(db, explanation_id)
    if not report or report.feature_type != AIFeatureType.STUDENT_EXPLANATION:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explanation not found.")
    if report.requester_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    # Progress tracking removed as it relied on Redis
    return StudentExplanationStatusResponse(
        explanation_id=report.id,
        status=report.status,
        error_details=report.error_details,
        progress=None,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.get(
    "/{explanation_id}/result",
    response_model=StudentExplanationResultResponse,
    summary="Get completed student explanation result",
)
async def get_student_explanation_result(
    explanation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> StudentExplanationResultResponse:
    report = await get_ai_generation(db, explanation_id)
    if not report or report.feature_type != AIFeatureType.STUDENT_EXPLANATION:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Explanation not found.")
    if report.requester_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if report.status != AIGenerationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Explanation is not completed yet.",
        )
    if not isinstance(report.parsed_output_json, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored explanation output is invalid.",
        )

    from app.services.ai.validation import validate_student_explanation_output
    validated = validate_student_explanation_output(report.parsed_output_json)
    return StudentExplanationResultResponse(
        explanation_id=report.id,
        status=report.status,
        explanation=validated,
        created_at=report.created_at,
        updated_at=report.updated_at,
        prompt_version=report.prompt_version,
        model_name=report.model_name,
    )
