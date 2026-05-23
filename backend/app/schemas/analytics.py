from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ScoreTrendPoint(BaseModel):
    assessment_id: Optional[str] = None
    score: Optional[float] = None
    percentage: Optional[float] = None
    pass_fail: Optional[bool] = None
    submitted_at: Optional[str] = None


class StudentAssessmentAnalytics(BaseModel):
    total_submissions: int = 0
    avg_score: float = 0.0
    avg_percentage: float = 0.0
    passed: int = 0
    failed: int = 0
    score_trend: list[ScoreTrendPoint] = []


class StudentAttendanceAnalytics(BaseModel):
    total_sessions: int = 0
    present: int = 0
    late: int = 0
    absent: int = 0
    attendance_percentage: float = 0.0


class StudentAnalyticsResponse(BaseModel):
    student_id: str
    enrolled_workshops: int = 0
    assessment: StudentAssessmentAnalytics = StudentAssessmentAnalytics()
    attendance: StudentAttendanceAnalytics = StudentAttendanceAnalytics()


class StudentAttendanceRecord(BaseModel):
    attendance_id: str
    session_id: Optional[str] = None
    session_title: Optional[str] = None
    start_time: Optional[str] = None
    workshop_id: Optional[str] = None
    workshop_title: Optional[str] = None
    status: Optional[str] = None


class StudentAttendanceResponse(BaseModel):
    student_id: str
    total_sessions: int = 0
    present: int = 0
    late: int = 0
    absent: int = 0
    attendance_percentage: float = 0.0
    records: list[StudentAttendanceRecord] = []


class WorkshopEnrollmentAnalytics(BaseModel):
    total_enrolled: int = 0
    completed: int = 0
    dropped: int = 0
    active: int = 0


class WorkshopAssessmentAnalytics(BaseModel):
    total_submissions: int = 0
    avg_score: float = 0.0
    avg_percentage: float = 0.0
    pass_rate_percentage: float = 0.0


class WorkshopAttendanceAnalytics(BaseModel):
    total_attendance_records: int = 0
    avg_attendance_percentage: float = 0.0


class WorkshopAnalyticsResponse(BaseModel):
    workshop_id: str
    enrollment: WorkshopEnrollmentAnalytics = WorkshopEnrollmentAnalytics()
    assessment: WorkshopAssessmentAnalytics = WorkshopAssessmentAnalytics()
    attendance: WorkshopAttendanceAnalytics = WorkshopAttendanceAnalytics()


class LeaderboardEntry(BaseModel):
    rank: int
    student_id: str
    student_name: str
    average_percentage: float = 0.0
    attempts: int = 0
    passed: int = 0


class AssessmentLeaderboardResponse(BaseModel):
    assessment_id: str
    entries: list[LeaderboardEntry] = []


class WorkshopLeaderboardResponse(BaseModel):
    workshop_id: str
    entries: list[LeaderboardEntry] = []


class LeaderboardAttemptQuestion(BaseModel):
    question_id: str
    question_text: str
    selected_option_texts: list[str] = []
    correct_option_texts: list[str] = []
    earned_marks: int = 0
    max_marks: int = 0
    is_correct: bool = False


class LeaderboardAttemptDetail(BaseModel):
    submission_id: str
    submitted_at: Optional[str] = None
    score: float = 0
    percentage: float = 0
    pass_fail: bool = False
    questions: list[LeaderboardAttemptQuestion] = []


class LeaderboardStudentDrilldownResponse(BaseModel):
    context_type: str
    context_id: str
    student_id: str
    student_name: str
    attempts: list[LeaderboardAttemptDetail] = []
    average_percentage: float = 0.0
    total_attempts: int = 0


class InstitutionStudentRosterItem(BaseModel):
    id: str
    name: str
    email: str
    workshop: str
    status: str


class InstitutionStudentRosterResponse(BaseModel):
    items: list[InstitutionStudentRosterItem] = []
    total: int = 0


class InstitutionAttendanceRow(BaseModel):
    student: str
    mon: bool = False
    tue: bool = False
    wed: bool = False
    thu: bool = False
    fri: bool = False


class InstitutionAttendanceReportResponse(BaseModel):
    rows: list[InstitutionAttendanceRow] = []
    total: int = 0


class DashboardAlertItem(BaseModel):
    id: str
    text: str
    level: str = "info"


class DashboardActivityItem(BaseModel):
    id: str
    text: str
    time: str
    type: str = "general"


class DashboardSeriesPoint(BaseModel):
    label: str
    value: float


class InstitutionDashboardAggregateResponse(BaseModel):
    kpis: dict[str, float | int | str]
    alerts: list[DashboardAlertItem] = []
    activity_feed: list[DashboardActivityItem] = []
    attendance_trend: list[DashboardSeriesPoint] = []
    enrollment_trend: list[DashboardSeriesPoint] = []
    report_cards: dict[str, float | int | str]


class AdminDashboardInsightsResponse(BaseModel):
    weekly_activity: list[DashboardSeriesPoint] = []
    demographics: list[dict]
    activity_feed: list[DashboardActivityItem] = []


class ExportFileResponse(BaseModel):
    file_name: str
    file_type: str
    download_url: str


class InstitutionStudentBulkActionRequest(BaseModel):
    student_ids: list[str]
    action: str = "set_inactive"


class InstitutionStudentBulkActionResponse(BaseModel):
    requested_students: int
    affected_students: int
    updated_enrollments: int
    message: str
