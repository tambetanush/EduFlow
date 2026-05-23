from __future__ import annotations

import asyncio
import logging
import random
from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.crud.crud_ai_generation import get_ai_generation, update_ai_generation
from app.crud.crud_misc import create_notification
from app.db import AsyncSessionLocal
from app.models import (
    AIFeatureType,
    AIGeneration,
    AIGenerationStatus,
    NotificationType,
)
from app.schemas.ai import (
    AIGenerationUpdate,
    AITokenUsage,
)
from app.schemas.misc import NotificationCreate
from app.services.ai.admin_report_context import build_admin_report_context
from app.services.ai.admin_report_prompt import build_admin_report_prompt
from app.services.ai.cache import compute_cache_expiry
from app.services.ai.gemini_client import GeminiClient, GeminiTransientError
from app.services.ai.student_explanation_prompt import build_student_explanation_prompt
from app.services.ai.validation import (
    validate_admin_report_output,
    validate_student_explanation_output,
)

logger = logging.getLogger(__name__)

def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None

def _utc_now() -> datetime:
    return datetime.now(timezone.utc)

async def _with_session(fn):
    async with AsyncSessionLocal() as session:
        try:
            result = await fn(session)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def _mark_failed(
    db: AsyncSession,
    *,
    generation: AIGeneration | None,
    error: Exception,
) -> None:
    if not generation:
        return
    try:
        await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.FAILED,
                error_details={
                    "error_type": error.__class__.__name__,
                    "message": str(error),
                },
            ),
        )
    except Exception:
        return

async def _run_admin_report_attempt(db: AsyncSession, generation_id: str, scheduled_run_id: str | None) -> None:
    generation = await get_ai_generation(db, generation_id)
    if not generation or generation.feature_type != AIFeatureType.ADMIN_REPORT:
        return
    if generation.status == AIGenerationStatus.COMPLETED:
        return

    await update_ai_generation(db, generation, AIGenerationUpdate(status=AIGenerationStatus.PROCESSING))
    await db.commit()  # Release lock during AI call

    request_payload = generation.raw_prompt_input or {}
    date_from = _parse_date(request_payload.get("date_from"))
    date_to = _parse_date(request_payload.get("date_to"))

    try:
        context = await build_admin_report_context(
            db,
            institution_id=generation.institution_id,
            date_from=date_from,
            date_to=date_to,
        )

        compiled_prompt = build_admin_report_prompt(
            request_payload=request_payload,
            analytics_context=context,
        )

        gemini = GeminiClient.from_settings()
        # Fallback to generate_simple for robustness in this direct background task
        raw_text = await gemini.generate_simple(prompt=compiled_prompt)
        
        import json
        import re
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1))
            else:
                raise Exception("Fail to parse AI output as JSON")

        validated = validate_admin_report_output(parsed)

        await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.COMPLETED,
                raw_model_output=raw_text,
                parsed_output_json=validated.model_dump(),
                error_details={},
                cache_expires_at=compute_cache_expiry(ttl_seconds=settings.AI_ADMIN_REPORT_CACHE_TTL_SECONDS),
            ),
        )

        if scheduled_run_id:
            try:
                from app.crud.crud_scheduled_reports import mark_scheduled_run_completed
                await mark_scheduled_run_completed(db, run_id=scheduled_run_id, generation_id=generation_id)
            except Exception as exc:
                logger.warning("Failed to finalize scheduled run %s: %s", scheduled_run_id, exc)

        try:
            await create_notification(
                db,
                NotificationCreate(
                    user_id=generation.requester_user_id,
                    message=f"AI report is ready (id: {generation_id}).",
                    notification_type=NotificationType.GENERAL,
                ),
            )
        except Exception:
            pass
    except Exception as exc:
        await _mark_failed(db, generation=generation, error=exc)
        if scheduled_run_id:
            try:
                from app.crud.crud_scheduled_reports import mark_scheduled_run_failed
                await mark_scheduled_run_failed(
                    db,
                    run_id=scheduled_run_id,
                    error_details={"error_type": exc.__class__.__name__, "message": str(exc)},
                )
            except Exception:
                pass
        raise

