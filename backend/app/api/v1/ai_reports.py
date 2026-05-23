from __future__ import annotations

import asyncio
from fastapi import (APIRouter, Depends, Header, HTTPException, Query, status)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_db, require_role
from app.config import settings
from app.crud.crud_ai_generation import (fail_stale_active_generations,
                                         find_active_generation_by_fingerprint,
                                         find_cached_completed_generation,
                                         get_ai_generation,
                                         list_ai_generations,
                                         find_generation_by_idempotency_key)
from app.models import (AIFeatureType, AIGeneration, AIGenerationStatus, User,
                        UserRole)
from app.schemas.ai import (AdminAIReportCreateRequest,
                            AdminAIReportCreateResponse, AdminAIReportListItem,
                            AdminAIReportResultResponse,
                            AdminAIReportStatusResponse,
                            AIGenerationCreate)
from app.schemas.base import Page
from app.services.ai.admin_report_pipeline import \
    request_admin_report_generation
from app.services.ai.cache import build_admin_report_request_fingerprint

router = APIRouter(prefix="/ai/reports", tags=["ai-reports"])

# Rate limits removed as requested by user to eliminate bottlenecks

def _resolve_scope(
    payload: AdminAIReportCreateRequest,
    current_user: User,
) -> tuple[str | None, str, str]:
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admin is not linked to any institution.",
            )
        if payload.institution_id and payload.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot generate reports outside your institution scope.",
            )
        return current_user.institution_id, "institution", current_user.institution_id

    if current_user.role == UserRole.ADMIN:
        if payload.institution_id:
            return payload.institution_id, "institution", payload.institution_id
        return None, "platform", "global"

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied.",
    )


def _assert_report_access(report: AIGeneration, current_user: User) -> None:
    if current_user.role == UserRole.ADMIN:
        return

    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admin is not linked to any institution.",
            )
        if report.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this report scope.",
            )
        return

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")


