from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_role
from app.crud.crud_assessment import (
    apply_grade,
    get_assessment,
    get_questions_by_assessment,
    get_submission,
    get_submissions_by_student,
    start_submission,
)
from app.models import User, UserRole
from app.schemas.assessment import (
    GradeResult,
    QuestionPublicResponse,
    SubmissionResponse,
    TestStartResponse,
)
from app.services.grading import build_per_question_review
from app.crud.crud_misc import create_notification
from app.schemas.misc import NotificationCreate

router = APIRouter(prefix="/tests", tags=["tests"])


# ────────────────────────────────────────────────────────────────────────────
# POST /tests/{assessment_id}/start
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{assessment_id}/start",
    response_model=TestStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a test — creates a blank submission and returns questions (no correct answers)",
)
async def start_test(
    assessment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> TestStartResponse:
    assessment = await get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    # Prevent double-starting: if student already has an un-graded submission, reuse it
    if current_user.role == UserRole.STUDENT:
        existing_items, _ = await get_submissions_by_student(db, current_user.id, limit=200)
        for sub in existing_items:
            if sub.assessment_id == assessment_id and sub.pass_fail is None:
                # Return the existing in-progress submission
                questions, _ = await get_questions_by_assessment(db, assessment_id, limit=200)
                return TestStartResponse(
                    submission_id=sub.id,
                    assessment_id=assessment_id,
                    title=assessment.title or "",
                    total_marks=assessment.total_marks or 0,
                    questions=[QuestionPublicResponse.model_validate(q) for q in questions],
                )

    submission = await start_submission(db, student_id=current_user.id, assessment_id=assessment_id)
    questions, _ = await get_questions_by_assessment(db, assessment_id, limit=200)
    return TestStartResponse(
        submission_id=submission.id,
        assessment_id=assessment_id,
        title=assessment.title or "",
        total_marks=assessment.total_marks or 0,
        questions=[QuestionPublicResponse.model_validate(q) for q in questions],
    )


# ────────────────────────────────────────────────────────────────────────────
# POST /tests/{assessment_id}/submit
# ────────────────────────────────────────────────────────────────────────────


@router.post(
    "/{assessment_id}/submit",
    response_model=GradeResult,
    summary="Submit test answers — auto-grades MCQ/MSQ, persists score and pass/fail",
)
async def submit_test(
    assessment_id: str,
    submission_id: str,  # passed as query param
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
) -> GradeResult:
    assessment = await get_assessment(db, assessment_id)
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")

    submission = await get_submission(db, submission_id)
    if not submission or submission.assessment_id != assessment_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found.")

    # Students can only submit their own submission
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    # Already graded?
    if submission.pass_fail is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This submission has already been graded.",
        )

    # Load all questions (up to 500) for grading
    questions, _ = await get_questions_by_assessment(db, assessment_id, limit=500)

    per_question = build_per_question_review(
        questions=list(questions),
        answers=submission.answers or [],
    )
    correct_count = sum(1 for item in per_question if item["is_correct"])
    total_questions = len(per_question)
    percentage_score = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0.0
    pass_fail = percentage_score >= 60.0

    print("[grading] answers received:", submission.answers or [])
    print("[grading] correct answers:", [
        {"question_id": question.id, "correct_option_ids": [opt.get("id") for opt in (question.options or []) if opt.get("is_correct")]}
        for question in questions
    ])

    # Persist grades
    await apply_grade(
        db,
        submission,
        score=round(percentage_score),
        total_marks=100,
        pass_fail=pass_fail,
    )

    if submission.student_id:
        await create_notification(
            db,
            NotificationCreate(
                user_id=submission.student_id,
                title="Assessment graded",
                message=f"Your score: {round(percentage_score)}%",
                notification_type="success",
            ),
        )

    return GradeResult(
        submission_id=submission.id,
        score=percentage_score,
        correct_count=correct_count,
        total=total_questions,
        pass_fail=pass_fail,
        per_question=per_question,
    )