from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    PaginationParams,
    ensure_user_can_read_assessments_for_workshop,
    get_current_user,
    get_db,
    require_role,
)
from app.crud.crud_assessment import (
    apply_grade,
    append_answers,
    get_assessment,
    get_questions_by_assessment,
    get_submission,
    get_submissions_by_assessment,
    get_submissions_by_student,
)
from app.models import User, UserRole
from app.schemas.assessment import (
    AnswerBatch,
    SubmissionResponse,
    SubmissionResultResponse,
    SubmissionReviewQuestion,
    SubmissionReviewResponse,
)
from app.schemas.base import Page
from app.services.grading import build_per_question_review

router = APIRouter(prefix="/submissions", tags=["submissions"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


def _build_submission_result_payload(submission, questions) -> SubmissionResultResponse:
    per_question = build_per_question_review(
        questions=list(questions),
        answers=submission.answers or [],
    )
    correct_count = sum(1 for item in per_question if item["is_correct"])
    total = len(per_question)
    score = round((correct_count / total) * 100, 1) if total > 0 else 0.0
    pass_fail = score >= 60.0

    return SubmissionResultResponse(
        submission_id=str(submission.id),
        assessment_id=str(submission.assessment_id),
        student_id=str(submission.student_id or ""),
        score=score,
        correct_count=correct_count,
        total=total,
        pass_fail=pass_fail,
        per_question=per_question,
    )


# ────────────────────────────────────────────────────────────────────────────
# POST /submissions/{submission_id}/answers  — append/upsert answers
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{submission_id}/answers",
    response_model=SubmissionResponse,
    summary="Append or replace answers in a submission (student: own only)",
)
async def post_answers(
    submission_id: str,
    payload: AnswerBatch,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResponse:
    submission = await get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    # Students can only update their own submission
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    # Cannot modify a graded submission
    if submission.pass_fail is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot modify answers on an already-graded submission.",
        )

    updated = await append_answers(db, submission, payload)
    return SubmissionResponse.model_validate(updated)


# ────────────────────────────────────────────────────────────────────────────
# GET /submissions/{submission_id}/result  — view score/pass/fail
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/{submission_id}/result",
    response_model=SubmissionResultResponse,
    summary="Get graded result of a submission",
)
async def get_result(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionResultResponse:
    submission = await get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    # Students see only their own results
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if submission.pass_fail is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This submission has not been graded yet. Submit first.",
        )

    questions, _ = await get_questions_by_assessment(db, submission.assessment_id, limit=500)
    return _build_submission_result_payload(submission, questions)


# ────────────────────────────────────────────────────────────────────────────
# GET /submissions/student/{student_id}
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/student/{student_id}",
    response_model=Page[SubmissionResponse],
    summary="List all submissions for a student",
)
async def list_by_student(
    student_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[SubmissionResponse]:
    if current_user.role == UserRole.STUDENT and current_user.id != student_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    items, total = await get_submissions_by_student(db, student_id, offset=page.offset, limit=page.limit)
    return Page(
        items=[SubmissionResponse.model_validate(s) for s in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ────────────────────────────────────────────────────────────────────────────
# GET /submissions/assessment/{assessment_id}  (staff)
# ────────────────────────────────────────────────────────────────────────────


@router.get(
    "/assessment/{assessment_id}",
    response_model=Page[SubmissionResponse],
    summary="List all submissions for an assessment (staff only)",
)
async def list_by_assessment(
    assessment_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_STAFF)),
) -> Page[SubmissionResponse]:
    assessment = await get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    await ensure_user_can_read_assessments_for_workshop(db, current_user, assessment.workshop_id)
    items, total = await get_submissions_by_assessment(db, assessment_id, offset=page.offset, limit=page.limit)
    return Page(
        items=[SubmissionResponse.model_validate(s) for s in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.get(
    "/{submission_id}/review",
    response_model=SubmissionReviewResponse,
    summary="Detailed graded submission review for staff",
)
async def review_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SubmissionReviewResponse:
    submission = await get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
        
    # Permission check: Staff can see any; Students can see only their own
    is_staff = current_user.role in _STAFF
    if not is_staff and submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if submission.pass_fail is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Submission is not graded yet.")

    assessment = await get_assessment(db, submission.assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    await ensure_user_can_read_assessments_for_workshop(db, current_user, assessment.workshop_id)

    questions, _ = await get_questions_by_assessment(db, submission.assessment_id, limit=500)
    answer_lookup = {
        item.get("question_id"): item.get("selected_option_ids", [])
        for item in (submission.answers or [])
        if isinstance(item, dict)
    }

    review_rows: list[SubmissionReviewQuestion] = []
    total_marks = 0
    for question in questions:
        options = question.options or []
        correct_ids = [opt.get("id") for opt in options if opt.get("is_correct")]
        selected_ids = answer_lookup.get(question.id, [])

        selected_texts = [opt.get("text", "") for opt in options if opt.get("id") in selected_ids]
        correct_texts = [opt.get("text", "") for opt in options if opt.get("id") in correct_ids]
        max_marks = int(question.marks or 0)
        is_correct = sorted(selected_ids) == sorted(correct_ids)
        earned_marks = max_marks if is_correct else 0
        total_marks += max_marks

        review_rows.append(
            SubmissionReviewQuestion(
                question_id=question.id,
                question_text=question.text or "",
                selected_option_ids=selected_ids,
                selected_option_texts=selected_texts,
                correct_option_ids=correct_ids,
                correct_option_texts=correct_texts,
                earned_marks=earned_marks,
                max_marks=max_marks,
                is_correct=is_correct,
            )
        )

    return SubmissionReviewResponse(
        submission_id=submission.id,
        assessment_id=submission.assessment_id,
        student_id=submission.student_id,
        score=int(submission.score or 0),
        total_marks=total_marks,
        percentage=float(submission.percentage or 0),
        pass_fail=bool(submission.pass_fail),
        questions=review_rows,
    )


@router.post(
    "/{submission_id}/grade",
    response_model=SubmissionResultResponse,
    summary="Auto-grade a pending submission (staff only)",
)
async def grade_pending_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_STAFF)),
) -> SubmissionResultResponse:
    submission = await get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")
    if submission.pass_fail is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Submission already graded.")

    assessment = await get_assessment(db, submission.assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    await ensure_user_can_read_assessments_for_workshop(db, current_user, assessment.workshop_id)

    questions, _ = await get_questions_by_assessment(db, submission.assessment_id, limit=500)
    payload = _build_submission_result_payload(submission, questions)
    await apply_grade(
        db,
        submission,
        score=round(payload.score),
        total_marks=100,
        pass_fail=bool(payload.pass_fail),
    )
    return payload