@router.post(
    "/",
    response_model=AdminAIReportCreateResponse,
    summary="Create and generate an admin AI report",
)
async def create_admin_ai_report(
    payload: AdminAIReportCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> AdminAIReportCreateResponse:
    institution_id, source_entity_type, source_entity_id = _resolve_scope(payload, current_user)
    request_payload = payload.model_dump(mode="json")
    fingerprint_payload = {
        **request_payload,
        "institution_id": institution_id,
        "source_entity_type": source_entity_type,
        "source_entity_id": source_entity_id,
    }
    request_fingerprint = build_admin_report_request_fingerprint(
        institution_id=institution_id,
        source_entity_type=source_entity_type,
        source_entity_id=source_entity_id,
        prompt_version=settings.AI_ADMIN_REPORT_PROMPT_VERSION,
        model_name=settings.GEMINI_MODEL_NAME,
        raw_prompt_input=fingerprint_payload,
    )

    # Simple Database-based idempotency check
    if idempotency_key:
        existing = await find_generation_by_idempotency_key(
            db,
            user_id=current_user.id,
            feature_type=AIFeatureType.ADMIN_REPORT,
            idempotency_key=idempotency_key
        )
        if existing:
            return AdminAIReportCreateResponse(
                report_id=existing.id,
                status=existing.status,
                from_cache=False,
                deduplicated=True,
                result=existing.parsed_output_json if existing.status == AIGenerationStatus.COMPLETED else None,
            )

    await fail_stale_active_generations(
        db,
        feature_type=AIFeatureType.ADMIN_REPORT,
        stale_after_seconds=settings.AI_ADMIN_REPORT_STALE_AFTER_SECONDS,
    )

    if not payload.force_regenerate:
        active = await find_active_generation_by_fingerprint(
            db,
            feature_type=AIFeatureType.ADMIN_REPORT,
            request_fingerprint=request_fingerprint,
        )
        if active:
            return AdminAIReportCreateResponse(
                report_id=active.id,
                status=active.status,
                from_cache=False,
                deduplicated=True,
                result=active.parsed_output_json if active.status == AIGenerationStatus.COMPLETED else None,
            )

        cached = await find_cached_completed_generation(
            db,
            feature_type=AIFeatureType.ADMIN_REPORT,
            request_fingerprint=request_fingerprint,
        )
        if cached:
            return AdminAIReportCreateResponse(
                report_id=cached.id,
                status=cached.status,
                from_cache=True,
                deduplicated=True,
                result=cached.parsed_output_json,
            )

    from app.crud.crud_ai_generation import create_ai_generation
    generation = await create_ai_generation(
        db,
        AIGenerationCreate(
            feature_type=AIFeatureType.ADMIN_REPORT,
            requester_user_id=current_user.id,
            institution_id=institution_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            prompt_version=settings.AI_ADMIN_REPORT_PROMPT_VERSION,
            model_name=settings.GEMINI_MODEL_NAME,
            raw_prompt_input=fingerprint_payload,
            request_fingerprint=request_fingerprint,
            idempotency_key=idempotency_key,
            cache_expires_at=None,
        ),
    )

    # Direct execution without complex pipeline
    if generation.status in (AIGenerationStatus.PENDING, AIGenerationStatus.PROCESSING):
        from app.services.ai.admin_report_context import build_admin_report_context
        from app.services.ai.admin_report_prompt import build_admin_report_prompt
        from app.services.ai.gemini_client import GeminiClient
        from app.crud.crud_ai_generation import update_ai_generation
        from app.schemas.ai import AIGenerationUpdate
        from app.services.ai.cache import compute_cache_expiry
        import json
        import re

        try:
            # 1. Update status
            await update_ai_generation(db, generation, AIGenerationUpdate(status=AIGenerationStatus.PROCESSING))
            await db.commit()  # Release DB lock while processing AI
            
            # 2. Build context and prompt (synchronous/inline)
            context = await build_admin_report_context(
                db, 
                institution_id=generation.institution_id, 
                date_from=payload.date_from, 
                date_to=payload.date_to
            )
            prompt = build_admin_report_prompt(request_payload=request_payload, analytics_context=context)
            
            # 3. Call AI simply
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
                    cache_expires_at=compute_cache_expiry(ttl_seconds=settings.AI_ADMIN_REPORT_CACHE_TTL_SECONDS),
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

    return AdminAIReportCreateResponse(
        report_id=generation.id,
        status=generation.status,
        from_cache=False,
        deduplicated=False,
        result=generation.parsed_output_json if generation.status == AIGenerationStatus.COMPLETED else None,
    )


@router.get(
    "/{report_id}/status",
    response_model=AdminAIReportStatusResponse,
    summary="Get admin AI report generation status",
)
async def get_admin_ai_report_status(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> AdminAIReportStatusResponse:
    report = await get_ai_generation(db, report_id)
    if not report or report.feature_type != AIFeatureType.ADMIN_REPORT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _assert_report_access(report, current_user)
    
    # Progress tracking removed as it relied on Redis
    return AdminAIReportStatusResponse(
        report_id=report.id,
        status=report.status,
        error_details=report.error_details,
        progress=None,
        created_at=report.created_at,
        updated_at=report.updated_at,
    )


@router.get(
    "/{report_id}/result",
    response_model=AdminAIReportResultResponse,
    summary="Get completed admin AI report result",
)
async def get_admin_ai_report_result(
    report_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> AdminAIReportResultResponse:
    report = await get_ai_generation(db, report_id)
    if not report or report.feature_type != AIFeatureType.ADMIN_REPORT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found.")
    _assert_report_access(report, current_user)

    if report.status != AIGenerationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Report is not completed yet.",
        )
    if not isinstance(report.parsed_output_json, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored report output is invalid.",
        )

    from app.services.ai.validation import validate_admin_report_output
    validated = validate_admin_report_output(report.parsed_output_json)
    return AdminAIReportResultResponse(
        report_id=report.id,
        status=report.status,
        result=validated,
        created_at=report.created_at,
        updated_at=report.updated_at,
        prompt_version=report.prompt_version,
        model_name=report.model_name,
    )


@router.get(
    "/",
    response_model=Page[AdminAIReportListItem],
    summary="List previous admin AI reports",
)
async def list_admin_ai_reports(
    page: PaginationParams = Depends(),
    institution_id: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> Page[AdminAIReportListItem]:
    scoped_institution_id = institution_id
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admin is not linked to any institution.",
            )
        if scoped_institution_id and scoped_institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot list reports outside your institution scope.",
            )
        scoped_institution_id = current_user.institution_id

    rows, total = await list_ai_generations(
        db,
        feature_type=AIFeatureType.ADMIN_REPORT,
        institution_id=scoped_institution_id,
        offset=page.offset,
        limit=page.limit,
    )
    items = [
        AdminAIReportListItem(
            report_id=row.id,
            status=row.status,
            institution_id=row.institution_id,
            source_entity_type=row.source_entity_type,
            source_entity_id=row.source_entity_id,
            prompt_version=row.prompt_version,
            model_name=row.model_name,
            summary_preview=(row.parsed_output_json or {}).get("summary")
            if isinstance(row.parsed_output_json, dict)
            else None,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]
    return Page(items=items, total=total, offset=page.offset, limit=page.limit)
