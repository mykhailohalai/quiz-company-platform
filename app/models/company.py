from typing import TYPE_CHECKING

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Uuid, String, Enum as SAEnum
from uuid import UUID, uuid4
from app.core.database import Base
from enum import Enum, auto

from app.models.mixins import TimeStampMixin

if TYPE_CHECKING:
    from app.models.user import User


class CompanyVisibility(Enum):
    Hidden = auto()
    Visible_to_all = auto()


class Company(TimeStampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(String(1500), nullable=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship(back_populates="companies")
    visibility: Mapped[CompanyVisibility] = mapped_column(
        SAEnum(CompanyVisibility, name="company_visibility"),
        nullable=False,
        default=CompanyVisibility.Visible_to_all
    )
