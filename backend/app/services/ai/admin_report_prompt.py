from __future__ import annotations

import json
from typing import Any


def build_admin_report_prompt(
    *,
    request_payload: dict[str, Any],
    analytics_context: dict[str, Any],
) -> str:
    # Direct, instruction-heavy prompt mirroring ai_content_generator.py style
    return f"""You are an expert educational data analyst.
Based on the provided data, generate a structured JSON report for administrators.

DATA CONTEXT:
{json.dumps(analytics_context, indent=2)}

REQUEST PARAMETERS:
{json.dumps(request_payload, indent=2)}

You MUST return a valid JSON object with these EXACT keys:
- "summary": A 1-sentence executive summary.
- "key_insights": A list of strings (max 2).
- "risk_flags": A list of strings (max 2).
- "recommendations": A list of objects {{"title", "action", "rationale", "priority"}} (exactly 2 items).
- "trend_highlights": A list of strings (exactly 1 item).
- "data_window": An object {{"scope": "...", "start_date": "...", "end_date": "..."}}
- "caveats": A list of strings (can be empty).

Return ONLY the JSON. No conversational text."""

