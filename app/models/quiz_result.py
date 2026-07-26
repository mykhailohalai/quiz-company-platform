from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, Uuid

from app.core.database import Base

from sqlalchemy.orm import Mapped, mapped_column

class QuizResult(Base):
    __tablename__ = "quiz_results"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    quiz_id: Mapped[UUID] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)

