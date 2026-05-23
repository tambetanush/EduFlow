from __future__ import annotations

from typing import Optional, Sequence, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models import Institution, User
from app.schemas.user import InstitutionCreate, InstitutionUpdate, UserCreate, UserUpdate


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role,
        institution_id=data.institution_id,
        phone=data.phone,
        bio=data.bio,
        department=data.department,
        parent_name=data.parent_name,
        parent_email=str(data.parent_email) if data.parent_email else None,
        institution_admin_name=data.institution_admin_name,
        institution_admin_address=data.institution_admin_address,
        institution_admin_code=data.institution_admin_code,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_users(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 100,
    institution_id: Optional[str] = None,
) -> Tuple[Sequence[User], int]:
    """Return (users, total_count). Optionally filter by institution."""
    q = select(User)
    if institution_id is not None:
        q = q.where(User.institution_id == institution_id)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def update_user(
    db: AsyncSession, user: User, data: UserUpdate
) -> User:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.flush()


# ---------------------------------------------------------------------------
# Institution CRUD
# ---------------------------------------------------------------------------


async def create_institution(
    db: AsyncSession, data: InstitutionCreate
) -> Institution:
    institution = Institution(**data.model_dump())
    db.add(institution)
    await db.flush()
    await db.refresh(institution)
    return institution


async def get_institution(
    db: AsyncSession, institution_id: str
) -> Optional[Institution]:
    return await db.get(Institution, institution_id)


async def get_institutions(
    db: AsyncSession, *, offset: int = 0, limit: int = 100
) -> Tuple[Sequence[Institution], int]:
    """Return (institutions, total_count)."""
    q = select(Institution)
    total_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total: int = total_result.scalar_one()
    items_result = await db.execute(q.offset(offset).limit(limit))
    return items_result.scalars().all(), total


async def update_institution(
    db: AsyncSession, institution: Institution, data: InstitutionUpdate
) -> Institution:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(institution, field, value)
    await db.flush()
    await db.refresh(institution)
    return institution


async def delete_institution(
    db: AsyncSession, institution: Institution
) -> None:
    await db.delete(institution)
    await db.flush()
