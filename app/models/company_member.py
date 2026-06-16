from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Uuid, Enum as SAEnum

from uuid import UUID, uuid4
from enum import Enum, auto

from app.core.database import Base
from app.models.mixins import TimeStampMixin

class Role(Enum):
    Owner = auto()
    Member = auto()


class InviteStatus(Enum):
    Pending_invite = auto()
    Pending_request = auto()
    Active = auto()
    Rejected = auto()

class CompanyMember(TimeStampMixin, Base):
    __tablename__="company_members"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[Role] = mapped_column(
        SAEnum(Role, name="role"),
        nullable=False
    )
    status: Mapped[InviteStatus] = mapped_column(
        SAEnum(InviteStatus, name="invite_status"),
        nullable=False    
    )
