import asyncio
import os
import sys

# Add backend to sys.path
sys.path.append(os.getcwd())

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models import User, Enrollment, Workshop, Assessment, Submission, EnrollmentStatus
from app.schemas.user import PublicStudentProfileResponse

# Mock DATABASE_URL if needed
DATABASE_URL = "sqlite+aiosqlite:///./eduflow.db"

async def verify_logic():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    student_id = "995d1b3f-8db1-4f77-ae8d-cff538d57201"
    
    async with async_session() as db:
        # Get user
        result = await db.execute(select(User).where(User.id == student_id))
        user = result.scalars().first()
        
        if not user:
            print("Student not found")
            return

        print(f"Verifying profile for {user.name} ({user.email})")

        # Active enrollments
        result = await db.execute(
            select(Enrollment, Workshop)
            .join(Workshop, Enrollment.workshop_id == Workshop.id)
            .where(Enrollment.student_id == student_id)
            .where(Enrollment.status != EnrollmentStatus.COMPLETED)
        )
        active_enrollments = result.all()
        print(f"Active Enrollments: {len(active_enrollments)}")

        # Completed enrollments
        result = await db.execute(
            select(Enrollment, Workshop)
            .join(Workshop, Enrollment.workshop_id == Workshop.id)
            .where(Enrollment.student_id == student_id)
            .where(Enrollment.status == EnrollmentStatus.COMPLETED)
        )
        completed_enrollments = result.all()
        print(f"Completed Enrollments: {len(completed_enrollments)}")

        # Submissions
        result = await db.execute(
            select(Submission, Assessment)
            .join(Assessment, Submission.assessment_id == Assessment.id)
            .where(Submission.student_id == student_id)
            .order_by(Submission.submitted_at.desc())
        )
        submissions = result.all()
        print(f"Submissions: {len(submissions)}")

        # Stats
        total_workshops = len(active_enrollments) + len(completed_enrollments)
        completed_workshops = len(completed_enrollments)
        completion_rate = (completed_workshops / total_workshops * 100) if total_workshops > 0 else 0
        
        print(f"Stats: Total={total_workshops}, Completed={completed_workshops}, Rate={completion_rate:.2f}%")

        # Validate with Schema
        response_data = {
            "student": {
                "id": user.id,
                "name": user.name,
                "role": user.role,
                "profile_photo": user.profile_photo,
                "bio": user.bio,
                "department": user.department,
                "created_at": user.created_at.isoformat() if user.created_at else None,
            },
            "active_enrollments": [
                {
                    "workshop": {"id": w.id, "title": w.name, "start_date": w.start_date.isoformat() if w.start_date else None, "end_date": w.end_date.isoformat() if w.end_date else None},
                    "status": e.status,
                    "enrolled_at": e.enrolled_at.isoformat() if e.enrolled_at else None,
                }
                for e, w in active_enrollments
            ],
            "completed_enrollments": [
                {
                    "workshop": {"id": w.id, "title": w.name, "start_date": w.start_date.isoformat() if w.start_date else None, "end_date": w.end_date.isoformat() if w.end_date else None},
                    "status": e.status,
                    "enrolled_at": e.enrolled_at.isoformat() if e.enrolled_at else None,
                }
                for e, w in completed_enrollments
            ],
            "submissions": [
                {
                    "assessment": {"id": a.id, "title": a.title, "total_marks": a.total_marks, "pass_mark": a.pass_mark},
                    "score": s.score,
                    "percentage": s.percentage,
                    "pass_fail": s.pass_fail,
                    "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None,
                }
                for s, a in submissions
            ],
            "stats": {
                "total_workshops": total_workshops,
                "completed_workshops": completed_workshops,
                "completion_rate": completion_rate,
            },
        }
        
        # This will raise an error if the model doesn't match the data
        public_profile = PublicStudentProfileResponse(**response_data)
        print("Schema validation PASSED")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_logic())
