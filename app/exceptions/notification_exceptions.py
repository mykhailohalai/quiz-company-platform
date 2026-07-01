from uuid import UUID


class NotificationNotFoundException(Exception):
    def __init__(self, notification_id: UUID):
        super().__init__(f"Notification with id {notification_id} was not found.")
