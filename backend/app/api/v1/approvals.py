from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import PaginationParams, get_current_user, get_db, require_role
from app.crud import (
    delete_user,
    delete_workshop,
    get_user,
    get_workshop,
)
from app.crud.crud_admin import (
    create_approval_request,
    get_approval_request,
    list_approval_requests,
    resolve_approval_request,
)
from app.models import (
    ApprovalRequest,
    ApprovalRequestStatus,
    ApprovalRequestType,
    User,
    UserRole,
)
from app.schemas.base import Page
from app.schemas.misc import ApprovalRequestCreate, ApprovalRequestResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


@router.post(
    "/requests",
    response_model=ApprovalRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an approval request (staff only)",
)
async def create_request(
    payload: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(*_STAFF)),
) -> ApprovalRequestResponse:
    # Validate request_type.
    try:
        req_type = ApprovalRequestType(payload.request_type)
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid request_type")

    data = dict(payload.payload or {})

    # Minimal enforcement for institution-scoped staff.
    if current_user.role in (UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR):
        if req_type == ApprovalRequestType.DELETE_WORKSHOP:
            wid = str(data.get("workshop_id") or "")
            workshop = await get_workshop(db, wid)
            if not workshop or workshop.institution_id != current_user.institution_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        if req_type in (ApprovalRequestType.DELETE_EDUCATOR, ApprovalRequestType.DELETE_STUDENT):
            uid = str(data.get("user_id") or "")
            target = await get_user(db, uid)
            if not target or target.institution_id != current_user.institution_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    req = ApprovalRequest(
        request_type=req_type,
        payload=data,
        requested_by=current_user.id,
        status=ApprovalRequestStatus.PENDING,
    )
    created = await create_approval_request(db, req)
    return ApprovalRequestResponse.model_validate(created)


@router.get(
    "/requests",
    response_model=Page[ApprovalRequestResponse],
    summary="List approval requests (admin only)",
)
async def list_requests(
    page: PaginationParams = Depends(),
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> Page[ApprovalRequestResponse]:
    items, total = await list_approval_requests(db, offset=page.offset, limit=page.limit, status=status_filter)
    return Page(
        items=[ApprovalRequestResponse.model_validate(i) for i in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


async def _apply_request(db: AsyncSession, req: ApprovalRequest) -> None:
    data = dict(req.payload or {})
    if req.request_type == ApprovalRequestType.DELETE_WORKSHOP:
        wid = str(data.get("workshop_id") or "")
        workshop = await get_workshop(db, wid)
        if workshop:
            await delete_workshop(db, workshop)
    elif req.request_type in (ApprovalRequestType.DELETE_EDUCATOR, ApprovalRequestType.DELETE_STUDENT):
        uid = str(data.get("user_id") or "")
        user = await get_user(db, uid)
        if user:
            await delete_user(db, user)


@router.post(
    "/requests/{request_id}/approve",
    response_model=ApprovalRequestResponse,
    summary="Approve a request (admin only)",
)
async def approve(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> ApprovalRequestResponse:
    req = await get_approval_request(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

    if req.status != ApprovalRequestStatus.PENDING:
        return ApprovalRequestResponse.model_validate(req)

    await _apply_request(db, req)
    updated = await resolve_approval_request(db, req, status=ApprovalRequestStatus.APPROVED)
    return ApprovalRequestResponse.model_validate(updated)


@router.post(
    "/requests/{request_id}/reject",
    response_model=ApprovalRequestResponse,
    summary="Reject a request (admin only)",
)
async def reject(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
) -> ApprovalRequestResponse:
    req = await get_approval_request(db, request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found.")

    if req.status != ApprovalRequestStatus.PENDING:
        return ApprovalRequestResponse.model_validate(req)

    updated = await resolve_approval_request(db, req, status=ApprovalRequestStatus.REJECTED)
    return ApprovalRequestResponse.model_validate(updated)