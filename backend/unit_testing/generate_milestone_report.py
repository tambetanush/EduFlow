"""
generate_milestone_report.py
────────────────────────────
Collects every test_*.py function under backend/unit_testing, runs pytest,
and produces pytest_milestone_report.md with:
  • A matrix table that shows each test's input (HTTP requests) and output
    (expected assertions → JSON, actual result → JSON) side by side.
  • Full code snippets for every test.
  • Raw pytest output appended at the bottom.

Input  JSON = HTTP calls found in the test body (method, url, body/params).
Output JSON = expected assertions derived from assert statements +
              actual result from pytest (status, failure detail if any).
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UNIT_TEST_DIR = ROOT / "unit_testing"
OUTPUT_FILE = UNIT_TEST_DIR / "pytest_milestone_report.md"


# ──────────────────────────────────────────────────────────────────────────────
# Data model
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class HttpCall:
    method: str
    url: str
    body: Any = None       # JSON body (dict) or None
    params: Any = None     # query-string params or None
    files: Any = None      # multipart files description or None


@dataclass
class AssertExpectation:
    raw: str               # original assert source text
    kind: str              # "status_code", "json_field", "json_key_exists",
    # "json_key_type", "general"
    expected: Any = None   # the expected value (for status_code / json_field)
    field_path: str = ""   # e.g. "payload['assessment']['avg_percentage']"


@dataclass
class TestCaseInfo:
    file_path: Path
    function_name: str
    lineno: int
    http_calls: list[HttpCall] = field(default_factory=list)
    expectations: list[AssertExpectation] = field(default_factory=list)
    # raw assert strings (legacy)
    asserts: list[str] = field(default_factory=list)
    snippet: str = ""
    status: str = "NOT_RUN"
    failure_detail: str = ""

    @property
    def node_id(self) -> str:
        rel = self.file_path.relative_to(ROOT).as_posix()
        return f"{rel}::{self.function_name}"


# ──────────────────────────────────────────────────────────────────────────────
# AST helpers – extract HTTP calls
# ──────────────────────────────────────────────────────────────────────────────

def _try_literal(node: ast.expr) -> Any:
    """Best-effort conversion of an AST node to a Python literal."""
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def _extract_http_calls(func_node: ast.FunctionDef, source: str) -> list[HttpCall]:
    """
    Walk the function body and find patterns like:
        client.get(url)
        client.post(url, json={...})
        client.patch(url, json={...})
        client.delete(url)
    """
    calls: list[HttpCall] = []
    http_methods = {"get", "post", "patch", "put", "delete"}

    for node in ast.walk(func_node):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        # Must be an attribute call: <something>.METHOD(...)
        if not isinstance(func, ast.Attribute):
            continue
        method_name = func.attr.lower()
        if method_name not in http_methods:
            continue

        # First positional arg is the URL
        url: str = ""
        if node.args:
            url_val = _try_literal(node.args[0])
            if url_val is None:
                # It might be an f-string or a variable – grab source segment
                seg = ast.get_source_segment(source, node.args[0])
                url = seg or "<dynamic>"
            else:
                url = str(url_val)

        body: Any = None
        params: Any = None
        files_desc: Any = None

        for kw in node.keywords:
            if kw.arg == "json":
                body = _try_literal(kw.value)
                if body is None:
                    seg = ast.get_source_segment(source, kw.value)
                    body = seg or "<dynamic>"
            elif kw.arg == "params":
                params = _try_literal(kw.value)
                if params is None:
                    seg = ast.get_source_segment(source, kw.value)
                    params = seg or "<dynamic>"
            elif kw.arg == "files":
                # Describe files loosely as a string
                seg = ast.get_source_segment(source, kw.value)
                files_desc = seg or "<multipart>"

        calls.append(HttpCall(
            method=method_name.upper(),
            url=url,
            body=body,
            params=params,
            files=files_desc,
        ))

    return calls


# ──────────────────────────────────────────────────────────────────────────────
# AST helpers – parse assert statements into structured expectations
# ──────────────────────────────────────────────────────────────────────────────

def _parse_assertion(assert_node: ast.Assert, source: str) -> AssertExpectation:
    """
    Classify a single assert into a structured expectation.

    Recognised patterns:
      assert  response.status_code == 200          → kind="status_code", expected=200
      assert  payload["key"] == "value"            → kind="json_field",   expected="value"
      assert  "key" in resp.json()                 → kind="json_key_exists"
      assert  isinstance(x, list)                  → kind="json_key_type"
      anything else                                → kind="general"
    """
    test_expr = assert_node.test
    raw = ast.get_source_segment(source, assert_node) or ""
    raw = " ".join(raw.split())

    # ── assert <lhs> == <rhs> ────────────────────────────────────────────────
    if isinstance(test_expr, ast.Compare):
        ops = test_expr.ops
        comparators = test_expr.comparators

        if len(ops) == 1 and isinstance(ops[0], ast.Eq) and len(comparators) == 1:
            lhs = test_expr.left
            rhs = comparators[0]

            lhs_src = ast.get_source_segment(source, lhs) or ""
            rhs_val = _try_literal(rhs)

            # status_code check
            if "status_code" in lhs_src:
                return AssertExpectation(raw=raw, kind="status_code",
                                         expected=rhs_val, field_path=lhs_src)

            # JSON field check
            rhs_src = ast.get_source_segment(source, rhs) or ""
            return AssertExpectation(raw=raw, kind="json_field",
                                     expected=rhs_val if rhs_val is not None else rhs_src,
                                     field_path=lhs_src)

        # assert len(x) >= N  or  x >= N
        cmp_ops = [type(o).__name__ for o in ops]
        if any(op in cmp_ops for op in ("GtE", "Gt", "LtE", "Lt")):
            lhs_src = ast.get_source_segment(source, test_expr.left) or ""
            rhs_src = ast.get_source_segment(source, comparators[-1]) or ""
            op_sym = {"GtE": ">=", "Gt": ">", "LtE": "<=",
                      "Lt": "<"}.get(cmp_ops[0], cmp_ops[0])
            return AssertExpectation(raw=raw, kind="json_field",
                                     expected=f"{lhs_src} {op_sym} {rhs_src}",
                                     field_path=lhs_src)

        # "key" in collection
        if len(ops) == 1 and isinstance(ops[0], ast.In):
            lhs_src = ast.get_source_segment(source, test_expr.left) or ""
            rhs_src = ast.get_source_segment(source, comparators[0]) or ""
            return AssertExpectation(raw=raw, kind="json_key_exists",
                                     field_path=lhs_src,
                                     expected=f"{lhs_src} in {rhs_src}")

    # ── assert isinstance(x, TYPE) ───────────────────────────────────────────
    if (isinstance(test_expr, ast.Call)
            and isinstance(test_expr.func, ast.Name)
            and test_expr.func.id == "isinstance"):
        if len(test_expr.args) >= 2:
            obj_src = ast.get_source_segment(source, test_expr.args[0]) or ""
            typ_src = ast.get_source_segment(source, test_expr.args[1]) or ""
            return AssertExpectation(raw=raw, kind="json_key_type",
                                     field_path=obj_src,
                                     expected=f"isinstance({obj_src}, {typ_src})")

    # ── generic ───────────────────────────────────────────────────────────────
    return AssertExpectation(raw=raw, kind="general", expected=raw)


def _parse_assertions(func_node: ast.FunctionDef, source: str) -> list[AssertExpectation]:
    expectations = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Assert):
            expectations.append(_parse_assertion(node, source))
    return expectations


# ──────────────────────────────────────────────────────────────────────────────
# Collect tests
# ──────────────────────────────────────────────────────────────────────────────

def collect_tests() -> list[TestCaseInfo]:
    tests: list[TestCaseInfo] = []
    for file_path in sorted(UNIT_TEST_DIR.glob("test_*.py")):
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source)
        lines = source.splitlines()

        for node in tree.body:
            if not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")):
                continue

            http_calls = _extract_http_calls(node, source)
            expectations = _parse_assertions(node, source)

            # Legacy raw assert strings (kept for compatibility)
            raw_asserts: list[str] = []
            for inner in ast.walk(node):
                if isinstance(inner, ast.Assert):
                    seg = ast.get_source_segment(source, inner)
                    if seg:
                        raw_asserts.append(" ".join(seg.split()))

            start = max(node.lineno - 1, 0)
            end = min((getattr(node, "end_lineno", node.lineno)
                      or node.lineno), len(lines))
            snippet_lines = lines[start:end]
            if len(snippet_lines) > 50:
                snippet_lines = snippet_lines[:50] + ["    ..."]

            tests.append(TestCaseInfo(
                file_path=file_path,
                function_name=node.name,
                lineno=node.lineno,
                http_calls=http_calls,
                expectations=expectations,
                asserts=raw_asserts,
                snippet="\n".join(snippet_lines),
            ))
    return tests


# ──────────────────────────────────────────────────────────────────────────────
# Run pytest
# ──────────────────────────────────────────────────────────────────────────────

def run_pytest() -> tuple[dict[str, str], dict[str, str], str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    env["DATABASE_URL"] = "sqlite+aiosqlite:///./eduflow_milestone_report.db"

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "unit_testing",
        "-vv",
        "--maxfail=0",
        "--tb=short",
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    output = (proc.stdout or "") + "\n" + (proc.stderr or "")

    status_map: dict[str, str] = {}
    line_pattern = re.compile(
        r"^(unit_testing[/\\][^:\n]+::test[^\s]+)\s+(PASSED|FAILED|ERROR|SKIPPED)(?:\s+\[[^\]]+\])?$",
        re.MULTILINE,
    )
    for node_id, status in line_pattern.findall(output):
        normalized = node_id.replace("\\", "/")
        status_map[normalized] = status

    failure_map: dict[str, str] = {}
    failure_header = re.compile(r"_{3,}\s*(test_[A-Za-z0-9_]+)\s*_{3,}")
    lines = output.splitlines()
    for idx, line in enumerate(lines):
        m = failure_header.search(line)
        if not m:
            continue
        fn_name = m.group(1)
        detail = ""
        for j in range(idx + 1, min(idx + 25, len(lines))):
            candidate = lines[j].strip()
            if not candidate:
                continue
            if candidate.startswith("E   ") or "AssertionError" in candidate or "HTTPException" in candidate:
                detail = candidate
                break
        if not detail:
            detail = "Failed (see pytest output section)."
        failure_map[fn_name] = detail

    return status_map, failure_map, output


# ──────────────────────────────────────────────────────────────────────────────
# Build JSON representations for report
# ──────────────────────────────────────────────────────────────────────────────

def _build_input_json(test: TestCaseInfo) -> dict:
    """
    Represent the HTTP calls made by the test as a structured dict.
    """
    if not test.http_calls:
        return {"note": "No HTTP calls detected (fixture-only or setup test)"}

    calls = []
    for call in test.http_calls:
        entry: dict[str, Any] = {
            "method": call.method,
            "url": call.url,
        }
        if call.body is not None:
            entry["body"] = call.body
        if call.params is not None:
            entry["params"] = call.params
        if call.files is not None:
            entry["files"] = call.files
        calls.append(entry)

    return {"http_calls": calls}


def _build_expected_json(test: TestCaseInfo) -> dict:
    """
    Represent the assertions as a structured expected-output dict.
    Groups by assertion kind.
    """
    status_codes: list[Any] = []
    field_checks: list[dict] = []
    key_exists: list[str] = []
    type_checks: list[str] = []
    general: list[str] = []

    for exp in test.expectations:
        if exp.kind == "status_code":
            status_codes.append(exp.expected)
        elif exp.kind == "json_field":
            field_checks.append({
                "field": exp.field_path.strip(),
                "expected_value": exp.expected,
            })
        elif exp.kind == "json_key_exists":
            key_exists.append(str(exp.expected))
        elif exp.kind == "json_key_type":
            type_checks.append(str(exp.expected))
        else:
            general.append(str(exp.expected))

    result: dict[str, Any] = {}
    if status_codes:
        # Deduplicate while preserving order
        seen: list = []
        for s in status_codes:
            if s not in seen:
                seen.append(s)
        result["expected_status_codes"] = seen if len(seen) > 1 else seen[0]
    if field_checks:
        result["expected_json_fields"] = field_checks
    if key_exists:
        result["expected_keys_present"] = key_exists
    if type_checks:
        result["expected_type_checks"] = type_checks
    if general:
        result["other_assertions"] = general
    if not result:
        result["note"] = "No explicit assertions; expected to pass without exception."

    return result


def _build_actual_json(test: TestCaseInfo) -> dict:
    """
    Represent the actual pytest result as a structured dict.
    """
    result: dict[str, Any] = {"pytest_result": test.status}

    if test.status == "PASSED":
        result["detail"] = "All assertions passed."
    elif test.status in {"FAILED", "ERROR"}:
        result["failure_detail"] = test.failure_detail or "See raw pytest output for details."
    elif test.status == "SKIPPED":
        result["detail"] = "Test was skipped."
    else:
        result["detail"] = "Test was not captured by pytest output parser."

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Markdown helpers
# ──────────────────────────────────────────────────────────────────────────────

def _md_escape(value: str) -> str:
    return value.replace("|", "\\|")


def _json_code_block(obj: Any) -> str:
    """Return a fenced JSON code block (single-line for table cells, collapsed)."""
    return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"


def _inline_json(obj: Any) -> str:
    """
    For embedding inside a Markdown table cell we must avoid newlines.
    We use a <details> fold.
    """
    pretty = json.dumps(obj, indent=2, ensure_ascii=False)
    # Escape pipe characters inside the JSON
    pretty = pretty.replace("|", "\\|")
    # Replace newlines with <br> for table cell rendering
    one_line = pretty.replace("\n", "<br>").replace("  ", "&nbsp;&nbsp;")
    return one_line


# ──────────────────────────────────────────────────────────────────────────────
# Build the full markdown report
# ──────────────────────────────────────────────────────────────────────────────

def build_report(tests: list[TestCaseInfo], raw_output: str) -> str:
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    passed = sum(1 for t in tests if t.status == "PASSED")
    failed = sum(1 for t in tests if t.status in {"FAILED", "ERROR"})
    skipped = sum(1 for t in tests if t.status == "SKIPPED")
    not_run = sum(1 for t in tests if t.status == "NOT_RUN")

    parts: list[str] = []

    # ── Header ───────────────────────────────────────────────────────────────
    parts.append("# Pytest Milestone Report")
    parts.append("")
    parts.append(f"- Generated at: `{generated}`")
    parts.append("- Test scope: `backend/unit_testing/test_*.py`")
    parts.append(
        f"- Summary: **Passed={passed}**, **Failed/Error={failed}**, "
        f"**Skipped={skipped}**, **Not captured={not_run}**"
    )
    parts.append("")

    # ── Summary table (overview) ──────────────────────────────────────────────
    parts.append("## Test Case Overview")
    parts.append("")
    parts.append("| # | Test Case | File | Status |")
    parts.append("|---|---|---|---|")
    for i, test in enumerate(tests, 1):
        status_icon = {
            "PASSED": "✅ PASSED",
            "FAILED": "❌ FAILED",
            "ERROR": "🔥 ERROR",
            "SKIPPED": "⏭ SKIPPED",
        }.get(test.status, "⬜ NOT_RUN")
        ref = f"`{test.file_path.name}:{test.lineno}`"
        case_label = f"`{test.function_name}`"
        parts.append(f"| {i} | {case_label} | {ref} | {status_icon} |")
    parts.append("")

    # ── Detailed per-test sections ────────────────────────────────────────────
    parts.append(
        "## Detailed Test Cases (Input / Expected Output / Actual Output)")
    parts.append("")
    parts.append(
        "> Each test section shows:\n"
        "> - **Input JSON** – HTTP requests extracted from the test body\n"
        "> - **Expected Output JSON** – assertions parsed from the test code\n"
        "> - **Actual Output JSON** – pytest result with pass/fail details\n"
        "> - **Code Snippet** – first ~50 lines of the test function"
    )
    parts.append("")

    for i, test in enumerate(tests, 1):
        input_json = _build_input_json(test)
        expected_json = _build_expected_json(test)
        actual_json = _build_actual_json(test)

        status_badge = {
            "PASSED": "✅ PASSED",
            "FAILED": "❌ FAILED",
            "ERROR": "🔥 ERROR",
            "SKIPPED": "⏭ SKIPPED",
        }.get(test.status, "⬜ NOT_RUN")

        parts.append(f"### {i}. `{test.function_name}` — {status_badge}")
        parts.append("")
        parts.append(
            f"- **Source:** `{test.file_path.relative_to(ROOT).as_posix()}:{test.lineno}`"
        )
        parts.append(f"- **Node ID:** `{test.node_id}`")
        if test.failure_detail:
            parts.append(f"- **Failure:** `{_md_escape(test.failure_detail)}`")
        parts.append("")

        # Three columns: Input | Expected | Actual
        parts.append("#### Input JSON (HTTP Requests)")
        parts.append("")
        parts.append(_json_code_block(input_json))
        parts.append("")

        parts.append("#### Expected Output JSON (Assertions)")
        parts.append("")
        parts.append(_json_code_block(expected_json))
        parts.append("")

        parts.append("#### Actual Output JSON (Pytest Result)")
        parts.append("")
        parts.append(_json_code_block(actual_json))
        parts.append("")

        parts.append("#### Code Snippet")
        parts.append("")
        parts.append("```python")
        parts.append(test.snippet)
        parts.append("```")
        parts.append("")
        parts.append("---")
        parts.append("")

    # ── Raw pytest output ─────────────────────────────────────────────────────
    parts.append("## Raw Pytest Output")
    parts.append("")
    parts.append("```text")
    parts.append(raw_output.strip())
    parts.append("```")
    parts.append("")

    return "\n".join(parts)


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("Collecting tests …")
    tests = collect_tests()
    print(f"  Found {len(tests)} test functions.")

    print("Running pytest …")
    status_map, failure_map, raw_output = run_pytest()

    for test in tests:
        key = test.node_id.replace("\\", "/")
        test.status = status_map.get(key, "NOT_RUN")
        test.failure_detail = failure_map.get(test.function_name, "")

    passed = sum(1 for t in tests if t.status == "PASSED")
    failed = sum(1 for t in tests if t.status in {"FAILED", "ERROR"})
    print(f"  Results: {passed} passed, {failed} failed/error.")

    print("Building report …")
    report = build_report(tests, raw_output)
    OUTPUT_FILE.write_text(report, encoding="utf-8")
    print(f"Report generated: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
