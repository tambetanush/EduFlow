from fastapi import APIRouter


from app.api.v1 import (
    ai_student_explanations,
    ai_reports,
    ai_scheduled_reports,
    ai_content_generator,
    support,
    analytics,
    approvals,
    assessments,
    auth,
    bulk,
    communication,
    certificates,
    dashboard,
    enrollments,
    fees,
    institutions,
    materials,
    modules,
    notifications,
    progress,
    payments,
    questions,
    salaries,
    sessions,
    submissions,
    tests,
    users,
    workshops,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(institutions.router)
api_router.include_router(workshops.router)
api_router.include_router(modules.router)
api_router.include_router(materials.router)
api_router.include_router(enrollments.router)
api_router.include_router(sessions.router)
api_router.include_router(assessments.router)
api_router.include_router(questions.router)
api_router.include_router(tests.router)
api_router.include_router(submissions.router)
api_router.include_router(certificates.router)
api_router.include_router(fees.router)
api_router.include_router(payments.router)
api_router.include_router(bulk.router)
api_router.include_router(communication.router)
api_router.include_router(analytics.router)
api_router.include_router(ai_reports.router)
api_router.include_router(ai_student_explanations.router)
api_router.include_router(ai_scheduled_reports.router)
api_router.include_router(support.router)
api_router.include_router(notifications.router)
api_router.include_router(progress.router)
api_router.include_router(dashboard.router)
api_router.include_router(ai_content_generator.router)

# Admin panel support
api_router.include_router(approvals.router)
api_router.include_router(salaries.router)
