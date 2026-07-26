from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from app.dependencies import get_current_user_dep, get_notification_service
from app.models.user import User
from app.schemas.notification import NotificationResponseSchema, PaginatedNotificationResponseSchema
from app.services.notification_service import NotificationService
notification_router = APIRouter()


@notification_router.get(
    "/users/me/notifications",
    response_model=PaginatedNotificationResponseSchema,
    status_code=status.HTTP_200_OK
)
async def get_user_notifications(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user_dep),
    notification_service: NotificationService = Depends(get_notification_service),
):
    notifications, total = await notification_service.get_notifications_by_user(current_user.id, skip, limit)

    return PaginatedNotificationResponseSchema(
        notifications=notifications,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@notification_router.patch(
    "/notifications/{notification_id}",
    response_model=NotificationResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    notification_service: NotificationService = Depends(get_notification_service),
):
    return await notification_service.mark_as_read(notification_id, current_user.id)
