from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.quiz import QuestionType


# --- Answer schemas ---
class AnswerCreateRequestSchema(BaseModel):
    text: str = Field(..., min_length=1)
    is_correct: bool


class AnswerResponseSchema(BaseModel):
    id: UUID
    text: str
    is_correct: bool

    model_config = ConfigDict(from_attributes=True)


# --- Question schemas ---
class QuestionCreateRequestSchema(BaseModel):
    title: str = Field(..., min_length=1)
    answers: list[AnswerCreateRequestSchema] = Field(..., min_length=2, max_length=4)
    question_type: QuestionType = Field(default=QuestionType.MultipleAnswer)


class QuestionResponseSchema(BaseModel):
    id: UUID
    title: str
    answers: list[AnswerResponseSchema]
    question_type: QuestionType

    model_config = ConfigDict(from_attributes=True)


# --- Quiz schemas ---
class QuizCreateRequestSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=500)
    frequency: int = Field(..., gt=0)
    questions: list[QuestionCreateRequestSchema] = Field(..., min_length=2)


class QuizUpdateRequestSchema(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, min_length=1, max_length=500)
    frequency: int | None = Field(None, gt=0)
    questions: list[QuestionCreateRequestSchema] | None = None


class QuizResponseSchema(BaseModel):
    id: UUID
    title: str
    description: str
    frequency: int
    questions: list[QuestionResponseSchema]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedQuizResponseSchema(BaseModel):
    quizzes: list[QuizResponseSchema]
    total: int
    skip: int
    limit: int
    has_more: bool
