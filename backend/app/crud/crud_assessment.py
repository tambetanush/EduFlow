from __future__ import annotations

from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assessment, Question, Submission
from app.schemas.assessment import (
    AssessmentCreate,
    AssessmentUpdate,
    AnswerBatch,
    QuestionCreate,
    QuestionUpdate,
    SubmissionCreate,
    SubmissionUpdate,
)


# ---------------------------------------------------------------------------
# Assessment CRUD
# ---------------------------------------------------------------------------


async def create_assessment(
    db: AsyncSession, data: AssessmentCreate
) -> Assessment:
    assessment = Assessment(**data.model_dump())
    db.add(assessment)
    await db.flush()
    await db.refresh(assessment)
    return assessment


async def get_assessment(
    db: AsyncSession, assessment_id: str
) -> Optional[Assessment]:
    return await db.get(Assessment, assessment_id)


async def get_assessments_by_workshop(
    db: AsyncSession, workshop_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Assessment], int]:
    """Return (assessments, total_count) for a workshop."""
    q = select(Assessment).where(Assessment.workshop_id == workshop_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def get_assessments_by_module(
    db: AsyncSession, module_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Assessment], int]:
    """Return (assessments, total_count) for a module."""
    q = select(Assessment).where(Assessment.module_id == module_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def update_assessment(
    db: AsyncSession, assessment: Assessment, data: AssessmentUpdate
) -> Assessment:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(assessment, field, value)
    await db.flush()
    await db.refresh(assessment)
    return assessment


async def delete_assessment(db: AsyncSession, assessment: Assessment) -> None:
    await db.delete(assessment)
    await db.flush()


# ---------------------------------------------------------------------------
# Question CRUD
# ---------------------------------------------------------------------------


async def create_question(db: AsyncSession, data: QuestionCreate) -> Question:
    payload = data.model_dump()
    # Serialise OptionItem sub-models to plain dicts for the JSON column
    payload["options"] = [opt.model_dump() for opt in data.options]
    question = Question(**payload)
    db.add(question)
    await db.flush()
    await db.refresh(question)
    return question


async def get_question(db: AsyncSession, question_id: str) -> Optional[Question]:
    return await db.get(Question, question_id)


async def get_questions_by_assessment(
    db: AsyncSession, assessment_id: str, *, offset: int = 0, limit: int = 200
) -> Tuple[Sequence[Question], int]:
    """Return (questions, total_count) for an assessment."""
    q = select(Question).where(Question.assessment_id == assessment_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def update_question(
    db: AsyncSession, question: Question, data: QuestionUpdate
) -> Question:
    payload = data.model_dump(exclude_unset=True)
    if "options" in payload and payload["options"] is not None:
        payload["options"] = [
            opt.model_dump() if hasattr(opt, "model_dump") else opt
            for opt in payload["options"]
        ]
    for field, value in payload.items():
        setattr(question, field, value)
    await db.flush()
    await db.refresh(question)
    return question


async def delete_question(db: AsyncSession, question: Question) -> None:
    await db.delete(question)
    await db.flush()


# ---------------------------------------------------------------------------
# Submission CRUD
# ---------------------------------------------------------------------------


async def create_submission(
    db: AsyncSession, data: SubmissionCreate
) -> Submission:
    payload = data.model_dump()
    # Serialise AnswerItem sub-models to plain dicts for the JSON column
    payload["answers"] = [ans.model_dump() for ans in data.answers]
    submission = Submission(**payload)
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    return submission


async def start_submission(
    db: AsyncSession, student_id: str, assessment_id: str
) -> Submission:
    """Create a blank submission record (test started, no answers yet)."""
    submission = Submission(
        student_id=student_id,
        assessment_id=assessment_id,
        answers=[],
    )
    db.add(submission)
    await db.flush()
    await db.refresh(submission)
    return submission


async def get_submission(
    db: AsyncSession, submission_id: str
) -> Optional[Submission]:
    return await db.get(Submission, submission_id)


async def get_submissions_by_student(
    db: AsyncSession, student_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Submission], int]:
    """Return (submissions, total_count) for a student."""
    q = select(Submission).where(Submission.student_id == student_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def get_submissions_by_assessment(
    db: AsyncSession, assessment_id: str, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Submission], int]:
    """Return (submissions, total_count) for an assessment."""
    q = select(Submission).where(Submission.assessment_id == assessment_id)
    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    items = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return items, total


async def append_answers(
    db: AsyncSession, submission: Submission, batch: AnswerBatch
) -> Submission:
    """Merge new answers into the submission's JSON answers list.

    Existing answers for the same question_id are replaced (upsert-by-question).
    """
    existing: dict[str, dict] = {
        a["question_id"]: a for a in (submission.answers or [])
    }
    for ans in batch.answers:
        existing[ans.question_id] = ans.model_dump()
    submission.answers = list(existing.values())
    await db.flush()
    await db.refresh(submission)
    return submission


async def apply_grade(
    db: AsyncSession,
    submission: Submission,
    score: int,
    total_marks: int,
    pass_fail: bool,
) -> Submission:
    """Persist grading results onto a submission row."""
    submission.score = score
    submission.percentage = round((score / total_marks) * 100) if total_marks else 0
    submission.pass_fail = pass_fail
    await db.flush()
    await db.refresh(submission)
    return submission


async def update_submission(
    db: AsyncSession, submission: Submission, data: SubmissionUpdate
) -> Submission:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(submission, field, value)
    await db.flush()
    await db.refresh(submission)
    return submission


async def delete_submission(db: AsyncSession, submission: Submission) -> None:
    await db.delete(submission)
    await db.flush()