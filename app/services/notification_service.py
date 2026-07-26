import logging
from datetime import datetime
from uuid import UUID

from app.models.notification import Notification, NotificationStatus
from app.utils.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def send_notification(self, company_id: UUID, message: str) -> None:
        async with self.uow:
            members = await self.uow.company_members.get_all_members_by_company(company_id)
            for member in members:
                notification = Notification(
                    user_id=member.user_id,
                    message=message,
                    status=NotificationStatus.UNREAD,
                    timestamp=datetime.utcnow(),
                )
                await self.uow.notifications.create(notification)
            await self.uow.commit()
            logger.info("Sent %d notifications for company %s", len(members), company_id)

    async def get_notifications_by_user(self, user_id: UUID, skip: int, limit: int) -> tuple[list[Notification], int]:
        async with self.uow:
            return await self.uow.notifications.get_notifications_by_user(user_id, skip, limit)

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        async with self.uow:
            notification = await self.uow.notifications.mark_as_read(notification_id, user_id)
            await self.uow.commit()
            logger.info("Notification %s marked as read by user %s", notification_id, user_id)
            return notification
