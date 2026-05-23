from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_validator, model_validator

from app.models import QuestionType


# ---------------------------------------------------------------------------
# OptionItem (embedded in Question.options JSON column)
# ---------------------------------------------------------------------------


class OptionItem(BaseModel):
    id: str
    text: str
    is_correct: bool = False


# ---------------------------------------------------------------------------
# OptionItemPublic — strips is_correct before sending to students
# ---------------------------------------------------------------------------


class OptionItemPublic(BaseModel):
    id: str
    text: str


# ---------------------------------------------------------------------------
# AnswerItem (embedded in Submission.answers JSON column)
# Supports both MCQ (single string) and MSQ (list of strings)
# ---------------------------------------------------------------------------


class AnswerItem(BaseModel):
    question_id: str
    # For MCQ: one option id; for MSQ: multiple option ids
    selected_option_ids: List[str] = []

    @model_validator(mode="before")
    @classmethod
    def _normalise_legacy(cls, data: object) -> object:
        """Accept old single-string format ``selected_option_id`` for compatibility."""
        if isinstance(data, dict):
            if "selected_option_id" in data and "selected_option_ids" not in data:
                sid = data.pop("selected_option_id")
                data["selected_option_ids"] = [sid] if sid else []
        return data


# ---------------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------------


class AssessmentCreate(BaseModel):
    workshop_id: str
    module_id: Optional[str] = None
    title: str
    total_marks: int = 0
    pass_mark: int = 0  # minimum marks needed to pass


class AssessmentUpdate(BaseModel):
    title: Optional[str] = None
    total_marks: Optional[int] = None
    pass_mark: Optional[int] = None
    module_id: Optional[str] = None


class AssessmentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    workshop_id: Optional[str]
    module_id: Optional[str]
    title: Optional[str]
    total_marks: Optional[int]
    pass_mark: Optional[int] = 0


# ---------------------------------------------------------------------------
# Question — full (admin/educator view, includes is_correct)
# ---------------------------------------------------------------------------


class QuestionCreate(BaseModel):
    assessment_id: str
    text: str
    type: QuestionType
    marks: int = 1
    options: list[OptionItem] = []


class QuestionUpdate(BaseModel):
    text: Optional[str] = None
    type: Optional[QuestionType] = None
    marks: Optional[int] = None
    options: Optional[list[OptionItem]] = None


class QuestionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    assessment_id: Optional[str]
    text: Optional[str]
    type: Optional[QuestionType]
    marks: Optional[int]
    options: list[OptionItem] = []

    @field_validator("options", mode="before")
    @classmethod
    def coerce_options(cls, v: object) -> list[OptionItem]:
        if v is None:
            return []
        if isinstance(v, list):
            return [OptionItem(**item) if isinstance(item, dict) else item for item in v]
        return v  # type: ignore[return-value]


# Question as seen by a student (no is_correct)
class QuestionPublicResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    assessment_id: Optional[str]
    text: Optional[str]
    type: Optional[QuestionType]
    marks: Optional[int]
    options: list[OptionItemPublic] = []

    @field_validator("options", mode="before")
    @classmethod
    def coerce_options(cls, v: object) -> list[OptionItemPublic]:
        if v is None:
            return []
        if isinstance(v, list):
            return [OptionItemPublic(**item) if isinstance(item, dict) else OptionItemPublic(id=item.id, text=item.text) for item in v]
        return v  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Submission
# ---------------------------------------------------------------------------


class SubmissionCreate(BaseModel):
    student_id: str
    assessment_id: str
    answers: list[AnswerItem] = []


class SubmissionUpdate(BaseModel):
    score: Optional[int] = None
    percentage: Optional[int] = None
    pass_fail: Optional[bool] = None


class AnswerBatch(BaseModel):
    """Body for POST /submissions/{id}/answers — append/replace answers."""
    answers: list[AnswerItem]


class SubmissionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    student_id: Optional[str]
    assessment_id: Optional[str]
    score: Optional[int]
    percentage: Optional[int]
    pass_fail: Optional[bool] = None
    answers: list[AnswerItem] = []
    submitted_at: Optional[datetime]

    @field_validator("answers", mode="before")
    @classmethod
    def coerce_answers(cls, v: object) -> list[AnswerItem]:
        if v is None:
            return []
        if isinstance(v, list):
            return [AnswerItem(**item) if isinstance(item, dict) else item for item in v]
        return v  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Test Start / Submit responses
# ---------------------------------------------------------------------------


class TestStartResponse(BaseModel):
    """Returned when a student starts a test (hides correct answers)."""
    submission_id: str
    assessment_id: str
    title: str
    total_marks: int
    questions: list[QuestionPublicResponse]


class GradeResult(BaseModel):
    """Returned by POST /tests/{id}/submit."""
    submission_id: str
    score: float
    correct_count: int
    total: int
    pass_fail: bool
    per_question: list["PerQuestionResultItem"] = []


class PerQuestionOption(BaseModel):
    id: str
    text: str


class PerQuestionResultItem(BaseModel):
    question_id: str
    question_text: str
    options: list[PerQuestionOption] = []
    student_answer_ids: list[str] = []  # For MSQ: can have multiple
    correct_answer_ids: list[str] = []  # For MSQ: can have multiple
    is_correct: bool
    explanation: Optional[str] = None
    # Legacy single-ID fields for backward compatibility
    student_answer_id: Optional[str] = None
    correct_answer_id: Optional[str] = None


class SubmissionResultResponse(BaseModel):
    submission_id: str
    assessment_id: str
    student_id: str
    score: float
    correct_count: int
    total: int
    pass_fail: bool
    per_question: list[PerQuestionResultItem] = []


class SubmissionReviewQuestion(BaseModel):
    question_id: str
    question_text: str
    selected_option_ids: list[str] = []
    selected_option_texts: list[str] = []
    correct_option_ids: list[str] = []
    correct_option_texts: list[str] = []
    earned_marks: int
    max_marks: int
    is_correct: bool


class SubmissionReviewResponse(BaseModel):
    submission_id: str
    assessment_id: str
    student_id: str
    score: int
    total_marks: int
    percentage: float
    pass_fail: bool
    questions: list[SubmissionReviewQuestion] = []


GradeResult.model_rebuild()
