from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field


class QuestionAnswerSchema(BaseModel):
    question_id: UUID
    answer_ids: list[UUID]


class QuizSubmitSchema(BaseModel):
    answers: list[QuestionAnswerSchema]


class QuizResultResponseSchema(BaseModel):
    id: UUID
    user_id: UUID
    quiz_id: UUID
    company_id: UUID
    correct_answers: int
    total_questions: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def score_percentage(self) -> float:
        if self.total_questions == 0:
            return 0.0
        return round(self.correct_answers / self.total_questions * 100, 2)


class AverageScoreResponseSchema(BaseModel):
    average_score: float


class QuizAnswerRedisSchema(BaseModel):
    user_id: UUID
    company_id: UUID
    quiz_id: UUID
    question_id: UUID
    answer_ids: list[UUID]
    is_correct: bool
    answered_at: datetime