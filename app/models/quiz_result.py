from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Numeric, Uuid, func

from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    quiz_id: Mapped[UUID] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(precision=5, scale=2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
