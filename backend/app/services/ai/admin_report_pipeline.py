from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.crud.crud_ai_generation import (create_ai_generation,
                                         fail_stale_active_generations,
                                         find_active_generation_by_fingerprint,
                                         find_cached_completed_generation,
                                         update_ai_generation)
from app.models import AIFeatureType, AIGeneration, AIGenerationStatus
from app.schemas.ai import (ADMIN_REPORT_RESPONSE_JSON_SCHEMA,
                            AIGenerationCreate, AIGenerationUpdate,
                            AITokenUsage)
from app.services.ai.cache import (build_admin_report_request_fingerprint,
                                   compute_cache_expiry)
from app.services.ai.gemini_client import GeminiClient
from app.services.ai.validation import validate_admin_report_output
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class AdminReportRequestResult:
    generation: AIGeneration
    deduplicated: bool
    from_cache: bool


async def request_admin_report_generation(
    db: AsyncSession,
    *,
    requester_user_id: str,
    institution_id: str | None,
    source_entity_type: str,
    source_entity_id: str,
    prompt_version: str,
    model_name: str,
    raw_prompt_input: dict[str, Any],
    fingerprint_input: dict[str, Any] | None = None,
    cache_ttl_seconds: int,
    stale_after_seconds: int = 0,
    force_regenerate: bool = False,
) -> AdminReportRequestResult:
    fingerprint = build_admin_report_request_fingerprint(
        institution_id=institution_id,
        source_entity_type=source_entity_type,
        source_entity_id=source_entity_id,
        prompt_version=prompt_version,
        model_name=model_name,
        raw_prompt_input=fingerprint_input if fingerprint_input is not None else raw_prompt_input,
    )

    if not force_regenerate:
        await fail_stale_active_generations(
            db,
            feature_type=AIFeatureType.ADMIN_REPORT,
            stale_after_seconds=stale_after_seconds,
            request_fingerprint=fingerprint,
        )
        active = await find_active_generation_by_fingerprint(
            db,
            feature_type=AIFeatureType.ADMIN_REPORT,
            request_fingerprint=fingerprint,
        )
        if active:
            return AdminReportRequestResult(generation=active, deduplicated=True, from_cache=False)

        cached = await find_cached_completed_generation(
            db,
            feature_type=AIFeatureType.ADMIN_REPORT,
            request_fingerprint=fingerprint,
        )
        if cached:
            return AdminReportRequestResult(generation=cached, deduplicated=True, from_cache=True)

    generation = await create_ai_generation(
        db,
        AIGenerationCreate(
            feature_type=AIFeatureType.ADMIN_REPORT,
            requester_user_id=requester_user_id,
            institution_id=institution_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            prompt_version=prompt_version,
            model_name=model_name,
            raw_prompt_input=raw_prompt_input,
            request_fingerprint=fingerprint,
            cache_expires_at=compute_cache_expiry(ttl_seconds=cache_ttl_seconds),
        ),
    )
    return AdminReportRequestResult(generation=generation, deduplicated=False, from_cache=False)


async def execute_admin_report_generation(
    db: AsyncSession,
    *,
    generation: AIGeneration,
    compiled_prompt: str,
    gemini_client: GeminiClient,
    cache_ttl_seconds: int,
) -> AIGeneration:
    await update_ai_generation(
        db,
        generation,
        AIGenerationUpdate(status=AIGenerationStatus.PROCESSING),
    )

    try:
        result = await gemini_client.generate_structured(
            prompt=compiled_prompt,
            response_json_schema=ADMIN_REPORT_RESPONSE_JSON_SCHEMA,
        )
        validated = validate_admin_report_output(result.parsed_output)
        return await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.COMPLETED,
                raw_model_output=result.raw_output,
                parsed_output_json=validated.model_dump(),
                error_details={},
                retry_count=result.retries_used,
                token_usage=AITokenUsage(
                    input_tokens=result.usage.input_tokens,
                    output_tokens=result.usage.output_tokens,
                    total_tokens=result.usage.total_tokens,
                ),
                cache_expires_at=compute_cache_expiry(ttl_seconds=cache_ttl_seconds),
            ),
        )
    except Exception as exc:
        await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.FAILED,
                error_details={
                    "error_type": exc.__class__.__name__,
                    "message": str(exc),
                },
            ),
        )
        raise
