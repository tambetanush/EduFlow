from __future__ import annotations

import json
from typing import Any


def build_student_explanation_prompt(
    *,
    prompt_payload: dict[str, Any],
) -> str:
    # Direct, instruction-heavy prompt mirroring ai_content_generator.py style
    return f"""You are a supportive assessment coach.
Explain why a student's answer was incorrect without giving away the final answer.

DATA CONTEXT:
{json.dumps(prompt_payload, indent=2)}

You MUST return a valid JSON object with these EXACT keys:
- "why_it_was_wrong": 1 sentence explaining the student's mistake.
- "correct_reasoning": 1 sentence explaining the logic behind the correct answer.
- "common_mistake": 1 sentence describing a common pitfall.
- "hint_for_retry": 1 sentence to help the student find the answer themselves.
- "confidence": A number between 0.0 and 1.0.
- "follow_up_questions": A list of strings (can be empty).

Return ONLY the JSON. No conversational text."""