async def generate_admin_ai_report(generation_id: str, *, scheduled_run_id: str | None = None) -> None:
    retries = 0
    max_outer_retries = 2
    while True:
        try:
            await _with_session(lambda db: _run_admin_report_attempt(db, generation_id, scheduled_run_id))
            break
        except GeminiTransientError as exc:
            retries += 1
            if retries > max_outer_retries:
                logger.error(f"AI job failed after max retries: {exc}")
                break
            await asyncio.sleep(1.0)
        except Exception as exc:
            logger.error(f"AI job failed: {exc}")
            break

async def _run_student_explanation_attempt(db: AsyncSession, generation_id: str) -> None:
    generation = await get_ai_generation(db, generation_id)
    if not generation or generation.feature_type != AIFeatureType.STUDENT_EXPLANATION:
        return
    if generation.status == AIGenerationStatus.COMPLETED:
        return

    await update_ai_generation(db, generation, AIGenerationUpdate(status=AIGenerationStatus.PROCESSING))
    await db.commit()  # Release lock during AI call

    try:
        raw = generation.raw_prompt_input or {}
        prompt_payload = raw.get("prompt_payload") if isinstance(raw, dict) else None
        if not isinstance(prompt_payload, dict):
            prompt_payload = {}
        disallowed_option_ids = (raw.get("correct_option_ids") if isinstance(raw, dict) else None) or []
        disallowed_option_texts = (raw.get("correct_option_texts") if isinstance(raw, dict) else None) or []
        if not isinstance(disallowed_option_ids, list):
            disallowed_option_ids = []
        if not isinstance(disallowed_option_texts, list):
            disallowed_option_texts = []
        disallowed_option_ids = [str(v) for v in disallowed_option_ids if v]
        disallowed_option_texts = [str(v) for v in disallowed_option_texts if v]

        prompt = build_student_explanation_prompt(prompt_payload=prompt_payload)

        gemini = GeminiClient.from_settings()
        raw_text = await gemini.generate_simple(prompt=prompt)
        
        import json
        import re
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group(1))
            else:
                raise Exception("Fail to parse AI output as JSON")

        validated = validate_student_explanation_output(
            parsed,
            disallowed_option_ids=disallowed_option_ids,
            disallowed_option_texts=disallowed_option_texts,
        )

        await update_ai_generation(
            db,
            generation,
            AIGenerationUpdate(
                status=AIGenerationStatus.COMPLETED,
                raw_model_output=raw_text,
                parsed_output_json=validated.model_dump(),
                error_details={},
                cache_expires_at=compute_cache_expiry(ttl_seconds=settings.AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS),
            ),
        )

    except Exception as exc:
        await _mark_failed(db, generation=generation, error=exc)
        raise

async def generate_student_explanation(generation_id: str) -> None:
    retries = 0
    max_outer_retries = 2
    while True:
        try:
            await _with_session(lambda db: _run_student_explanation_attempt(db, generation_id))
            break
        except GeminiTransientError as exc:
            retries += 1
            if retries > max_outer_retries:
                logger.error(f"Student explanation job failed after max retries: {exc}")
                break
            await asyncio.sleep(1.0)
        except Exception as exc:
            logger.error(f"Student explanation job failed: {exc}")
            break

async def _run_tick_scheduled_reports(db: AsyncSession) -> None:
    from app.crud.crud_scheduled_reports import claim_due_scheduled_runs

    claimed_runs = await claim_due_scheduled_runs(
        db,
        now=_utc_now(),
        lookahead_seconds=settings.SCHEDULED_REPORT_LOOKAHEAD_SECONDS,
    )
    if not claimed_runs:
        return

    for run_info in claimed_runs:
        try:
            asyncio.create_task(generate_admin_ai_report(run_info.ai_generation_id, scheduled_run_id=run_info.id))
        except Exception as exc:
            logger.exception("Failed to enqueue scheduled report generation %s", run_info.ai_generation_id)
            try:
                from app.crud.crud_scheduled_reports import mark_scheduled_run_failed
                await mark_scheduled_run_failed(
                    db, run_id=run_info.id, error_details={"error_type": exc.__class__.__name__, "message": str(exc)}
                )
            except Exception:
                pass

async def tick_scheduled_ai_reports() -> None:
    try:
        await _with_session(_run_tick_scheduled_reports)
    except Exception as exc:
        logger.exception("Failed tick_scheduled_ai_reports task %s", exc)
