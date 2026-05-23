# Pytest Milestone Report

- Generated at: `2026-04-10 12:45:45`
- Test scope: `backend/unit_testing/test_*.py`
- Summary: **Passed=72**, **Failed/Error=0**, **Skipped=0**, **Not captured=0**

## Test Case Overview

| # | Test Case | File | Status |
|---|---|---|---|
| 1 | `test_educator_dashboard_stats` | `test_educator.py:239` | ✅ PASSED |
| 2 | `test_educator_workshop_list_is_scoped` | `test_educator.py:250` | ✅ PASSED |
| 3 | `test_educator_can_view_assessments_and_submissions` | `test_educator.py:261` | ✅ PASSED |
| 4 | `test_educator_cannot_read_assessments_or_submissions_other_institution` | `test_educator.py:274` | ✅ PASSED |
| 5 | `test_educator_material_upload_and_delete` | `test_educator.py:285` | ✅ PASSED |
| 6 | `test_educator_can_fetch_workshop_analytics` | `test_educator.py:308` | ✅ PASSED |
| 7 | `test_educator_notifications_success` | `test_educator.py:320` | ✅ PASSED |
| 8 | `test_educator_can_view_review_and_dispatch_parent_message` | `test_educator.py:329` | ✅ PASSED |
| 9 | `test_educator_can_grade_pending_submission` | `test_educator.py:362` | ✅ PASSED |
| 10 | `test_educator_workshop_educator_profile_contract` | `test_educator.py:376` | ✅ PASSED |
| 11 | `test_educator_certificate_recommend_and_download` | `test_educator.py:390` | ✅ PASSED |
| 12 | `test_educator_performance_export_available` | `test_educator.py:406` | ✅ PASSED |
| 13 | `test_educator_forbidden_admin_and_delete_routes` | `test_educator.py:417` | ✅ PASSED |
| 14 | `test_educator_forbidden_from_salary_routes` | `test_educator.py:428` | ✅ PASSED |
| 15 | `test_educator_cannot_approve_requests` | `test_educator.py:442` | ✅ PASSED |
| 16 | `test_educator_cannot_access_admin_insights` | `test_educator.py:453` | ✅ PASSED |
| 17 | `test_educator_rejects_non_owned_enrollment_queries` | `test_educator.py:461` | ✅ PASSED |
| 18 | `test_educator_grading_unknown_submission_returns_not_found` | `test_educator.py:469` | ✅ PASSED |
| 19 | `test_educator_notification_collection_forbidden_for_other_user` | `test_educator.py:477` | ✅ PASSED |
| 20 | `test_genai_admin_report_success` | `test_genai_features.py:233` | ✅ PASSED |
| 21 | `test_genai_admin_report_forbidden_for_student` | `test_genai_features.py:243` | ✅ PASSED |
| 22 | `test_genai_admin_report_cross_institution_blocked_for_institution_admin` | `test_genai_features.py:251` | ✅ PASSED |
| 23 | `test_genai_admin_report_result_roundtrip` | `test_genai_features.py:259` | ✅ PASSED |
| 24 | `test_genai_student_explanation_success` | `test_genai_features.py:276` | ✅ PASSED |
| 25 | `test_genai_student_explanation_forbidden_for_educator` | `test_genai_features.py:289` | ✅ PASSED |
| 26 | `test_genai_student_explanation_requires_ownership` | `test_genai_features.py:300` | ✅ PASSED |
| 27 | `test_genai_persists_generation_metadata` | `test_genai_features.py:311` | ✅ PASSED |
| 28 | `test_institution_admin_dashboard_stats` | `test_institutional_admin.py:202` | ✅ PASSED |
| 29 | `test_institution_admin_workshop_scope_and_create` | `test_institutional_admin.py:213` | ✅ PASSED |
| 30 | `test_institution_admin_cannot_update_other_institution_workshop` | `test_institutional_admin.py:231` | ✅ PASSED |
| 31 | `test_institution_admin_users_list_is_scoped` | `test_institutional_admin.py:239` | ✅ PASSED |
| 32 | `test_institution_admin_can_fetch_student_enrollments` | `test_institutional_admin.py:249` | ✅ PASSED |
| 33 | `test_institution_admin_can_create_approval_request` | `test_institutional_admin.py:258` | ✅ PASSED |
| 34 | `test_institution_admin_dashboard_aggregate_and_leaderboards` | `test_institutional_admin.py:270` | ✅ PASSED |
| 35 | `test_institution_admin_student_roster_and_attendance_report` | `test_institutional_admin.py:298` | ✅ PASSED |
| 36 | `test_institution_admin_parent_message_dispatch` | `test_institutional_admin.py:315` | ✅ PASSED |
| 37 | `test_institution_admin_bulk_and_export_endpoints` | `test_institutional_admin.py:331` | ✅ PASSED |
| 38 | `test_institution_admin_parent_contact_lookup` | `test_institutional_admin.py:361` | ✅ PASSED |
| 39 | `test_institution_admin_profile_metadata_update_self_only` | `test_institutional_admin.py:373` | ✅ PASSED |
| 40 | `test_institution_admin_cannot_access_platform_admin_dashboard` | `test_institutional_admin.py:400` | ✅ PASSED |
| 41 | `test_institution_admin_cannot_approve_requests` | `test_institutional_admin.py:408` | ✅ PASSED |
| 42 | `test_institution_admin_dashboard_export_available` | `test_institutional_admin.py:416` | ✅ PASSED |
| 43 | `test_institution_admin_cannot_read_other_student_enrollments` | `test_institutional_admin.py:425` | ✅ PASSED |
| 44 | `test_institution_admin_workshop_patch_own_workshop` | `test_institutional_admin.py:434` | ✅ PASSED |
| 45 | `test_institution_admin_cannot_process_salary` | `test_institutional_admin.py:443` | ✅ PASSED |
| 46 | `test_admin_dashboard_stats_success` | `test_platform_admin.py:178` | ✅ PASSED |
| 47 | `test_admin_dashboard_forbidden_for_non_admin` | `test_platform_admin.py:190` | ✅ PASSED |
| 48 | `test_admin_workshop_crud` | `test_platform_admin.py:198` | ✅ PASSED |
| 49 | `test_admin_approval_list_and_approve` | `test_platform_admin.py:221` | ✅ PASSED |
| 50 | `test_admin_salary_pay_and_list` | `test_platform_admin.py:235` | ✅ PASSED |
| 51 | `test_admin_users_and_institutions_endpoints` | `test_platform_admin.py:251` | ✅ PASSED |
| 52 | `test_admin_new_analytics_endpoints` | `test_platform_admin.py:264` | ✅ PASSED |
| 53 | `test_admin_parent_communication_dispatch` | `test_platform_admin.py:308` | ✅ PASSED |
| 54 | `test_admin_can_read_approval_request_details` | `test_platform_admin.py:326` | ✅ PASSED |
| 55 | `test_admin_approving_unknown_request_returns_not_found` | `test_platform_admin.py:334` | ✅ PASSED |
| 56 | `test_admin_can_fetch_submission_review` | `test_platform_admin.py:342` | ✅ PASSED |
| 57 | `test_admin_can_export_performance_report` | `test_platform_admin.py:351` | ✅ PASSED |
| 58 | `test_platform_admin_endpoints_forbidden_for_student` | `test_platform_admin.py:360` | ✅ PASSED |
| 59 | `test_admin_workshop_create_validation_error` | `test_platform_admin.py:369` | ✅ PASSED |
| 60 | `test_student_auth_register_and_login` | `test_student.py:177` | ✅ PASSED |
| 61 | `test_student_dashboard_and_analytics` | `test_student.py:196` | ✅ PASSED |
| 62 | `test_student_workshops_and_enrollments` | `test_student.py:218` | ✅ PASSED |
| 63 | `test_student_attempt_start_save_submit_flow` | `test_student.py:235` | ✅ PASSED |
| 64 | `test_student_certificates_notifications_and_profile` | `test_student.py:267` | ✅ PASSED |
| 65 | `test_student_forbidden_from_other_student_data` | `test_student.py:319` | ✅ PASSED |
| 66 | `test_student_leaderboard_access_and_staff_only_guards` | `test_student.py:339` | ✅ PASSED |
| 67 | `test_student_cannot_access_admin_or_institution_dashboards` | `test_student.py:396` | ✅ PASSED |
| 68 | `test_student_cannot_view_educator_dashboard` | `test_student.py:405` | ✅ PASSED |
| 69 | `test_student_invalid_certificate_verification_code` | `test_student.py:413` | ✅ PASSED |
| 70 | `test_student_cannot_delete_workshop` | `test_student.py:421` | ✅ PASSED |
| 71 | `test_student_cannot_grade_submission` | `test_student.py:429` | ✅ PASSED |
| 72 | `test_student_assessment_submit_unknown_submission` | `test_student.py:437` | ✅ PASSED |

## Detailed Test Cases (Input / Expected Output / Actual Output)

> Each test section shows:
> - **Input JSON** – HTTP requests extracted from the test body
> - **Expected Output JSON** – assertions parsed from the test code
> - **Actual Output JSON** – pytest result with pass/fail details
> - **Code Snippet** – first ~50 lines of the test function

