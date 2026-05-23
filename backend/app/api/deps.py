from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db import AsyncSessionLocal
from app.models import Enrollment, User, UserRole, Workshop

# OAuth2 bearer scheme – points at the login endpoint (update path when created)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ---------------------------------------------------------------------------
# Database session dependency
# ---------------------------------------------------------------------------


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session; commits on success, rolls back on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Current-user dependency
# ---------------------------------------------------------------------------


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode JWT and return the corresponding User ORM object.

    Raises 401 if the token is invalid/expired or the user no longer exists.
    """
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")  # type: ignore[assignment]
        if user_id is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exc
    return user


# ---------------------------------------------------------------------------
# RBAC checker factory
# ---------------------------------------------------------------------------


def require_role(*allowed_roles: UserRole) -> Callable:
    """Return a FastAPI dependency that enforces role-based access.

    Usage::

        @router.post("/admin-only")
        async def admin_route(
            current_user: User = Depends(require_role(UserRole.ADMIN)),
        ):
            ...

    Raises 403 if the authenticated user's role is not in ``allowed_roles``.
    """

    async def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. Required role(s): "
                    f"{[r.value for r in allowed_roles]}"
                ),
            )
        return current_user

    return _check


# ---------------------------------------------------------------------------
# PaginationParams — injectable query-param bundle
# ---------------------------------------------------------------------------


@dataclass
class PaginationParams:
    """Standardised pagination parameters for all list endpoints.

    Usage::

        @router.get("/items")
        async def list_items(page: PaginationParams = Depends()):
            items, total = await crud.get_items(db, offset=page.offset, limit=page.limit)
            return Page(items=items, total=total, offset=page.offset, limit=page.limit)
    """

    offset: int = Query(default=0, ge=0, description="Number of records to skip")
    limit: int = Query(default=50, ge=1, le=1000, description="Maximum records to return")


# ---------------------------------------------------------------------------
# Institution-level access helpers
# ---------------------------------------------------------------------------


async def get_institution_admin_institution_id(
    current_user: User = Depends(get_current_user),
) -> Optional[str]:
    """Return the caller's institution_id if they are an INSTITUTION_ADMIN.

    - ``ADMIN`` → returns ``None`` (no restriction; see all).
    - ``INSTITUTION_ADMIN`` → returns their own ``institution_id``.
    - Any other role → raises 403.
    """
    if current_user.role == UserRole.ADMIN:
        return None
    if current_user.role == UserRole.INSTITUTION_ADMIN:
        if not current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Institution admin is not linked to any institution.",
            )
        return current_user.institution_id
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied. Admins and institution admins only.",
    )


def verify_workshop_access(raise_on_mismatch: bool = True) -> Callable:
    """Factory: returns a dependency that checks the caller can access a workshop.

    Rules:
    - ``ADMIN`` → always allowed.
    - ``INSTITUTION_ADMIN`` / ``EDUCATOR`` → workshop's ``institution_id`` must
      match the caller's ``institution_id``.
    - ``STUDENT`` → raises 403 (use ``verify_student_self`` for student data).

    Usage::

        @router.get("/{workshop_id}")
        async def get_workshop(
            workshop_id: str,
            db: AsyncSession = Depends(get_db),
            current_user: User = Depends(verify_workshop_access()),
        ):
            ...
    """

    async def _check(
        workshop_id: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role == UserRole.ADMIN:
            return current_user

        if current_user.role == UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot perform this action directly on workshops.",
            )

        # INSTITUTION_ADMIN or EDUCATOR — must belong to the same institution
        if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
            workshop = await db.get(Workshop, workshop_id)
            if workshop is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workshop not found.",
                )
            if workshop.institution_id != current_user.institution_id:
                if raise_on_mismatch:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You do not have access to this workshop.",
                    )
        return current_user

    return _check


async def ensure_user_can_read_assessments_for_workshop(
    db: AsyncSession,
    current_user: User,
    workshop_id: str,
) -> None:
    """Enforce workshop boundary for assessment/submission reads (admin: any; staff: same institution; student: enrolled)."""

    if current_user.role == UserRole.ADMIN:
        return

    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        workshop = await db.get(Workshop, workshop_id)
        if workshop is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workshop not found.",
            )
        if workshop.institution_id != current_user.institution_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )
        return

    if current_user.role == UserRole.STUDENT:
        row = (
            await db.execute(
                select(Enrollment.id).where(
                    Enrollment.student_id == current_user.id,
                    Enrollment.workshop_id == workshop_id,
                ).limit(1)
            )
        ).scalar_one_or_none()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied.",
    )


def verify_student_self(param_name: str = "student_id") -> Callable:
    """Factory: returns a dependency that ensures a STUDENT only sees their own data.

    ``ADMIN``, ``INSTITUTION_ADMIN``, and ``EDUCATOR`` always pass through.

    Usage::

        @router.get("/student/{student_id}")
        async def list_for_student(
            student_id: str,
            _: User = Depends(verify_student_self("student_id")),
        ):
            ...
    """

    async def _check(
        student_id: str,
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role == UserRole.STUDENT:
            if current_user.id != student_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Students may only access their own records.",
                )
        return current_user

    return _check
