from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def sanitize_text(text: str, *, max_chars: int = 6000, max_lines: int = 120) -> str:
    if not text:
        return ""
    text = _EMAIL_RE.sub("[redacted-email]", text)
    lines = text.splitlines()
    sensitive_markers = (
        "student_selected_option_texts",
        "student_selected_option_ids",
        "correct_option_texts",
        "correct_option_ids",
        "raw_prompt_input",
        "\"prompt_payload\"",
        "prompt_payload",
    )
    safe_lines: list[str] = []
    for line in lines:
        if any(marker in line for marker in sensitive_markers):
            safe_lines.append("[redacted-sensitive-line]")
        else:
            safe_lines.append(line)
        if len(safe_lines) >= max_lines:
            break
    out = "\n".join(safe_lines)
    if len(out) > max_chars:
        out = out[:max_chars] + "\n[truncated]"
    return out

