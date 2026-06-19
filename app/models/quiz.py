from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey, Integer, Uuid, Enum as SAEnum, String

from uuid import UUID, uuid4
from enum import Enum, auto

from app.core.database import Base
from app.models.mixins import TimeStampMixin

class QuestionType(Enum):
    SingleAnswer = auto()
    MultipleAnswer = auto()

class Quiz(TimeStampMixin, Base):
    __tablename__ = "quizzes"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"), nullable=False)
    questions: Mapped[list["Question"]] = relationship(
        back_populates="quiz", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(SAEnum(QuestionType), nullable=False)
    quiz_id: Mapped[UUID] = mapped_column(ForeignKey("quizzes.id"), nullable=False)
    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(String, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    question_id: Mapped[UUID] = mapped_column(ForeignKey("questions.id"), nullable=False)
    question: Mapped["Question"] = relationship(back_populates="answers")
