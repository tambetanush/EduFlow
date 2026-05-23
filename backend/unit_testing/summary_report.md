# EduFlow Frontend ↔ Backend Integration Audit (Current Snapshot)

## Scope
- Date: 2026-03-27
- Repo snapshot scanned: current `frontend/src/pages/**` files only
- Backend tests added under `backend/unit_testing`

## Current Frontend Pages Discovered and Integration Status

| Page | Status | Backend Integration Notes |
|---|---|---|
| `LandingPage.tsx` | not integrated | Marketing/static page, no API calls |
| `Login.tsx` | fully integrated | Uses `POST /api/v1/auth/login` and `GET /api/v1/users/me` (via auth hook) |
| `SignUp.tsx` | fully integrated | Uses `POST /api/v1/auth/register` |
| `NotFound.tsx` | not integrated | Static 404 page |
| `assessments/AssessmentAttempt.tsx` | fully integrated | Uses `POST /api/v1/tests/{assessment_id}/start`, `POST /api/v1/submissions/{submission_id}/answers`, `POST /api/v1/tests/{assessment_id}/submit` |
| `assessments/Assessments.tsx` | partially integrated | Reads live assessments, but create/edit/questions/leaderboard still local/mock |
| `assessments/Results.tsx` | partially integrated | Uses backend result payload, but leaderboard/feedback is local-only |
| `certificates/Certificates.tsx` | partially integrated | Live fetch/generate wired; recommend/download actions are UI-only |
| `certificates/VerifyCertificate.tsx` | fully integrated | Uses `GET /api/v1/certificates/verify/{verification_code}` |
| `dashboard/AdminDashboard.tsx` | partially integrated | Live stats + workshop CRUD, but chart/activity/demographic sections are fallback arrays |
| `dashboard/InstitutionDashboard.tsx` | partially integrated | Workshop list is live; student/attendance/reports panes are static arrays |
| `dashboard/EducatorDashboard.tsx` | partially integrated | Live dashboard stats/workshops; activity chart/quick-actions are UI-local |
| `dashboard/StudentDashboard.tsx` | partially integrated | Live workshops/enrollments/learning/analytics; progress chart fallback used when analytics trend missing |
| `manage/ApprovalPanel.tsx` | fully integrated | Uses approvals APIs end-to-end |
| `manage/EducatorManagement.tsx` | partially integrated | Live user/salary/approval flows; department/type derivations are synthetic |
| `manage/InstituteManagement.tsx` | fully integrated | Uses institutions/users/workshops APIs for computed table metrics |
| `manage/SalaryManagement.tsx` | fully integrated | Uses salary/users/institutions APIs |
| `manage/StudentManagement.tsx` | partially integrated | Live users/enrollments/workshops/approval-request; parent email flow is UI-only |
| `materials/Materials.tsx` | partially integrated | Live material listing; upload/delete/download actions are local/simulated |
| `notifications/Notifications.tsx` | partially integrated | Live list fetch; mark-read/delete/email are local UI mutations |
| `profile/ProfilePage.tsx` | partially integrated | Live profile update/institution fetch; avatar upload and several profile fields are local-only |
| `reports/PerformanceReports.tsx` | partially integrated | Uses live workshop/student analytics; still sampled/local report widgets |
| `submissions/Submissions.tsx` | partially integrated | Live submissions list; grading/question-breakdown remains mock/local |
| `workshops/WorkshopsList.tsx` | partially integrated | Live list + admin CRUD; leaderboard is mock, institution-admin delete flow is UI-request only |
| `workshops/WorkshopDetails.tsx` | partially integrated | Live workshop/modules/assessments; educator profile block is mock |

## Pages Mentioned Previously but Missing in This Snapshot
- `ArchivePage.tsx` (not present)
- `BulkOperationsPage.tsx` (not present)
- `ReportsPage.tsx` (not present)
- `Index.tsx` (not present as a page entry here)
- `educator/EducatorReportsPage.tsx` (not present)
- `educator/EducatorStudentsPage.tsx` (not present)
- `educator/EducatorAttendancePage.tsx` (not present)
- `educator/EducatorCommunicationPage.tsx` (not present)

## Backend Unit Tests Added
- `backend/unit_testing/test_platform_admin.py`
- `backend/unit_testing/test_institutional_admin.py`
- `backend/unit_testing/test_educator.py`
- `backend/unit_testing/test_student.py`

## Backend API Endpoints Tested (Checklist)

### Platform admin tests
- [x] `GET /api/v1/dashboard/admin`
- [x] `GET /api/v1/users/`
- [x] `GET /api/v1/institutions/`
- [x] `POST /api/v1/workshops/`
- [x] `PATCH /api/v1/workshops/{workshop_id}`
- [x] `DELETE /api/v1/workshops/{workshop_id}`
- [x] `GET /api/v1/approvals/requests`
- [x] `POST /api/v1/approvals/requests/{request_id}/approve`
- [x] `POST /api/v1/salaries/pay`
- [x] `GET /api/v1/salaries/`

