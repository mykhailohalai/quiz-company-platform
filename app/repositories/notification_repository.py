from uuid import UUID

from sqlalchemy import func, select

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.notification_exceptions import NotificationNotFoundException
from app.models.notification import Notification, NotificationStatus
from app.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification, None]):
    model = Notification
    not_found_exception = NotificationNotFoundException
    already_exists_exception = Exception

    async def get_by_user_id(self, user_id: UUID) -> list[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.timestamp.desc())
        )
        return result.scalars().all()

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        notification = await self.get_by_id(notification_id)
        if notification.user_id != user_id:
            raise ForbiddenException()
        notification.status = NotificationStatus.READ
        await self.session.flush()
        return notification

    async def get_notifications_by_user(self, user_id: UUID, skip: int, limit: int) -> tuple[list[Notification], int]:
        total = await self.session.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id)
        )

        notifications = await self.session.execute(
            select(Notification).where(
                Notification.user_id == user_id
            ).offset(skip).limit(limit)
        )

        return notifications.scalars().all(), total
