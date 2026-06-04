from datetime import datetime
from sqlalchemy import func
from sqlalchemy import Uuid, String
from sqlalchemy.orm import Mapped, mapped_column
from uuid import UUID, uuid4

from app.core.database import Base


class TimeStampMixin():
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


class User(TimeStampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    fname: Mapped[str] = mapped_column(String(50), nullable=False)
    sname: Mapped[str] = mapped_column(String(50), nullable=False)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=True, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)