### Institutional admin tests
- [x] `GET /api/v1/dashboard/educator`
- [x] `GET /api/v1/workshops/` (institution-scoped)
- [x] `POST /api/v1/workshops/` (institution-scoped create)
- [x] `PATCH /api/v1/workshops/{workshop_id}` (forbidden cross-institution case)
- [x] `GET /api/v1/users/` (institution-scoped)
- [x] `GET /api/v1/enrollments/student/{student_id}`
- [x] `POST /api/v1/approvals/requests`

### Educator tests
- [x] `GET /api/v1/dashboard/educator`
- [x] `GET /api/v1/workshops/` (institution-scoped)
- [x] `GET /api/v1/assessments/workshop/{workshop_id}`
- [x] `GET /api/v1/submissions/assessment/{assessment_id}`
- [x] `GET /api/v1/analytics/workshop/{workshop_id}`
- [x] `GET /api/v1/notifications/{user_id}`
- [x] forbidden checks on `GET /api/v1/dashboard/admin` and `DELETE /api/v1/workshops/{workshop_id}`

### Student tests
- [x] `POST /api/v1/auth/register`
- [x] `POST /api/v1/auth/login`
- [x] `GET /api/v1/dashboard/student/{student_id}`
- [x] `GET /api/v1/analytics/student/{student_id}`
- [x] `GET /api/v1/workshops/`
- [x] `GET /api/v1/enrollments/student/{student_id}`
- [x] `POST /api/v1/enrollments/` (forbidden other-student case)
- [x] `POST /api/v1/tests/{assessment_id}/start`
- [x] `POST /api/v1/submissions/{submission_id}/answers`
- [x] `POST /api/v1/tests/{assessment_id}/submit` (success + re-submit conflict)
- [x] `GET /api/v1/certificates/student/{student_id}`
- [x] `GET /api/v1/certificates/verify/{verification_code}`
- [x] `GET /api/v1/notifications/{user_id}`
- [x] `GET /api/v1/users/me`
- [x] forbidden checks on `GET /api/v1/users/{other_student}` and `GET /api/v1/dashboard/student/{other_student}`

## Test Run Result
- Command: `.\.venv\Scripts\python -m pytest -p no:cacheprovider unit_testing/test_platform_admin.py unit_testing/test_institutional_admin.py unit_testing/test_educator.py unit_testing/test_student.py`
- Result: **24 passed**, 0 failed

## Backend Endpoints Referenced by Frontend but Missing/Mismatched
- No hard 404/route-name mismatches were found for endpoints currently called via `frontend/src/services/api.ts`.
- Integration gaps are mostly due to **frontend still using local/mock UI flows** even though backend routes exist.

## Frontend Paths Still Relying on Mock/Fallback Data
- `assessments/Assessments.tsx` (leaderboard + create/edit/question builder local)
- `assessments/Results.tsx` (leaderboard local)
- `dashboard/AdminDashboard.tsx` (fallback chart/feed blocks)
- `dashboard/InstitutionDashboard.tsx` (alerts/activity/student/attendance/reports local arrays)
- `dashboard/EducatorDashboard.tsx` (chart/quick-action content local)
- `materials/Materials.tsx` (upload/delete/download simulated)
- `notifications/Notifications.tsx` (mark-read/delete/email not persisted)
- `profile/ProfilePage.tsx` (avatar upload + extra profile fields local)
- `reports/PerformanceReports.tsx` (sampled/report widgets still mixed)
- `submissions/Submissions.tsx` (question breakdown + grading action local)
- `workshops/WorkshopDetails.tsx` (educator block mock)
- `workshops/WorkshopsList.tsx` (leaderboard mock; institution delete request not persisted)

## Exact Missing Backend Contracts (for Fully Live UI in Remaining Gaps)
- Dedicated leaderboard endpoints for assessment/workshop/result leaderboards (currently mocked in multiple pages).
- Institution dashboard aggregate/reporting contracts for alerts/activity feed, attendance grid/trends, and report KPI cards used in current UI panels.
- Communication/email dispatch contract for parent messaging flows used in `StudentManagement` and `Notifications`.
- Staff-oriented submission review/breakdown contract matching the detailed question breakdown UI in `Submissions`.

## Final Conclusion
- The current frontend is **not fully integrated** end-to-end yet.
- Core API connectivity exists for many pages and role workflows, and role-based backend unit tests now cover those live endpoints.
- Remaining work is primarily to replace local/mock UI behaviors with backend-driven flows where contracts are still absent or not yet wired.
