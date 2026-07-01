from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationStatus


class NotificationResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    message: str
    status: NotificationStatus
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationUpdateSchema(BaseModel):
    status: NotificationStatus


class PaginatedNotificationResponseSchema(BaseModel):
    notifications: list[NotificationResponseSchema]
    total: int
    skip: int
    limit: int
    has_more: bool
