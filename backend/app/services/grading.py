"""
app/services/grading.py
-----------------------
Pure, synchronous auto-grading logic for MCQ and MSQ questions.
The grading service is kept DB-free so it can be unit-tested with no setup.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QuestionResult:
    question_id: str
    earned: int
    max_marks: int
    correct: bool


@dataclass
class GradingReport:
    score: int
    total_marks: int
    pass_fail: bool
    details: list[QuestionResult] = field(default_factory=list)

    @property
    def percentage(self) -> float:
        if self.total_marks == 0:
            return 0.0
        return round((self.score / self.total_marks) * 100, 2)


def _correct_ids(options: list[dict]) -> set[str]:
    """Return the set of option IDs marked as correct."""
    return {
        _normalize_answer_value(opt.get("id"))
        for opt in options
        if opt.get("is_correct") and _normalize_answer_value(opt.get("id")) is not None
    }


def _normalize_answer_value(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        trimmed = value.strip()
        return trimmed if trimmed else None
    return str(value).strip()


def _extract_selected_option_ids(answer_row: dict) -> list[str]:
    # Canonical field
    raw = answer_row.get("selected_option_ids")
    if isinstance(raw, list):
        normalized = [_normalize_answer_value(item) for item in raw]
        return [item for item in normalized if item]

    # Legacy fields / integration variants
    for key in ("selected_option_id", "selected_option", "option_id", "answer"):
        if key in answer_row:
            value = _normalize_answer_value(answer_row.get(key))
            return [value] if value else []

    return []


def build_per_question_review(
    questions: list[Any],
    answers: list[dict],
) -> list[dict[str, Any]]:
    answer_map: dict[str, list[str]] = {}
    for ans in answers:
        if not isinstance(ans, dict):
            continue
        qid = _normalize_answer_value(ans.get("question_id"))
        if not qid:
            continue
        answer_map[qid] = _extract_selected_option_ids(ans)

    review: list[dict[str, Any]] = []
    for question in questions:
        question_id = _normalize_answer_value(getattr(question, "id", None)) or ""
        options = list(getattr(question, "options", None) or [])
        normalized_options = [
            {
                "id": _normalize_answer_value(item.get("id")) or "",
                "text": str(item.get("text", "")),
            }
            for item in options
            if isinstance(item, dict)
        ]

        correct_ids = _correct_ids(options)
        selected_ids = set(answer_map.get(question_id, []))

        # For display: first item or None
        student_answer_id = next(iter(selected_ids), None) if selected_ids else None
        correct_answer_id = next(iter(correct_ids), None) if correct_ids else None

        if not correct_ids:
            print(f"[grading-warning] No correct answer key found for question_id={question_id}; marking wrong.")

        is_correct = bool(correct_ids) and selected_ids == correct_ids

        review.append(
            {
                "question_id": question_id,
                "question_text": str(getattr(question, "text", "") or ""),
                "options": normalized_options,
                "student_answer_ids": sorted(list(selected_ids)),  # All selected for MSQ
                "correct_answer_ids": sorted(list(correct_ids)),   # All correct for MSQ
                "student_answer_id": student_answer_id,  # Legacy: first only
                "correct_answer_id": correct_answer_id,  # Legacy: first only
                "is_correct": is_correct,
                "explanation": getattr(question, "explanation", None),
            }
        )

    return review


def grade_submission(
    questions: list[Any],
    answers: list[dict],
    pass_mark: int = 0,
) -> GradingReport:
    """Auto-grade MCQ / MSQ submission.

    Args:
        questions: List of SQLAlchemy Question ORM objects (or anything with
                   ``.id``, ``.type``, ``.marks``, ``.options`` attributes).
        answers:   List of raw answer dicts from ``Submission.answers`` JSON column.
                   Each dict must have ``question_id`` and ``selected_option_ids``.
        pass_mark: Minimum score required to pass (0 = no pass threshold).

    Returns:
        :class:`GradingReport` with per-question breakdown.
    """
    # Build answer lookup: question_id → set of selected option ids
    answer_map: dict[str, set[str]] = {}
    for ans in answers:
        if not isinstance(ans, dict):
            continue
        qid = _normalize_answer_value(ans.get("question_id"))
        if not qid:
            continue
        ids = _extract_selected_option_ids(ans)
        answer_map[qid] = set(ids)

    total_marks = 0
    score = 0
    details: list[QuestionResult] = []

    for i, q in enumerate(questions, start=1):
        q_max = q.marks or 0
        total_marks += q_max
        q_type = (str(q.type.value) if hasattr(q.type, "value") else str(q.type)).lower()
        options: list[dict] = q.options or []
        correct_ids = _correct_ids(options)
        qid = _normalize_answer_value(getattr(q, "id", None)) or ""
        selected_ids = answer_map.get(qid, set())

        student_answer = next(iter(selected_ids), None) if len(selected_ids) <= 1 else sorted(selected_ids)
        correct_answer = next(iter(correct_ids), None) if len(correct_ids) <= 1 else sorted(correct_ids)
        print(
            f"Q{i}: student_answer={repr(student_answer)} | "
            f"correct_answer={repr(correct_answer)} | "
            f"match={student_answer == correct_answer}"
        )

        if not correct_ids:
            print(f"[grading-warning] No correct answer key found for question_id={qid}; marking wrong.")

        if q_type == "mcq":
            # MCQ: exactly one correct; award full marks if selected matches
            if len(selected_ids) == 1 and selected_ids == correct_ids:
                earned = q_max
            else:
                earned = 0
        elif q_type == "msq":
            # MSQ: partial credit per correct option selected, penalise wrong picks
            # Strategy: +1 per correct selected, -1 per wrong selected, floor 0
            n_correct = len(correct_ids)
            if n_correct == 0:
                earned = 0
            else:
                hits = len(selected_ids & correct_ids)
                misses = len(selected_ids - correct_ids)
                raw = hits - misses
                # Scale to question marks
                earned = max(0, round((raw / n_correct) * q_max))
        else:
            # Unknown / open-ended: skip auto-grade
            earned = 0

        score += earned
        details.append(
            QuestionResult(
                question_id=q.id,
                earned=earned,
                max_marks=q_max,
                correct=(earned == q_max),
            )
        )

    pass_fail = score >= pass_mark
    return GradingReport(score=score, total_marks=total_marks, pass_fail=pass_fail, details=details)