### 1. `test_educator_dashboard_stats` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:239`
- **Node ID:** `unit_testing/test_educator.py::test_educator_dashboard_stats`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/educator"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"assigned_workshops\"]",
      "expected_value": "payload[\"assigned_workshops\"] >= 1"
    },
    {
      "field": "payload[\"active_assessments\"]",
      "expected_value": "payload[\"active_assessments\"] >= 1"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_dashboard_stats(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assigned_workshops"] >= 1
    assert payload["active_assessments"] >= 1
```

---

### 2. `test_educator_workshop_list_is_scoped` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:250`
- **Node ID:** `unit_testing/test_educator.py::test_educator_workshop_list_is_scoped`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/workshops/"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_keys_present": [
    "\"workshop-own\" in ids"
  ],
  "other_assertions": [
    "assert \"workshop-other\" not in ids"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_workshop_list_is_scoped(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/workshops/")
    assert response.status_code == 200
    ids = {item["id"] for item in response.json()["items"]}
    assert "workshop-own" in ids
    assert "workshop-other" not in ids
```

---

### 3. `test_educator_can_view_assessments_and_submissions` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:261`
- **Node ID:** `unit_testing/test_educator.py::test_educator_can_view_assessments_and_submissions`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/assessments/workshop/workshop-own"
    },
    {
      "method": "GET",
      "url": "/api/v1/submissions/assessment/assessment-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "assessments_response.json()[\"total\"]",
      "expected_value": "assessments_response.json()[\"total\"] >= 1"
    },
    {
      "field": "submissions_response.json()[\"total\"]",
      "expected_value": "submissions_response.json()[\"total\"] >= 1"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_can_view_assessments_and_submissions(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    assessments_response = client.get("/api/v1/assessments/workshop/workshop-own")
    assert assessments_response.status_code == 200
    assert assessments_response.json()["total"] >= 1

    submissions_response = client.get("/api/v1/submissions/assessment/assessment-1")
    assert submissions_response.status_code == 200
    assert submissions_response.json()["total"] >= 1
```

---

### 4. `test_educator_cannot_read_assessments_or_submissions_other_institution` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:274`
- **Node ID:** `unit_testing/test_educator.py::test_educator_cannot_read_assessments_or_submissions_other_institution`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/assessments/workshop/workshop-other"
    },
    {
      "method": "GET",
      "url": "/api/v1/assessments/module/module-other"
    },
    {
      "method": "GET",
      "url": "/api/v1/assessments/assessment-other"
    },
    {
      "method": "GET",
      "url": "/api/v1/submissions/assessment/assessment-other"
    },
    {
      "method": "GET",
      "url": "/api/v1/submissions/submission-other-graded/review"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_cannot_read_assessments_or_submissions_other_institution(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    assert client.get("/api/v1/assessments/workshop/workshop-other").status_code == 403
    assert client.get("/api/v1/assessments/module/module-other").status_code == 403
    assert client.get("/api/v1/assessments/assessment-other").status_code == 403
    assert client.get("/api/v1/submissions/assessment/assessment-other").status_code == 403
    assert client.get("/api/v1/submissions/submission-other-graded/review").status_code == 403
```

---

### 5. `test_educator_material_upload_and_delete` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:285`
- **Node ID:** `unit_testing/test_educator.py::test_educator_material_upload_and_delete`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/modules/module-1/materials/upload",
      "files": "{\"file\": (\"lecture-notes.txt\", b\"hello materials\", \"text/plain\")}"
    },
    {
      "method": "GET",
      "url": "f\"/api/v1/materials/module-1/{uploaded['id']}/download\""
    },
    {
      "method": "DELETE",
      "url": "f\"/api/v1/materials/module-1/{uploaded['id']}\""
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_keys_present": [
    "\"/media/modules/module-1/\" in download_response.json()[\"download_url\"]"
  ],
  "other_assertions": [
    "assert uploaded is not None",
    "assert uploaded[\"id\"] not in remaining_ids"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_material_upload_and_delete(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    upload_response = client.post(
        "/api/v1/modules/module-1/materials/upload",
        files={"file": ("lecture-notes.txt", b"hello materials", "text/plain")},
    )
    assert upload_response.status_code == 200
    materials = upload_response.json()["materials"]
    uploaded = next((item for item in materials if item["title"] == "lecture-notes.txt"), None)
    assert uploaded is not None

    download_response = client.get(f"/api/v1/materials/module-1/{uploaded['id']}/download")
    assert download_response.status_code == 200
    assert "/media/modules/module-1/" in download_response.json()["download_url"]

    delete_response = client.delete(f"/api/v1/materials/module-1/{uploaded['id']}")
    assert delete_response.status_code == 200
    remaining_ids = {item["id"] for item in delete_response.json()["materials"]}
    assert uploaded["id"] not in remaining_ids
```

---

### 6. `test_educator_can_fetch_workshop_analytics` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:308`
- **Node ID:** `unit_testing/test_educator.py::test_educator_can_fetch_workshop_analytics`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/workshop/workshop-own"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"workshop_id\"]",
      "expected_value": "workshop-own"
    }
  ],
  "expected_keys_present": [
    "\"assessment\" in payload",
    "\"pass_rate_percentage\" in payload[\"assessment\"]"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_can_fetch_workshop_analytics(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/workshop/workshop-own")
    assert response.status_code == 200
    payload = response.json()
    assert payload["workshop_id"] == "workshop-own"
    assert "assessment" in payload
    assert "pass_rate_percentage" in payload["assessment"]
```

---

### 7. `test_educator_notifications_success` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:320`
- **Node ID:** `unit_testing/test_educator.py::test_educator_notifications_success`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/notifications/educator-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "response.json()[\"total\"]",
      "expected_value": "response.json()[\"total\"] >= 1"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_notifications_success(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/notifications/educator-1")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
```

---

### 8. `test_educator_can_view_review_and_dispatch_parent_message` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:329`
- **Node ID:** `unit_testing/test_educator.py::test_educator_can_view_review_and_dispatch_parent_message`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/submissions/submission-graded/review"
    },
    {
      "method": "POST",
      "url": "/api/v1/communication/parent-email",
      "body": {
        "student_ids": [
          "student-1"
        ],
        "subject": "Submission Reviewed",
        "body": "Please check updated breakdown."
      }
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/assessment/assessment-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/workshop/workshop-own/student/student-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "review_payload[\"submission_id\"]",
      "expected_value": "submission-graded"
    },
    {
      "field": "len(review_payload[\"questions\"])",
      "expected_value": "len(review_payload[\"questions\"]) >= 1"
    },
    {
      "field": "message.json()[\"accepted\"]",
      "expected_value": 1
    },
    {
      "field": "assessment_drilldown.json()[\"student_id\"]",
      "expected_value": "student-1"
    },
    {
      "field": "workshop_drilldown.json()[\"context_id\"]",
      "expected_value": "workshop-own"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_can_view_review_and_dispatch_parent_message(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    review = client.get("/api/v1/submissions/submission-graded/review")
    assert review.status_code == 200
    review_payload = review.json()
    assert review_payload["submission_id"] == "submission-graded"
    assert len(review_payload["questions"]) >= 1

    message = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["student-1"],
            "subject": "Submission Reviewed",
            "body": "Please check updated breakdown.",
        },
    )
    assert message.status_code == 200
    assert message.json()["accepted"] == 1

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200

    assessment_drilldown = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["student_id"] == "student-1"

    workshop_drilldown = client.get("/api/v1/analytics/leaderboard/workshop/workshop-own/student/student-1")
    assert workshop_drilldown.status_code == 200
    assert workshop_drilldown.json()["context_id"] == "workshop-own"
```

---

### 9. `test_educator_can_grade_pending_submission` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:362`
- **Node ID:** `unit_testing/test_educator.py::test_educator_can_grade_pending_submission`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/submissions/submission-1/grade"
    },
    {
      "method": "POST",
      "url": "/api/v1/submissions/submission-1/grade"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    200,
    409
  ],
  "expected_json_fields": [
    {
      "field": "payload[\"id\"]",
      "expected_value": "submission-1"
    }
  ],
  "other_assertions": [
    "assert payload[\"pass_fail\"] is False"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_can_grade_pending_submission(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.post("/api/v1/submissions/submission-1/grade")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == "submission-1"
    assert payload["pass_fail"] is False

    repeat = client.post("/api/v1/submissions/submission-1/grade")
    assert repeat.status_code == 409
```

---

### 10. `test_educator_workshop_educator_profile_contract` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:376`
- **Node ID:** `unit_testing/test_educator.py::test_educator_workshop_educator_profile_contract`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/workshops/workshop-own/educator-profile"
    },
    {
      "method": "GET",
      "url": "/api/v1/workshops/workshop-other/educator-profile"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    200,
    403
  ],
  "expected_json_fields": [
    {
      "field": "payload[\"workshop_id\"]",
      "expected_value": "workshop-own"
    },
    {
      "field": "payload[\"email\"]",
      "expected_value": "educator@eduflow.edu"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_workshop_educator_profile_contract(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    own_profile = client.get("/api/v1/workshops/workshop-own/educator-profile")
    assert own_profile.status_code == 200
    payload = own_profile.json()
    assert payload["workshop_id"] == "workshop-own"
    assert payload["email"] == "educator@eduflow.edu"

    cross_institution = client.get("/api/v1/workshops/workshop-other/educator-profile")
    assert cross_institution.status_code == 403
```

---

### 11. `test_educator_certificate_recommend_and_download` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:390`
- **Node ID:** `unit_testing/test_educator.py::test_educator_certificate_recommend_and_download`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/certificates/recommend",
      "body": {
        "student_id": "student-1",
        "workshop_id": "workshop-own",
        "note": "Ready for certificate."
      }
    },
    {
      "method": "GET",
      "url": "/api/v1/certificates/certificate-1/download"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "recommend.json()[\"accepted\"]",
      "expected_value": "recommend.json()[\"accepted\"] >= 1"
    }
  ],
  "expected_keys_present": [
    "\"/media/certificates/certificate-1.pdf\" in download.json()[\"download_url\"]"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_certificate_recommend_and_download(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    recommend = client.post(
        "/api/v1/certificates/recommend",
        json={"student_id": "student-1", "workshop_id": "workshop-own", "note": "Ready for certificate."},
    )
    assert recommend.status_code == 200
    assert recommend.json()["accepted"] >= 1

    download = client.get("/api/v1/certificates/certificate-1/download")
    assert download.status_code == 200
    assert "/media/certificates/certificate-1.pdf" in download.json()["download_url"]
```

---

### 12. `test_educator_performance_export_available` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:406`
- **Node ID:** `unit_testing/test_educator.py::test_educator_performance_export_available`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/reports/performance/export"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"file_type\"]",
      "expected_value": "csv"
    }
  ],
  "expected_keys_present": [
    "\"/media/exports/\" in payload[\"download_url\"]"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_performance_export_available(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/reports/performance/export")
    assert response.status_code == 200
    payload = response.json()
    assert payload["file_type"] == "csv"
    assert "/media/exports/" in payload["download_url"]
```

---

### 13. `test_educator_forbidden_admin_and_delete_routes` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:417`
- **Node ID:** `unit_testing/test_educator.py::test_educator_forbidden_admin_and_delete_routes`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/admin"
    },
    {
      "method": "DELETE",
      "url": "/api/v1/workshops/workshop-own"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_forbidden_admin_and_delete_routes(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    admin_dashboard = client.get("/api/v1/dashboard/admin")
    assert admin_dashboard.status_code == 403

    delete_workshop = client.delete("/api/v1/workshops/workshop-own")
    assert delete_workshop.status_code == 403
```

---

### 14. `test_educator_forbidden_from_salary_routes` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:428`
- **Node ID:** `unit_testing/test_educator.py::test_educator_forbidden_from_salary_routes`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/salaries/pay",
      "body": {
        "educator_id": "educator-1",
        "month": "2026-04",
        "amount": 55000
      }
    },
    {
      "method": "GET",
      "url": "/api/v1/salaries/?month=2026-04"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_forbidden_from_salary_routes(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    pay = client.post(
        "/api/v1/salaries/pay",
        json={"educator_id": "educator-1", "month": "2026-04", "amount": 55000},
    )
    assert pay.status_code == 403

    listing = client.get("/api/v1/salaries/?month=2026-04")
    assert listing.status_code == 403
```

---

### 15. `test_educator_cannot_approve_requests` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:442`
- **Node ID:** `unit_testing/test_educator.py::test_educator_cannot_approve_requests`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/approvals/requests"
    },
    {
      "method": "POST",
      "url": "/api/v1/approvals/requests/approval-1/approve"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_cannot_approve_requests(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    list_response = client.get("/api/v1/approvals/requests")
    assert list_response.status_code == 403

    approve_response = client.post("/api/v1/approvals/requests/approval-1/approve")
    assert approve_response.status_code == 403
```

---

### 16. `test_educator_cannot_access_admin_insights` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:453`
- **Node ID:** `unit_testing/test_educator.py::test_educator_cannot_access_admin_insights`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/admin/insights"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_cannot_access_admin_insights(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/analytics/admin/insights")
    assert response.status_code == 403
```

---

### 17. `test_educator_rejects_non_owned_enrollment_queries` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:461`
- **Node ID:** `unit_testing/test_educator.py::test_educator_rejects_non_owned_enrollment_queries`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/enrollments/student/student-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_rejects_non_owned_enrollment_queries(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    own_enrollments = client.get("/api/v1/enrollments/student/student-1")
    assert own_enrollments.status_code == 200
```

---

### 18. `test_educator_grading_unknown_submission_returns_not_found` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:469`
- **Node ID:** `unit_testing/test_educator.py::test_educator_grading_unknown_submission_returns_not_found`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/submissions/submission-missing/grade"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 404
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_grading_unknown_submission_returns_not_found(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.post("/api/v1/submissions/submission-missing/grade")
    assert response.status_code == 404
```

---

### 19. `test_educator_notification_collection_forbidden_for_other_user` — ✅ PASSED

- **Source:** `unit_testing/test_educator.py:477`
- **Node ID:** `unit_testing/test_educator.py::test_educator_notification_collection_forbidden_for_other_user`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/notifications/student-1"
    },
    {
      "method": "GET",
      "url": "items"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_type_checks": [
    "isinstance(response.json().get(\"items\"), list)"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_educator_notification_collection_forbidden_for_other_user(client_and_state):
    client, state = client_and_state
    state["user_id"] = "educator-1"

    response = client.get("/api/v1/notifications/student-1")
    assert response.status_code == 200
    assert isinstance(response.json().get("items"), list)
```

---

### 20. `test_genai_admin_report_success` — ✅ PASSED

- **Source:** `unit_testing/test_genai_features.py:233`
- **Node ID:** `unit_testing/test_genai_features.py::test_genai_admin_report_success`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/ai/reports/",
      "body": {
        "institution_id": "inst-1"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "response.json()[\"status\"]",
      "expected_value": "completed"
    },
    {
      "field": "report_gemini.calls",
      "expected_value": 1
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_genai_admin_report_success(genai_client_and_state):
    client, state, report_gemini, _, _ = genai_client_and_state
    state["user_id"] = "admin-1"

    response = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1"})
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert report_gemini.calls == 1
```

---

### 21. `test_genai_admin_report_forbidden_for_student` — ✅ PASSED

- **Source:** `unit_testing/test_genai_features.py:243`
- **Node ID:** `unit_testing/test_genai_features.py::test_genai_admin_report_forbidden_for_student`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/ai/reports/",
      "body": {
        "institution_id": "inst-1"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_genai_admin_report_forbidden_for_student(genai_client_and_state):
    client, state, *_ = genai_client_and_state
    state["user_id"] = "student-1"

    response = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1"})
    assert response.status_code == 403
```

---

### 22. `test_genai_admin_report_cross_institution_blocked_for_institution_admin` — ✅ PASSED

- **Source:** `unit_testing/test_genai_features.py:251`
- **Node ID:** `unit_testing/test_genai_features.py::test_genai_admin_report_cross_institution_blocked_for_institution_admin`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/ai/reports/",
      "body": {
        "institution_id": "inst-2"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_genai_admin_report_cross_institution_blocked_for_institution_admin(genai_client_and_state):
    client, state, *_ = genai_client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-2"})
    assert response.status_code == 403
```

---

### 23. `test_genai_admin_report_result_roundtrip` — ✅ PASSED

- **Source:** `unit_testing/test_genai_features.py:259`
- **Node ID:** `unit_testing/test_genai_features.py::test_genai_admin_report_result_roundtrip`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/ai/reports/",
      "body": {
        "institution_id": "inst-1"
      }
    },
    {
      "method": "GET",
      "url": "f\"/api/v1/ai/reports/{report_id}/status\""
    },
    {
      "method": "GET",
      "url": "f\"/api/v1/ai/reports/{report_id}/result\""
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "status.json()[\"status\"]",
      "expected_value": "completed"
    }
  ],
  "expected_keys_present": [
    "\"summary\" in result.json()[\"result\"]"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_genai_admin_report_result_roundtrip(genai_client_and_state):
    client, state, _, _, _ = genai_client_and_state
    state["user_id"] = "admin-1"

    created = client.post("/api/v1/ai/reports/", json={"institution_id": "inst-1"})
    assert created.status_code == 200
    report_id = created.json()["report_id"]

    status = client.get(f"/api/v1/ai/reports/{report_id}/status")
    assert status.status_code == 200
    assert status.json()["status"] == "completed"

    result = client.get(f"/api/v1/ai/reports/{report_id}/result")
    assert result.status_code == 200
    assert "summary" in result.json()["result"]
```

---

### 24. `test_genai_student_explanation_success` — ✅ PASSED

- **Source:** `unit_testing/test_genai_features.py:276`
- **Node ID:** `unit_testing/test_genai_features.py::test_genai_student_explanation_success`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/ai/student-explanations/",
      "body": {
        "submission_id": "submission-1",
        "question_id": "question-1"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "response.json()[\"status\"]",
      "expected_value": "completed"
    },
    {
      "field": "explanation_gemini.calls",
      "expected_value": 1
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_genai_student_explanation_success(genai_client_and_state):
    client, state, _, explanation_gemini, _ = genai_client_and_state
    state["user_id"] = "student-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert explanation_gemini.calls == 1
```

---

### 25. `test_genai_student_explanation_forbidden_for_educator` — ✅ PASSED

- **Source:** `unit_testing/test_genai_features.py:289`
- **Node ID:** `unit_testing/test_genai_features.py::test_genai_student_explanation_forbidden_for_educator`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/ai/student-explanations/",
      "body": {
        "submission_id": "submission-1",
        "question_id": "question-1"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_genai_student_explanation_forbidden_for_educator(genai_client_and_state):
    client, state, *_ = genai_client_and_state
    state["user_id"] = "educator-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1"},
    )
    assert response.status_code == 403
```

---

### 26. `test_genai_student_explanation_requires_ownership` — ✅ PASSED

- **Source:** `unit_testing/test_genai_features.py:300`
- **Node ID:** `unit_testing/test_genai_features.py::test_genai_student_explanation_requires_ownership`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/ai/student-explanations/",
      "body": {
        "submission_id": "submission-2",
        "question_id": "question-1"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_genai_student_explanation_requires_ownership(genai_client_and_state):
    client, state, *_ = genai_client_and_state
    state["user_id"] = "student-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-2", "question_id": "question-1"},
    )
    assert response.status_code == 403
```

---

### 27. `test_genai_persists_generation_metadata` — ✅ PASSED

- **Source:** `unit_testing/test_genai_features.py:311`
- **Node ID:** `unit_testing/test_genai_features.py::test_genai_persists_generation_metadata`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/ai/student-explanations/",
      "body": {
        "submission_id": "submission-1",
        "question_id": "question-1"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "row.feature_type",
      "expected_value": "AIFeatureType.STUDENT_EXPLANATION"
    },
    {
      "field": "row.status",
      "expected_value": "AIGenerationStatus.COMPLETED"
    },
    {
      "field": "row.total_tokens",
      "expected_value": 50
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_genai_persists_generation_metadata(genai_client_and_state):
    client, state, _, _, session_local = genai_client_and_state
    state["user_id"] = "student-1"

    response = client.post(
        "/api/v1/ai/student-explanations/",
        json={"submission_id": "submission-1", "question_id": "question-1"},
    )
    assert response.status_code == 200
    explanation_id = response.json()["explanation_id"]

    async def _check():
        async with session_local() as session:
            row = (await session.execute(select(AIGeneration).where(AIGeneration.id == explanation_id))).scalar_one()
            assert row.feature_type == AIFeatureType.STUDENT_EXPLANATION
            assert row.status == AIGenerationStatus.COMPLETED
            assert row.total_tokens == 50

    asyncio.run(_check())
```

---

### 28. `test_institution_admin_dashboard_stats` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:202`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_stats`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/educator"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"assigned_workshops\"]",
      "expected_value": "payload[\"assigned_workshops\"] >= 1"
    }
  ],
  "expected_keys_present": [
    "\"pending_submissions\" in payload"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_dashboard_stats(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 200
    payload = response.json()
    assert payload["assigned_workshops"] >= 1
    assert "pending_submissions" in payload
```

---

### 29. `test_institution_admin_workshop_scope_and_create` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:213`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_workshop_scope_and_create`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/workshops/"
    },
    {
      "method": "POST",
      "url": "/api/v1/workshops/",
      "body": {
        "title": "Created by Institution Admin",
        "description": "Scoped create"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    200,
    201
  ],
  "expected_json_fields": [
    {
      "field": "create_response.json()[\"institution_id\"]",
      "expected_value": "inst-1"
    }
  ],
  "expected_keys_present": [
    "\"workshop-own\" in returned_ids"
  ],
  "other_assertions": [
    "assert \"workshop-other\" not in returned_ids"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_workshop_scope_and_create(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    list_response = client.get("/api/v1/workshops/")
    assert list_response.status_code == 200
    returned_ids = {item["id"] for item in list_response.json()["items"]}
    assert "workshop-own" in returned_ids
    assert "workshop-other" not in returned_ids

    create_response = client.post(
        "/api/v1/workshops/",
        json={"title": "Created by Institution Admin", "description": "Scoped create"},
    )
    assert create_response.status_code == 201
    assert create_response.json()["institution_id"] == "inst-1"
```

---

### 30. `test_institution_admin_cannot_update_other_institution_workshop` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:231`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_cannot_update_other_institution_workshop`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "PATCH",
      "url": "/api/v1/workshops/workshop-other",
      "body": {
        "title": "Illegal update"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_cannot_update_other_institution_workshop(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.patch("/api/v1/workshops/workshop-other", json={"title": "Illegal update"})
    assert response.status_code == 403
```

---

### 31. `test_institution_admin_users_list_is_scoped` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:239`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_users_list_is_scoped`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/users/?limit=200"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "other_assertions": [
    "assert all(item[\"institution_id\"] == \"inst-1\" for item in users)"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_users_list_is_scoped(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/users/?limit=200")
    assert response.status_code == 200
    users = response.json()["items"]
    assert all(item["institution_id"] == "inst-1" for item in users)
```

---

### 32. `test_institution_admin_can_fetch_student_enrollments` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:249`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_can_fetch_student_enrollments`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/enrollments/student/student-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "response.json()[\"total\"]",
      "expected_value": "response.json()[\"total\"] >= 1"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_can_fetch_student_enrollments(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/enrollments/student/student-1")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
```

---

### 33. `test_institution_admin_can_create_approval_request` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:258`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_can_create_approval_request`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/approvals/requests",
      "body": {
        "request_type": "delete_student",
        "payload": {
          "user_id": "student-1"
        }
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 201,
  "expected_json_fields": [
    {
      "field": "response.json()[\"status\"]",
      "expected_value": "pending"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_can_create_approval_request(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post(
        "/api/v1/approvals/requests",
        json={"request_type": "delete_student", "payload": {"user_id": "student-1"}},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "pending"
```

---

### 34. `test_institution_admin_dashboard_aggregate_and_leaderboards` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:270`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_aggregate_and_leaderboards`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/dashboard"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/assessment/assessment-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/workshop/workshop-own"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/workshop/workshop-own/student/student-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "assessment_lb.json()[\"assessment_id\"]",
      "expected_value": "assessment-1"
    },
    {
      "field": "workshop_lb.json()[\"workshop_id\"]",
      "expected_value": "workshop-own"
    },
    {
      "field": "assessment_drilldown.json()[\"student_id\"]",
      "expected_value": "student-1"
    },
    {
      "field": "workshop_drilldown.json()[\"context_type\"]",
      "expected_value": "workshop"
    }
  ],
  "expected_keys_present": [
    "\"kpis\" in payload",
    "\"alerts\" in payload",
    "\"attendance_trend\" in payload"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_dashboard_aggregate_and_leaderboards(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    aggregate = client.get("/api/v1/analytics/institution/dashboard")
    assert aggregate.status_code == 200
    payload = aggregate.json()
    assert "kpis" in payload
    assert "alerts" in payload
    assert "attendance_trend" in payload

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"

    workshop_lb = client.get("/api/v1/analytics/leaderboard/workshop/workshop-own")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-own"

    assessment_drilldown = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["student_id"] == "student-1"

    workshop_drilldown = client.get("/api/v1/analytics/leaderboard/workshop/workshop-own/student/student-1")
    assert workshop_drilldown.status_code == 200
    assert workshop_drilldown.json()["context_type"] == "workshop"
```

---

### 35. `test_institution_admin_student_roster_and_attendance_report` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:298`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_student_roster_and_attendance_report`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/students"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/attendance-report"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"total\"]",
      "expected_value": "payload[\"total\"] >= 1"
    },
    {
      "field": "attendance_payload[\"total\"]",
      "expected_value": "attendance_payload[\"total\"] >= 1"
    }
  ],
  "other_assertions": [
    "assert any(item[\"id\"] == \"student-1\" for item in payload[\"items\"])",
    "assert any(item[\"student\"] == \"Student One\" for item in attendance_payload[\"rows\"])"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_student_roster_and_attendance_report(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    students = client.get("/api/v1/analytics/institution/students")
    assert students.status_code == 200
    payload = students.json()
    assert payload["total"] >= 1
    assert any(item["id"] == "student-1" for item in payload["items"])

    attendance = client.get("/api/v1/analytics/institution/attendance-report")
    assert attendance.status_code == 200
    attendance_payload = attendance.json()
    assert attendance_payload["total"] >= 1
    assert any(item["student"] == "Student One" for item in attendance_payload["rows"])
```

---

### 36. `test_institution_admin_parent_message_dispatch` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:315`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_parent_message_dispatch`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/communication/parent-email",
      "body": {
        "student_ids": [
          "student-1"
        ],
        "subject": "Progress Update",
        "body": "Please review the latest grades."
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "response.json()[\"accepted\"]",
      "expected_value": 1
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_parent_message_dispatch(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["student-1"],
            "subject": "Progress Update",
            "body": "Please review the latest grades.",
        },
    )
    assert response.status_code == 200
    assert response.json()["accepted"] == 1
```

---

### 37. `test_institution_admin_bulk_and_export_endpoints` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:331`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_bulk_and_export_endpoints`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/analytics/institution/students/bulk-action",
      "body": {
        "student_ids": [
          "student-1"
        ],
        "action": "set_inactive"
      }
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/students"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/students/export?student_ids=student-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/attendance-report/export"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/dashboard/export"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"requested_students\"]",
      "expected_value": 1
    },
    {
      "field": "payload[\"updated_enrollments\"]",
      "expected_value": "payload[\"updated_enrollments\"] >= 1"
    },
    {
      "field": "student_row[\"status\"]",
      "expected_value": "Inactive"
    },
    {
      "field": "attendance_export.json()[\"file_type\"]",
      "expected_value": "csv"
    },
    {
      "field": "dashboard_export.json()[\"file_type\"]",
      "expected_value": "csv"
    }
  ],
  "expected_keys_present": [
    "\"/media/exports/\" in students_export.json()[\"download_url\"]"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_bulk_and_export_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    bulk_action = client.post(
        "/api/v1/analytics/institution/students/bulk-action",
        json={"student_ids": ["student-1"], "action": "set_inactive"},
    )
    assert bulk_action.status_code == 200
    payload = bulk_action.json()
    assert payload["requested_students"] == 1
    assert payload["updated_enrollments"] >= 1

    students = client.get("/api/v1/analytics/institution/students")
    assert students.status_code == 200
    student_row = next(item for item in students.json()["items"] if item["id"] == "student-1")
    assert student_row["status"] == "Inactive"

    students_export = client.get("/api/v1/analytics/institution/students/export?student_ids=student-1")
    assert students_export.status_code == 200
    assert "/media/exports/" in students_export.json()["download_url"]

    attendance_export = client.get("/api/v1/analytics/institution/attendance-report/export")
    assert attendance_export.status_code == 200
    assert attendance_export.json()["file_type"] == "csv"

    dashboard_export = client.get("/api/v1/analytics/institution/dashboard/export")
    assert dashboard_export.status_code == 200
    assert dashboard_export.json()["file_type"] == "csv"
```

---

### 38. `test_institution_admin_parent_contact_lookup` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:361`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_parent_contact_lookup`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/communication/parent-contacts?student_ids=student-1&student_ids=student-2"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"total\"]",
      "expected_value": 1
    },
    {
      "field": "payload[\"items\"][0][\"student_id\"]",
      "expected_value": "student-1"
    },
    {
      "field": "payload[\"items\"][0][\"parent_email\"]",
      "expected_value": "parent1@example.com"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_parent_contact_lookup(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/communication/parent-contacts?student_ids=student-1&student_ids=student-2")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["student_id"] == "student-1"
    assert payload["items"][0]["parent_email"] == "parent1@example.com"
```

---

### 39. `test_institution_admin_profile_metadata_update_self_only` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:373`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_profile_metadata_update_self_only`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "PATCH",
      "url": "/api/v1/users/inst-admin-1",
      "body": {
        "bio": "Leads institutional operations.",
        "department": "Administration",
        "institution_admin_name": "IIT Delhi South Campus",
        "institution_admin_address": "Hauz Khas, New Delhi",
        "institution_admin_code": "IITD-SA"
      }
    },
    {
      "method": "PATCH",
      "url": "/api/v1/users/student-1",
      "body": {
        "bio": "Should fail"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    200,
    403
  ],
  "expected_json_fields": [
    {
      "field": "payload[\"bio\"]",
      "expected_value": "Leads institutional operations."
    },
    {
      "field": "payload[\"department\"]",
      "expected_value": "Administration"
    },
    {
      "field": "payload[\"institution_admin_code\"]",
      "expected_value": "IITD-SA"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_profile_metadata_update_self_only(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    update_self = client.patch(
        "/api/v1/users/inst-admin-1",
        json={
            "bio": "Leads institutional operations.",
            "department": "Administration",
            "institution_admin_name": "IIT Delhi South Campus",
            "institution_admin_address": "Hauz Khas, New Delhi",
            "institution_admin_code": "IITD-SA",
        },
    )
    assert update_self.status_code == 200
    payload = update_self.json()
    assert payload["bio"] == "Leads institutional operations."
    assert payload["department"] == "Administration"
    assert payload["institution_admin_code"] == "IITD-SA"

    update_other = client.patch(
        "/api/v1/users/student-1",
        json={"bio": "Should fail"},
    )
    assert update_other.status_code == 403
```

---

### 40. `test_institution_admin_cannot_access_platform_admin_dashboard` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:400`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_cannot_access_platform_admin_dashboard`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/admin"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_cannot_access_platform_admin_dashboard(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/dashboard/admin")
    assert response.status_code == 403
```

---

### 41. `test_institution_admin_cannot_approve_requests` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:408`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_cannot_approve_requests`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/approvals/requests/approval-existing/approve"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_cannot_approve_requests(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post("/api/v1/approvals/requests/approval-existing/approve")
    assert response.status_code == 403
```

---

### 42. `test_institution_admin_dashboard_export_available` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:416`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_export_available`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/dashboard/export"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_keys_present": [
    "\"/media/exports/\" in response.json()[\"download_url\"]"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_dashboard_export_available(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/analytics/institution/dashboard/export")
    assert response.status_code == 200
    assert "/media/exports/" in response.json()["download_url"]
```

---

### 43. `test_institution_admin_cannot_read_other_student_enrollments` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:425`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_cannot_read_other_student_enrollments`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/enrollments/student/student-2"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_keys_present": [
    "\"items\" in response.json()"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_cannot_read_other_student_enrollments(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.get("/api/v1/enrollments/student/student-2")
    assert response.status_code == 200
    assert "items" in response.json()
```

---

### 44. `test_institution_admin_workshop_patch_own_workshop` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:434`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_workshop_patch_own_workshop`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "PATCH",
      "url": "/api/v1/workshops/workshop-own",
      "body": {
        "title": "Institution Workshop Updated"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "response.json()[\"title\"]",
      "expected_value": "Institution Workshop Updated"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_workshop_patch_own_workshop(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.patch("/api/v1/workshops/workshop-own", json={"title": "Institution Workshop Updated"})
    assert response.status_code == 200
    assert response.json()["title"] == "Institution Workshop Updated"
```

---

### 45. `test_institution_admin_cannot_process_salary` — ✅ PASSED

- **Source:** `unit_testing/test_institutional_admin.py:443`
- **Node ID:** `unit_testing/test_institutional_admin.py::test_institution_admin_cannot_process_salary`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/salaries/pay",
      "body": {
        "educator_id": "educator-1",
        "month": "2026-04",
        "amount": 60000
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_institution_admin_cannot_process_salary(client_and_state):
    client, state = client_and_state
    state["user_id"] = "inst-admin-1"

    response = client.post(
        "/api/v1/salaries/pay",
        json={"educator_id": "educator-1", "month": "2026-04", "amount": 60000},
    )
    assert response.status_code == 403
```

---

### 46. `test_admin_dashboard_stats_success` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:178`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_dashboard_stats_success`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/admin"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"total_institutions\"]",
      "expected_value": "payload[\"total_institutions\"] >= 1"
    },
    {
      "field": "payload[\"total_workshops\"]",
      "expected_value": "payload[\"total_workshops\"] >= 1"
    },
    {
      "field": "payload[\"total_students\"]",
      "expected_value": "payload[\"total_students\"] >= 1"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_dashboard_stats_success(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/dashboard/admin")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total_institutions"] >= 1
    assert payload["total_workshops"] >= 1
    assert payload["total_students"] >= 1
```

---

### 47. `test_admin_dashboard_forbidden_for_non_admin` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:190`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_dashboard_forbidden_for_non_admin`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/admin"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_dashboard_forbidden_for_non_admin(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-inst-admin"

    response = client.get("/api/v1/dashboard/admin")
    assert response.status_code == 403
```

---

### 48. `test_admin_workshop_crud` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:198`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_workshop_crud`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/workshops/",
      "body": {
        "title": "New Admin Workshop",
        "description": "Created by admin",
        "institution_id": "inst-1"
      }
    },
    {
      "method": "PATCH",
      "url": "f\"/api/v1/workshops/{created_id}\"",
      "body": {
        "title": "Renamed Workshop"
      }
    },
    {
      "method": "DELETE",
      "url": "f\"/api/v1/workshops/{created_id}\""
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    201,
    200,
    204
  ],
  "expected_json_fields": [
    {
      "field": "patch_response.json()[\"title\"]",
      "expected_value": "Renamed Workshop"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_workshop_crud(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    create_response = client.post(
        "/api/v1/workshops/",
        json={
            "title": "New Admin Workshop",
            "description": "Created by admin",
            "institution_id": "inst-1",
        },
    )
    assert create_response.status_code == 201
    created_id = create_response.json()["id"]

    patch_response = client.patch(f"/api/v1/workshops/{created_id}", json={"title": "Renamed Workshop"})
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Renamed Workshop"

    delete_response = client.delete(f"/api/v1/workshops/{created_id}")
    assert delete_response.status_code == 204
```

---

### 49. `test_admin_approval_list_and_approve` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:221`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_approval_list_and_approve`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/approvals/requests"
    },
    {
      "method": "POST",
      "url": "/api/v1/approvals/requests/approval-1/approve"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "approve_response.json()[\"status\"]",
      "expected_value": "approved"
    }
  ],
  "expected_keys_present": [
    "\"approval-1\" in request_ids"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_approval_list_and_approve(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    list_response = client.get("/api/v1/approvals/requests")
    assert list_response.status_code == 200
    request_ids = [item["id"] for item in list_response.json()["items"]]
    assert "approval-1" in request_ids

    approve_response = client.post("/api/v1/approvals/requests/approval-1/approve")
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"
```

---

### 50. `test_admin_salary_pay_and_list` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:235`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_salary_pay_and_list`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/salaries/pay",
      "body": {
        "educator_id": "user-inst-admin",
        "month": "2026-04",
        "amount": 62000
      }
    },
    {
      "method": "GET",
      "url": "/api/v1/salaries/?month=2026-04"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    201,
    200
  ],
  "expected_json_fields": [
    {
      "field": "pay_response.json()[\"amount\"]",
      "expected_value": 62000
    }
  ],
  "other_assertions": [
    "assert any(item[\"month\"] == \"2026-04\" for item in list_response.json()[\"items\"])"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_salary_pay_and_list(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    pay_response = client.post(
        "/api/v1/salaries/pay",
        json={"educator_id": "user-inst-admin", "month": "2026-04", "amount": 62000},
    )
    assert pay_response.status_code == 201
    assert pay_response.json()["amount"] == 62000

    list_response = client.get("/api/v1/salaries/?month=2026-04")
    assert list_response.status_code == 200
    assert any(item["month"] == "2026-04" for item in list_response.json()["items"])
```

---

### 51. `test_admin_users_and_institutions_endpoints` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:251`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_users_and_institutions_endpoints`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/users/?limit=50"
    },
    {
      "method": "GET",
      "url": "/api/v1/institutions/"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "users_response.json()[\"total\"]",
      "expected_value": "users_response.json()[\"total\"] >= 3"
    }
  ],
  "other_assertions": [
    "assert any(item[\"id\"] == \"inst-1\" for item in institutions_response.json())"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_users_and_institutions_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    users_response = client.get("/api/v1/users/?limit=50")
    assert users_response.status_code == 200
    assert users_response.json()["total"] >= 3

    institutions_response = client.get("/api/v1/institutions/")
    assert institutions_response.status_code == 200
    assert any(item["id"] == "inst-1" for item in institutions_response.json())
```

---

### 52. `test_admin_new_analytics_endpoints` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:264`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_new_analytics_endpoints`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/assessment/assessment-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/workshop/workshop-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/admin/insights"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/students"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/attendance-report"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/assessment/assessment-1/student/user-student"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/admin/insights"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    200,
    403
  ],
  "expected_json_fields": [
    {
      "field": "assessment_lb.json()[\"assessment_id\"]",
      "expected_value": "assessment-1"
    },
    {
      "field": "len(assessment_lb.json()[\"entries\"])",
      "expected_value": "len(assessment_lb.json()[\"entries\"]) >= 1"
    },
    {
      "field": "workshop_lb.json()[\"workshop_id\"]",
      "expected_value": "workshop-1"
    },
    {
      "field": "len(payload[\"weekly_activity\"])",
      "expected_value": 7
    },
    {
      "field": "institution_students.json()[\"total\"]",
      "expected_value": "institution_students.json()[\"total\"] >= 1"
    },
    {
      "field": "assessment_drilldown.json()[\"context_type\"]",
      "expected_value": "assessment"
    }
  ],
  "expected_keys_present": [
    "\"weekly_activity\" in payload",
    "\"demographics\" in payload",
    "\"activity_feed\" in payload"
  ],
  "expected_type_checks": [
    "isinstance(payload[\"demographics\"], list)",
    "isinstance(payload[\"activity_feed\"], list)"
  ],
  "other_assertions": [
    "assert all(\"label\" in point and \"value\" in point for point in payload[\"weekly_activity\"])",
    "assert all({\"range\", \"male\", \"female\"}.issubset(item.keys()) for item in payload[\"demographics\"])",
    "assert all({\"id\", \"text\", \"time\", \"type\"}.issubset(item.keys()) for item in payload[\"activity_feed\"])"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_new_analytics_endpoints(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    assessment_lb = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"
    assert len(assessment_lb.json()["entries"]) >= 1

    workshop_lb = client.get("/api/v1/analytics/leaderboard/workshop/workshop-1")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-1"

    admin_insights = client.get("/api/v1/analytics/admin/insights")
    assert admin_insights.status_code == 200
    payload = admin_insights.json()
    assert "weekly_activity" in payload
    assert len(payload["weekly_activity"]) == 7
    assert all("label" in point and "value" in point for point in payload["weekly_activity"])
    assert "demographics" in payload
    assert isinstance(payload["demographics"], list)
    if payload["demographics"]:
        assert all({"range", "male", "female"}.issubset(item.keys()) for item in payload["demographics"])
    assert "activity_feed" in payload
    assert isinstance(payload["activity_feed"], list)
    if payload["activity_feed"]:
        assert all({"id", "text", "time", "type"}.issubset(item.keys()) for item in payload["activity_feed"])

    institution_students = client.get("/api/v1/analytics/institution/students")
    assert institution_students.status_code == 200
    assert institution_students.json()["total"] >= 1

    institution_attendance = client.get("/api/v1/analytics/institution/attendance-report")
    assert institution_attendance.status_code == 200

    assessment_drilldown = client.get("/api/v1/analytics/leaderboard/assessment/assessment-1/student/user-student")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["context_type"] == "assessment"

    state["user_id"] = "user-inst-admin"
    forbidden_insights = client.get("/api/v1/analytics/admin/insights")
    assert forbidden_insights.status_code == 403
```

---

### 53. `test_admin_parent_communication_dispatch` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:308`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_parent_communication_dispatch`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/communication/parent-email",
      "body": {
        "student_ids": [
          "user-student"
        ],
        "subject": "Attendance Follow-up",
        "body": "Please connect with mentor."
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"accepted\"]",
      "expected_value": 1
    },
    {
      "field": "payload[\"failed\"]",
      "expected_value": 0
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_parent_communication_dispatch(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.post(
        "/api/v1/communication/parent-email",
        json={
            "student_ids": ["user-student"],
            "subject": "Attendance Follow-up",
            "body": "Please connect with mentor.",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] == 1
    assert payload["failed"] == 0
```

---

### 54. `test_admin_can_read_approval_request_details` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:326`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_can_read_approval_request_details`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/approvals/requests/approval-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 404
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_can_read_approval_request_details(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/approvals/requests/approval-1")
    assert response.status_code == 404
```

---

### 55. `test_admin_approving_unknown_request_returns_not_found` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:334`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_approving_unknown_request_returns_not_found`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/approvals/requests/approval-missing/approve"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 404
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_approving_unknown_request_returns_not_found(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.post("/api/v1/approvals/requests/approval-missing/approve")
    assert response.status_code == 404
```

---

### 56. `test_admin_can_fetch_submission_review` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:342`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_can_fetch_submission_review`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/submissions/submission-1/review"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "response.json()[\"submission_id\"]",
      "expected_value": "submission-1"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_can_fetch_submission_review(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/submissions/submission-1/review")
    assert response.status_code == 200
    assert response.json()["submission_id"] == "submission-1"
```

---

### 57. `test_admin_can_export_performance_report` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:351`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_can_export_performance_report`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/reports/performance/export"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "response.json()[\"file_type\"]",
      "expected_value": "csv"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_can_export_performance_report(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.get("/api/v1/analytics/reports/performance/export")
    assert response.status_code == 200
    assert response.json()["file_type"] == "csv"
```

---

### 58. `test_platform_admin_endpoints_forbidden_for_student` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:360`
- **Node ID:** `unit_testing/test_platform_admin.py::test_platform_admin_endpoints_forbidden_for_student`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/admin"
    },
    {
      "method": "GET",
      "url": "/api/v1/users/?limit=20"
    },
    {
      "method": "POST",
      "url": "/api/v1/approvals/requests/approval-1/approve"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_platform_admin_endpoints_forbidden_for_student(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-student"

    assert client.get("/api/v1/dashboard/admin").status_code == 403
    assert client.get("/api/v1/users/?limit=20").status_code == 403
    assert client.post("/api/v1/approvals/requests/approval-1/approve").status_code == 403
```

---

### 59. `test_admin_workshop_create_validation_error` — ✅ PASSED

- **Source:** `unit_testing/test_platform_admin.py:369`
- **Node ID:** `unit_testing/test_platform_admin.py::test_admin_workshop_create_validation_error`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/workshops/",
      "body": {
        "description": "Missing title should fail",
        "institution_id": "inst-1"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 422
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_admin_workshop_create_validation_error(client_and_state):
    client, state = client_and_state
    state["user_id"] = "user-admin"

    response = client.post(
        "/api/v1/workshops/",
        json={"description": "Missing title should fail", "institution_id": "inst-1"},
    )
    assert response.status_code == 422
```

---

### 60. `test_student_auth_register_and_login` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:177`
- **Node ID:** `unit_testing/test_student.py::test_student_auth_register_and_login`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/auth/register",
      "body": {
        "name": "New Student",
        "email": "newstudent@eduflow.edu",
        "password": "secret123",
        "role": "student"
      }
    },
    {
      "method": "POST",
      "url": "/api/v1/auth/login",
      "body": {
        "email": "newstudent@eduflow.edu",
        "password": "secret123"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    201,
    200
  ],
  "expected_keys_present": [
    "\"access_token\" in login_response.json()",
    "\"refresh_token\" in login_response.json()"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_auth_register_and_login(client_and_state):
    client, _ = client_and_state

    register_response = client.post(
        "/api/v1/auth/register",
        json={"name": "New Student", "email": "newstudent@eduflow.edu",
              "password": "secret123", "role": "student"},
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "newstudent@eduflow.edu", "password": "secret123"},
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert "refresh_token" in login_response.json()
```

---

### 61. `test_student_dashboard_and_analytics` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:196`
- **Node ID:** `unit_testing/test_student.py::test_student_dashboard_and_analytics`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/student/student-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/student/student-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 200,
  "expected_json_fields": [
    {
      "field": "payload[\"student_id\"]",
      "expected_value": "student-1"
    }
  ],
  "expected_keys_present": [
    "\"enrolled_workshops\" in dashboard.json()",
    "\"assessment\" in payload",
    "\"avg_percentage\" in payload[\"assessment\"]",
    "\"score_trend\" in payload[\"assessment\"]",
    "\"percentage\" in first_point",
    "\"submitted_at\" in first_point"
  ],
  "expected_type_checks": [
    "isinstance(payload[\"assessment\"][\"score_trend\"], list)"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_dashboard_and_analytics(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    dashboard = client.get("/api/v1/dashboard/student/student-1")
    assert dashboard.status_code == 200
    assert "enrolled_workshops" in dashboard.json()

    analytics = client.get("/api/v1/analytics/student/student-1")
    assert analytics.status_code == 200
    payload = analytics.json()
    assert payload["student_id"] == "student-1"
    assert "assessment" in payload
    assert "avg_percentage" in payload["assessment"]
    assert "score_trend" in payload["assessment"]
    assert isinstance(payload["assessment"]["score_trend"], list)
    if payload["assessment"]["score_trend"]:
        first_point = payload["assessment"]["score_trend"][0]
        assert "percentage" in first_point
        assert "submitted_at" in first_point
```

---

### 62. `test_student_workshops_and_enrollments` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:218`
- **Node ID:** `unit_testing/test_student.py::test_student_workshops_and_enrollments`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/workshops/"
    },
    {
      "method": "GET",
      "url": "/api/v1/enrollments/student/student-1"
    },
    {
      "method": "POST",
      "url": "/api/v1/enrollments/",
      "body": {
        "student_id": "student-2",
        "workshop_id": "workshop-1"
      }
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    200,
    403
  ],
  "expected_json_fields": [
    {
      "field": "workshops.json()[\"total\"]",
      "expected_value": "workshops.json()[\"total\"] >= 1"
    },
    {
      "field": "enrollments.json()[\"total\"]",
      "expected_value": "enrollments.json()[\"total\"] >= 1"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_workshops_and_enrollments(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    workshops = client.get("/api/v1/workshops/")
    assert workshops.status_code == 200
    assert workshops.json()["total"] >= 1

    enrollments = client.get("/api/v1/enrollments/student/student-1")
    assert enrollments.status_code == 200
    assert enrollments.json()["total"] >= 1

    forbidden_enroll = client.post(
        "/api/v1/enrollments/", json={"student_id": "student-2", "workshop_id": "workshop-1"})
    assert forbidden_enroll.status_code == 403
```

---

### 63. `test_student_attempt_start_save_submit_flow` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:235`
- **Node ID:** `unit_testing/test_student.py::test_student_attempt_start_save_submit_flow`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/tests/assessment-1/start"
    },
    {
      "method": "POST",
      "url": "f\"/api/v1/submissions/{submission_id}/answers\"",
      "body": {
        "answers": [
          {
            "question_id": "question-1",
            "selected_option_ids": [
              "q1-a"
            ]
          },
          {
            "question_id": "question-2",
            "selected_option_ids": [
              "q2-a"
            ]
          }
        ]
      }
    },
    {
      "method": "POST",
      "url": "f\"/api/v1/tests/assessment-1/submit?submission_id={submission_id}\""
    },
    {
      "method": "POST",
      "url": "f\"/api/v1/tests/assessment-1/submit?submission_id={submission_id}\""
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    201,
    200,
    409
  ],
  "expected_json_fields": [
    {
      "field": "len(start_payload[\"questions\"])",
      "expected_value": "len(start_payload[\"questions\"]) >= 2"
    },
    {
      "field": "submit.json()[\"score\"]",
      "expected_value": 20
    }
  ],
  "other_assertions": [
    "assert submit.json()[\"pass_fail\"] is True"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_attempt_start_save_submit_flow(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    start_response = client.post("/api/v1/tests/assessment-1/start")
    assert start_response.status_code == 201
    start_payload = start_response.json()
    submission_id = start_payload["submission_id"]
    assert len(start_payload["questions"]) >= 2

    save_answers = client.post(
        f"/api/v1/submissions/{submission_id}/answers",
        json={
            "answers": [
                {"question_id": "question-1", "selected_option_ids": ["q1-a"]},
                {"question_id": "question-2", "selected_option_ids": ["q2-a"]},
            ]
        },
    )
    assert save_answers.status_code == 200

    submit = client.post(
        f"/api/v1/tests/assessment-1/submit?submission_id={submission_id}")
    assert submit.status_code == 200
    assert submit.json()["score"] == 20
    assert submit.json()["pass_fail"] is True

    re_submit = client.post(
        f"/api/v1/tests/assessment-1/submit?submission_id={submission_id}")
    assert re_submit.status_code == 409
```

---

### 64. `test_student_certificates_notifications_and_profile` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:267`
- **Node ID:** `unit_testing/test_student.py::test_student_certificates_notifications_and_profile`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/certificates/student/student-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/certificates/verify/VERIFY-123"
    },
    {
      "method": "GET",
      "url": "/api/v1/notifications/student-1"
    },
    {
      "method": "PATCH",
      "url": "f\"/api/v1/notifications/{first_notification_id}/read\""
    },
    {
      "method": "DELETE",
      "url": "f\"/api/v1/notifications/{first_notification_id}\""
    },
    {
      "method": "GET",
      "url": "/api/v1/users/me"
    },
    {
      "method": "PATCH",
      "url": "/api/v1/users/student-1",
      "body": {
        "bio": "I love frontend engineering.",
        "department": "Computer Science"
      }
    },
    {
      "method": "POST",
      "url": "/api/v1/users/student-1/profile-photo",
      "files": "{\"file\": (\"avatar.png\", b\"avatar-bytes\", \"image/png\")}"
    },
    {
      "method": "GET",
      "url": "/api/v1/certificates/certificate-1/download"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    200,
    204
  ],
  "expected_json_fields": [
    {
      "field": "certificates.json()[\"total\"]",
      "expected_value": "certificates.json()[\"total\"] >= 1"
    },
    {
      "field": "notifications.json()[\"total\"]",
      "expected_value": "notifications.json()[\"total\"] >= 1"
    },
    {
      "field": "mark_read.json()[\"status\"]",
      "expected_value": "read"
    },
    {
      "field": "me.json()[\"id\"]",
      "expected_value": "student-1"
    },
    {
      "field": "profile_update.json()[\"bio\"]",
      "expected_value": "I love frontend engineering."
    },
    {
      "field": "profile_update.json()[\"department\"]",
      "expected_value": "Computer Science"
    }
  ],
  "expected_keys_present": [
    "\"/media/certificates/certificate-1.pdf\" in certificate_download.json()[\n        \"download_url\"]"
  ],
  "other_assertions": [
    "assert profile_upload.json()[\"profile_photo\"].startswith(\"media/avatars/\")"
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_certificates_notifications_and_profile(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    certificates = client.get("/api/v1/certificates/student/student-1")
    assert certificates.status_code == 200
    assert certificates.json()["total"] >= 1

    verify = client.get("/api/v1/certificates/verify/VERIFY-123")
    assert verify.status_code == 200

    notifications = client.get("/api/v1/notifications/student-1")
    assert notifications.status_code == 200
    assert notifications.json()["total"] >= 1

    first_notification_id = notifications.json()["items"][0]["id"]
    mark_read = client.patch(
        f"/api/v1/notifications/{first_notification_id}/read")
    assert mark_read.status_code == 200
    assert mark_read.json()["status"] == "read"

    delete_notification = client.delete(
        f"/api/v1/notifications/{first_notification_id}")
    assert delete_notification.status_code == 204

    me = client.get("/api/v1/users/me")
    assert me.status_code == 200
    assert me.json()["id"] == "student-1"

    profile_update = client.patch(
        "/api/v1/users/student-1",
        json={"bio": "I love frontend engineering.",
              "department": "Computer Science"},
    )
    assert profile_update.status_code == 200
    assert profile_update.json()["bio"] == "I love frontend engineering."
    assert profile_update.json()["department"] == "Computer Science"

    profile_upload = client.post(
        "/api/v1/users/student-1/profile-photo",
        files={"file": ("avatar.png", b"avatar-bytes", "image/png")},
    )
    assert profile_upload.status_code == 200
    assert profile_upload.json()["profile_photo"].startswith("media/avatars/")

    certificate_download = client.get(
        "/api/v1/certificates/certificate-1/download")
    assert certificate_download.status_code == 200
    assert "/media/certificates/certificate-1.pdf" in certificate_download.json()[
        "download_url"]
```

---

### 65. `test_student_forbidden_from_other_student_data` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:319`
- **Node ID:** `unit_testing/test_student.py::test_student_forbidden_from_other_student_data`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/users/student-2"
    },
    {
      "method": "GET",
      "url": "/api/v1/dashboard/student/student-2"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/student/student-2"
    },
    {
      "method": "POST",
      "url": "/api/v1/users/student-2/profile-photo",
      "files": "{\"file\": (\"avatar.png\", b\"avatar-bytes\", \"image/png\")}"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_forbidden_from_other_student_data(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    other_profile = client.get("/api/v1/users/student-2")
    assert other_profile.status_code == 403

    other_dashboard = client.get("/api/v1/dashboard/student/student-2")
    assert other_dashboard.status_code == 403

    other_analytics = client.get("/api/v1/analytics/student/student-2")
    assert other_analytics.status_code == 403

    other_upload = client.post(
        "/api/v1/users/student-2/profile-photo",
        files={"file": ("avatar.png", b"avatar-bytes", "image/png")},
    )
    assert other_upload.status_code == 403
```

---

### 66. `test_student_leaderboard_access_and_staff_only_guards` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:339`
- **Node ID:** `unit_testing/test_student.py::test_student_leaderboard_access_and_staff_only_guards`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/assessment/assessment-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/workshop/workshop-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/leaderboard/workshop/workshop-1/student/student-1"
    },
    {
      "method": "GET",
      "url": "/api/v1/submissions/submission-graded/review"
    },
    {
      "method": "POST",
      "url": "/api/v1/submissions/submission-graded/grade"
    },
    {
      "method": "POST",
      "url": "/api/v1/communication/parent-email",
      "body": {
        "student_ids": [
          "student-1"
        ],
        "subject": "Hi",
        "body": "Test"
      }
    },
    {
      "method": "GET",
      "url": "/api/v1/communication/parent-contacts?student_ids=student-1"
    },
    {
      "method": "POST",
      "url": "/api/v1/analytics/institution/students/bulk-action",
      "body": {
        "student_ids": [
          "student-1"
        ],
        "action": "set_inactive"
      }
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/attendance-report/export"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/reports/performance/export"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": [
    200,
    403
  ],
  "expected_json_fields": [
    {
      "field": "assessment_lb.json()[\"assessment_id\"]",
      "expected_value": "assessment-1"
    },
    {
      "field": "workshop_lb.json()[\"workshop_id\"]",
      "expected_value": "workshop-1"
    },
    {
      "field": "assessment_drilldown.json()[\"student_id\"]",
      "expected_value": "student-1"
    },
    {
      "field": "workshop_drilldown.json()[\"context_type\"]",
      "expected_value": "workshop"
    }
  ]
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_leaderboard_access_and_staff_only_guards(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    assessment_lb = client.get(
        "/api/v1/analytics/leaderboard/assessment/assessment-1")
    assert assessment_lb.status_code == 200
    assert assessment_lb.json()["assessment_id"] == "assessment-1"

    workshop_lb = client.get(
        "/api/v1/analytics/leaderboard/workshop/workshop-1")
    assert workshop_lb.status_code == 200
    assert workshop_lb.json()["workshop_id"] == "workshop-1"

    assessment_drilldown = client.get(
        "/api/v1/analytics/leaderboard/assessment/assessment-1/student/student-1")
    assert assessment_drilldown.status_code == 200
    assert assessment_drilldown.json()["student_id"] == "student-1"

    workshop_drilldown = client.get(
        "/api/v1/analytics/leaderboard/workshop/workshop-1/student/student-1")
    assert workshop_drilldown.status_code == 200
    assert workshop_drilldown.json()["context_type"] == "workshop"

    review_forbidden = client.get(
        "/api/v1/submissions/submission-graded/review")
    assert review_forbidden.status_code == 403

    grade_forbidden = client.post(
        "/api/v1/submissions/submission-graded/grade")
    assert grade_forbidden.status_code == 403

    communication_forbidden = client.post(
        "/api/v1/communication/parent-email",
        json={"student_ids": ["student-1"], "subject": "Hi", "body": "Test"},
    )
    assert communication_forbidden.status_code == 403

    parent_contacts_forbidden = client.get(
        "/api/v1/communication/parent-contacts?student_ids=student-1")
    assert parent_contacts_forbidden.status_code == 403

    institution_bulk_forbidden = client.post(
        "/api/v1/analytics/institution/students/bulk-action",
        json={"student_ids": ["student-1"], "action": "set_inactive"},
    )
    assert institution_bulk_forbidden.status_code == 403

    attendance_export_forbidden = client.get(
        "/api/v1/analytics/institution/attendance-report/export")
    ...
```

---

### 67. `test_student_cannot_access_admin_or_institution_dashboards` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:396`
- **Node ID:** `unit_testing/test_student.py::test_student_cannot_access_admin_or_institution_dashboards`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/admin"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/admin/insights"
    },
    {
      "method": "GET",
      "url": "/api/v1/analytics/institution/dashboard"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_cannot_access_admin_or_institution_dashboards(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    assert client.get("/api/v1/dashboard/admin").status_code == 403
    assert client.get("/api/v1/analytics/admin/insights").status_code == 403
    assert client.get("/api/v1/analytics/institution/dashboard").status_code == 403
```

---

### 68. `test_student_cannot_view_educator_dashboard` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:405`
- **Node ID:** `unit_testing/test_student.py::test_student_cannot_view_educator_dashboard`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/dashboard/educator"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_cannot_view_educator_dashboard(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.get("/api/v1/dashboard/educator")
    assert response.status_code == 403
```

---

### 69. `test_student_invalid_certificate_verification_code` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:413`
- **Node ID:** `unit_testing/test_student.py::test_student_invalid_certificate_verification_code`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "GET",
      "url": "/api/v1/certificates/verify/INVALID-CODE"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 404
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_invalid_certificate_verification_code(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.get("/api/v1/certificates/verify/INVALID-CODE")
    assert response.status_code == 404
```

---

### 70. `test_student_cannot_delete_workshop` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:421`
- **Node ID:** `unit_testing/test_student.py::test_student_cannot_delete_workshop`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "DELETE",
      "url": "/api/v1/workshops/workshop-1"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_cannot_delete_workshop(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.delete("/api/v1/workshops/workshop-1")
    assert response.status_code == 403
```

---

### 71. `test_student_cannot_grade_submission` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:429`
- **Node ID:** `unit_testing/test_student.py::test_student_cannot_grade_submission`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/submissions/submission-graded/grade"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 403
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_cannot_grade_submission(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.post("/api/v1/submissions/submission-graded/grade")
    assert response.status_code == 403
```

---

### 72. `test_student_assessment_submit_unknown_submission` — ✅ PASSED

- **Source:** `unit_testing/test_student.py:437`
- **Node ID:** `unit_testing/test_student.py::test_student_assessment_submit_unknown_submission`

#### Input JSON (HTTP Requests)

```json
{
  "http_calls": [
    {
      "method": "POST",
      "url": "/api/v1/tests/assessment-1/submit?submission_id=does-not-exist"
    }
  ]
}
```

#### Expected Output JSON (Assertions)

```json
{
  "expected_status_codes": 404
}
```

#### Actual Output JSON (Pytest Result)

```json
{
  "pytest_result": "PASSED",
  "detail": "All assertions passed."
}
```

#### Code Snippet

```python
def test_student_assessment_submit_unknown_submission(client_and_state):
    client, state = client_and_state
    state["user_id"] = "student-1"

    response = client.post("/api/v1/tests/assessment-1/submit?submission_id=does-not-exist")
    assert response.status_code == 404
```

---

## Raw Pytest Output

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0 -- C:\Program Files\Python314\python.exe
cachedir: .pytest_cache
rootdir: E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend
configfile: pyproject.toml
plugins: anyio-4.11.0, dash-4.0.0, Faker-38.2.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 72 items

unit_testing/test_educator.py::test_educator_dashboard_stats PASSED      [  1%]
unit_testing/test_educator.py::test_educator_workshop_list_is_scoped PASSED [  2%]
unit_testing/test_educator.py::test_educator_can_view_assessments_and_submissions PASSED [  4%]
unit_testing/test_educator.py::test_educator_cannot_read_assessments_or_submissions_other_institution PASSED [  5%]
unit_testing/test_educator.py::test_educator_material_upload_and_delete PASSED [  6%]
unit_testing/test_educator.py::test_educator_can_fetch_workshop_analytics PASSED [  8%]
unit_testing/test_educator.py::test_educator_notifications_success PASSED [  9%]
unit_testing/test_educator.py::test_educator_can_view_review_and_dispatch_parent_message PASSED [ 11%]
unit_testing/test_educator.py::test_educator_can_grade_pending_submission PASSED [ 12%]
unit_testing/test_educator.py::test_educator_workshop_educator_profile_contract PASSED [ 13%]
unit_testing/test_educator.py::test_educator_certificate_recommend_and_download PASSED [ 15%]
unit_testing/test_educator.py::test_educator_performance_export_available PASSED [ 16%]
unit_testing/test_educator.py::test_educator_forbidden_admin_and_delete_routes PASSED [ 18%]
unit_testing/test_educator.py::test_educator_forbidden_from_salary_routes PASSED [ 19%]
unit_testing/test_educator.py::test_educator_cannot_approve_requests PASSED [ 20%]
unit_testing/test_educator.py::test_educator_cannot_access_admin_insights PASSED [ 22%]
unit_testing/test_educator.py::test_educator_rejects_non_owned_enrollment_queries PASSED [ 23%]
unit_testing/test_educator.py::test_educator_grading_unknown_submission_returns_not_found PASSED [ 25%]
unit_testing/test_educator.py::test_educator_notification_collection_forbidden_for_other_user PASSED [ 26%]
unit_testing/test_genai_features.py::test_genai_admin_report_success PASSED [ 27%]
unit_testing/test_genai_features.py::test_genai_admin_report_forbidden_for_student PASSED [ 29%]
unit_testing/test_genai_features.py::test_genai_admin_report_cross_institution_blocked_for_institution_admin PASSED [ 30%]
unit_testing/test_genai_features.py::test_genai_admin_report_result_roundtrip PASSED [ 31%]
unit_testing/test_genai_features.py::test_genai_student_explanation_success PASSED [ 33%]
unit_testing/test_genai_features.py::test_genai_student_explanation_forbidden_for_educator PASSED [ 34%]
unit_testing/test_genai_features.py::test_genai_student_explanation_requires_ownership PASSED [ 36%]
unit_testing/test_genai_features.py::test_genai_persists_generation_metadata PASSED [ 37%]
unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_stats PASSED [ 38%]
unit_testing/test_institutional_admin.py::test_institution_admin_workshop_scope_and_create PASSED [ 40%]
unit_testing/test_institutional_admin.py::test_institution_admin_cannot_update_other_institution_workshop PASSED [ 41%]
unit_testing/test_institutional_admin.py::test_institution_admin_users_list_is_scoped PASSED [ 43%]
unit_testing/test_institutional_admin.py::test_institution_admin_can_fetch_student_enrollments PASSED [ 44%]
unit_testing/test_institutional_admin.py::test_institution_admin_can_create_approval_request PASSED [ 45%]
unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_aggregate_and_leaderboards PASSED [ 47%]
unit_testing/test_institutional_admin.py::test_institution_admin_student_roster_and_attendance_report PASSED [ 48%]
unit_testing/test_institutional_admin.py::test_institution_admin_parent_message_dispatch PASSED [ 50%]
unit_testing/test_institutional_admin.py::test_institution_admin_bulk_and_export_endpoints PASSED [ 51%]
unit_testing/test_institutional_admin.py::test_institution_admin_parent_contact_lookup PASSED [ 52%]
unit_testing/test_institutional_admin.py::test_institution_admin_profile_metadata_update_self_only PASSED [ 54%]
unit_testing/test_institutional_admin.py::test_institution_admin_cannot_access_platform_admin_dashboard PASSED [ 55%]
unit_testing/test_institutional_admin.py::test_institution_admin_cannot_approve_requests PASSED [ 56%]
unit_testing/test_institutional_admin.py::test_institution_admin_dashboard_export_available PASSED [ 58%]
unit_testing/test_institutional_admin.py::test_institution_admin_cannot_read_other_student_enrollments PASSED [ 59%]
unit_testing/test_institutional_admin.py::test_institution_admin_workshop_patch_own_workshop PASSED [ 61%]
unit_testing/test_institutional_admin.py::test_institution_admin_cannot_process_salary PASSED [ 62%]
unit_testing/test_platform_admin.py::test_admin_dashboard_stats_success PASSED [ 63%]
unit_testing/test_platform_admin.py::test_admin_dashboard_forbidden_for_non_admin PASSED [ 65%]
unit_testing/test_platform_admin.py::test_admin_workshop_crud PASSED     [ 66%]
unit_testing/test_platform_admin.py::test_admin_approval_list_and_approve PASSED [ 68%]
unit_testing/test_platform_admin.py::test_admin_salary_pay_and_list PASSED [ 69%]
unit_testing/test_platform_admin.py::test_admin_users_and_institutions_endpoints PASSED [ 70%]
unit_testing/test_platform_admin.py::test_admin_new_analytics_endpoints PASSED [ 72%]
unit_testing/test_platform_admin.py::test_admin_parent_communication_dispatch PASSED [ 73%]
unit_testing/test_platform_admin.py::test_admin_can_read_approval_request_details PASSED [ 75%]
unit_testing/test_platform_admin.py::test_admin_approving_unknown_request_returns_not_found PASSED [ 76%]
unit_testing/test_platform_admin.py::test_admin_can_fetch_submission_review PASSED [ 77%]
unit_testing/test_platform_admin.py::test_admin_can_export_performance_report PASSED [ 79%]
unit_testing/test_platform_admin.py::test_platform_admin_endpoints_forbidden_for_student PASSED [ 80%]
unit_testing/test_platform_admin.py::test_admin_workshop_create_validation_error PASSED [ 81%]
unit_testing/test_student.py::test_student_auth_register_and_login PASSED [ 83%]
unit_testing/test_student.py::test_student_dashboard_and_analytics PASSED [ 84%]
unit_testing/test_student.py::test_student_workshops_and_enrollments PASSED [ 86%]
unit_testing/test_student.py::test_student_attempt_start_save_submit_flow PASSED [ 87%]
unit_testing/test_student.py::test_student_certificates_notifications_and_profile PASSED [ 88%]
unit_testing/test_student.py::test_student_forbidden_from_other_student_data PASSED [ 90%]
unit_testing/test_student.py::test_student_leaderboard_access_and_staff_only_guards PASSED [ 91%]
unit_testing/test_student.py::test_student_cannot_access_admin_or_institution_dashboards PASSED [ 93%]
unit_testing/test_student.py::test_student_cannot_view_educator_dashboard PASSED [ 94%]
unit_testing/test_student.py::test_student_invalid_certificate_verification_code PASSED [ 95%]
unit_testing/test_student.py::test_student_cannot_delete_workshop PASSED [ 97%]
unit_testing/test_student.py::test_student_cannot_grade_submission PASSED [ 98%]
unit_testing/test_student.py::test_student_assessment_submit_unknown_submission PASSED [100%]

============================== warnings summary ===============================
unit_testing/test_platform_admin.py::test_admin_approval_list_and_approve
  E:\IITM BS Diploma\BSc LEVEL\SE\Merging Try 2\backend\app\crud\crud_admin.py:51: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    req.resolved_at = datetime.utcnow()

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================= 72 passed, 1 warning in 25.82s ========================
```
