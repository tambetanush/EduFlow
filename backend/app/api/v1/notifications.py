from __future__ import annotations

from app.api.deps import PaginationParams, get_current_user, get_db, require_role
from app.crud.crud_misc import (
    create_notification,
    delete_notification,
    get_notification,
    get_notifications_by_user,
    update_notification,
)
from app.models import NotificationStatus, User, UserRole
from app.schemas.base import Page
from app.schemas.misc import (
    NotificationBulkCreate,
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/notifications", tags=["notifications"])

_STAFF = (UserRole.ADMIN, UserRole.INSTITUTION_ADMIN, UserRole.EDUCATOR)


def _to_response(notification) -> NotificationResponse:
    return NotificationResponse(
        id=notification.id,
        user_id=notification.user_id,
        title=getattr(notification, "title", None) or "Notification",
        message=notification.message,
        status=notification.status,
        notification_type=notification.notification_type,
        created_at=notification.created_at,
    )


@router.post(
    "/send",
    response_model=list[NotificationResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Send a notification to multiple users concurrently (staff only)",
)
async def send_notification(
    payload: NotificationBulkCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(*_STAFF)),
) -> list[NotificationResponse]:
    results: list[NotificationResponse] = []

    for uid in set(payload.user_ids):
        data = NotificationCreate(
            user_id=uid,
            title=payload.title,
            message=payload.message,
            notification_type=payload.notification_type,
        )
        notif = await create_notification(db, data)
        results.append(_to_response(notif))

    return results


@router.get(
    "",
    response_model=list[NotificationResponse],
    summary="List notifications for the authenticated user",
)
async def list_current_user_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    items, _ = await get_notifications_by_user(db, current_user.id, offset=0, limit=50)
    return [_to_response(item) for item in items]


@router.get(
    "/{user_id}",
    response_model=Page[NotificationResponse],
    summary="List all notifications for a user (newest first)",
)
async def list_notifications(
    user_id: str,
    page: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[NotificationResponse]:
    if current_user.role == UserRole.STUDENT and current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    items, total = await get_notifications_by_user(
        db,
        user_id,
        offset=page.offset,
        limit=page.limit,
    )
    return Page(
        items=[_to_response(item) for item in items],
        total=total,
        offset=page.offset,
        limit=page.limit,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a notification as read",
)
async def mark_read(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationResponse:
    notif = await get_notification(db, notification_id)
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    if notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    updated = await update_notification(
        db,
        notif,
        NotificationUpdate(status=NotificationStatus.READ),
    )
    return _to_response(updated)


@router.patch(
    "/read-all",
    response_model=list[NotificationResponse],
    summary="Mark all notifications as read",
)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    items, _ = await get_notifications_by_user(db, current_user.id, offset=0, limit=500)
    updated_items: list[NotificationResponse] = []
    for item in items:
        if item.status != NotificationStatus.READ:
            item = await update_notification(
                db,
                item,
                NotificationUpdate(status=NotificationStatus.READ),
            )
        updated_items.append(_to_response(item))
    return updated_items


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Delete a notification",
)
async def delete_one(
    notification_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    notif = await get_notification(db, notification_id)
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")

    if notif.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    await delete_notification(db, notif)
