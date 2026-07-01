from uuid import UUID, uuid4

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.notification_exceptions import NotificationNotFoundException
from app.models.notification import Notification, NotificationStatus


class FakeNotificationRepository:
    def __init__(self, notifications=None):
        self.notifications = {n.id: n for n in (notifications or [])}

    async def create(self, notification: Notification) -> Notification:
        if notification.id is None:
            notification.id = uuid4()
        self.notifications[notification.id] = notification
        return notification

    async def get_by_id(self, notification_id: UUID) -> Notification:
        notification = self.notifications.get(notification_id)
        if notification is None:
            raise NotificationNotFoundException(notification_id)
        return notification

    async def get_notifications_by_user(
        self, user_id: UUID, skip: int, limit: int
    ) -> tuple[list[Notification], int]:
        results = [n for n in self.notifications.values() if n.user_id == user_id]
        results.sort(key=lambda n: n.timestamp, reverse=True)
        total = len(results)
        return results[skip : skip + limit], total

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        notification = await self.get_by_id(notification_id)
        if notification.user_id != user_id:
            raise ForbiddenException()
        notification.status = NotificationStatus.READ
        return notification
