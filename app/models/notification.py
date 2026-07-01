from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, String, Enum as SAEnum, Uuid    
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.core.database import Base

class NotificationStatus(Enum):
    UNREAD = "unread"
    READ = "read"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        SAEnum(NotificationStatus), nullable=False, default=NotificationStatus.UNREAD
    )
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
