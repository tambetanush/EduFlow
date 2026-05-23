from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    PaginationParams,
    get_current_user,
    get_db,
    require_role,
)
from app.crud import get_user, get_users, update_user
from app.models import User, UserRole, Enrollment, Workshop, EnrollmentStatus, Submission, Assessment
from app.schemas.base import Page
from app.schemas.user import (
    UserResponse, 
    UserUpdate, 
    PublicStudentProfileResponse, 
    PublicEnrollmentInfo, 
    PublicSubmissionInfo, 
    PublicStudentStats, 
    PublicWorkshopInfo, 
    PublicAssessmentInfo, 
    PublicUserResponse
)
from app.services.storage import delete_upload, save_upload
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["users"])


# ---------------------------------------------------------------------------
# GET /users/   — admin / institution_admin only, institution-filtered
# ---------------------------------------------------------------------------


@router.get(
    "/",
    response_model=Page[UserResponse],
    summary="List all users (admin only; institution_admin sees their institution only)",
)
async def list_users(
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)
    ),
) -> Page[UserResponse]:
    # Institution admins are automatically scoped to their institution
    inst_filter = (
        current_user.institution_id
        if current_user.role == UserRole.INSTITUTION_ADMIN
        else None
    )
    users, total = await get_users(
        db, offset=page.offset, limit=page.limit, institution_id=inst_filter
    )
    return Page(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------


@router.get("/me", response_model=UserResponse, summary="Current authenticated user")
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)


# ---------------------------------------------------------------------------
# GET /users/{user_id}
# ---------------------------------------------------------------------------


@router.get("/{user_id}", response_model=UserResponse, summary="Fetch user by ID")
async def get_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    # Students can only see themselves
    if current_user.role == UserRole.STUDENT:
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    # Institution admins and educators cannot view users from other institutions
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        if user.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# PATCH /users/{user_id}
# ---------------------------------------------------------------------------


@router.patch("/{user_id}", response_model=UserResponse, summary="Update user profile")
async def patch_user(
    user_id: str,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    # Users can only update themselves; admins/institution_admins can update students in their institution
    if current_user.role not in (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN):
        if current_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    
    # Institution admins can only update students in their institution
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        user = await get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
        if user.role != UserRole.STUDENT or user.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
    
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    updated = await update_user(db, user, payload)
    return UserResponse.model_validate(updated)


@router.post(
    "/{user_id}/profile-photo",
    response_model=UserResponse,
    summary="Upload and persist profile photo for a user",
)
async def upload_profile_photo(
    user_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    if current_user.role not in (UserRole.ADMIN,) and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    filename = file.filename or "avatar.jpg"
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    relative_path = await save_upload(content, filename, subfolder="avatars")
    if user.profile_photo:
        delete_upload(user.profile_photo)

    updated = await update_user(db, user, UserUpdate(profile_photo=relative_path))
    return UserResponse.model_validate(updated)


@router.patch(
    "/{user_id}/salary",
    response_model=UserResponse,
    summary="Update educator salary (admin or institution admin)",
)
async def update_educator_salary(
    user_id: str,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.INSTITUTION_ADMIN)),
) -> UserResponse:
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    if user.role != UserRole.EDUCATOR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not an educator.")
    
    # Institution admins can only update educators from their institution
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if user.institution_id != current_user.institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update salary for educator from different institution.")
    
    salary_amount = payload.get("salary_amount", 0)
    salary_type = payload.get("salary_type", "monthly")
    
    user.salary_amount = salary_amount
    user.salary_type = salary_type
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


# ---------------------------------------------------------------------------
# GET /users/{user_id}/public-profile
# ---------------------------------------------------------------------------


@router.get(
    "/{user_id}/public-profile",
    response_model=PublicStudentProfileResponse,
    summary="Fetch public student profile for parents (unauthenticated)",
)
async def get_public_student_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> PublicStudentProfileResponse:
    # 1. Fetch user (must be a student)
    user = await get_user(db, user_id)
    if not user or user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found."
        )

    # 2. Fetch enrollments & workshops
    enroll_q = (
        select(Enrollment, Workshop)
        .join(Workshop, Enrollment.workshop_id == Workshop.id)
        .where(Enrollment.student_id == user_id)
    )
    enroll_res = await db.execute(enroll_q)
    enrollments_data = enroll_res.all()

    active_enrollments = []
    completed_enrollments = []
    for enroll, workshop in enrollments_data:
        info = PublicEnrollmentInfo(
            workshop=PublicWorkshopInfo(
                id=workshop.id,
                title=workshop.title,
                start_date=workshop.start_date,
                end_date=workshop.end_date,
            ),
            status=enroll.status,
            enrolled_at=enroll.enrolled_at,
        )
        if enroll.status == EnrollmentStatus.COMPLETED:
            completed_enrollments.append(info)
        else:
            active_enrollments.append(info)

    # 3. Fetch submissions & assessments
    sub_q = (
        select(Submission, Assessment)
        .join(Assessment, Submission.assessment_id == Assessment.id)
        .where(Submission.student_id == user_id)
    )
    sub_res = await db.execute(sub_q)
    submissions_data = sub_res.all()

    public_submissions = []
    for sub, assessment in submissions_data:
        public_submissions.append(
            PublicSubmissionInfo(
                assessment=PublicAssessmentInfo(
                    id=assessment.id,
                    title=assessment.title,
                    total_marks=assessment.total_marks,
                    pass_mark=assessment.pass_mark,
                ),
                score=sub.score,
                percentage=sub.percentage,
                pass_fail=sub.pass_fail,
                submitted_at=sub.submitted_at,
            )
        )

    # 4. Stats
    total_w = len(enrollments_data)
    completed_w = len(completed_enrollments)
    rate = (completed_w / total_w * 100.0) if total_w > 0 else 0.0

    return PublicStudentProfileResponse(
        student=PublicUserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            profile_photo=user.profile_photo,
            bio=user.bio,
            department=user.department,
            created_at=user.created_at,
        ),
        active_enrollments=active_enrollments,
        completed_enrollments=completed_enrollments,
        submissions=public_submissions,
        stats=PublicStudentStats(
            total_workshops=total_w,
            completed_workshops=completed_w,
            completion_rate=rate,
        ),
    )
