from typing import TYPE_CHECKING

from sqlalchemy import Uuid, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4

from app.core.database import Base
from app.models.mixins import TimeStampMixin

if TYPE_CHECKING:
    from app.models.company import Company


class User(TimeStampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    fname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    lname: Mapped[str | None] = mapped_column(String(50), nullable=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    companies: Mapped[list["Company"]] = relationship(back_populates="owner")
