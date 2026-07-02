from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from app.exceptions.quiz_exceptions import (
    QuizNotFoundException,
    QuizAlreadyExistsException,
)
from app.models.quiz import Quiz, Question, Answer
from app.repositories.base_repository import BaseRepository
from app.schemas.quiz import QuizUpdateRequestSchema


class QuizRepository(BaseRepository[Quiz, QuizUpdateRequestSchema]):
    model = Quiz
    not_found_exception = QuizNotFoundException
    already_exists_exception = QuizAlreadyExistsException

    async def get_with_relations(self, company_id: UUID, quiz_id: UUID) -> Quiz:
        result = await self.session.execute(
            select(Quiz)
            .options(selectinload(Quiz.questions).selectinload(Question.answers))
            .where(
                and_(
                    Quiz.id == quiz_id,
                    Quiz.company_id == company_id
                )
            )
        )
        quiz = result.scalar_one_or_none()
        if quiz is None:
            raise QuizNotFoundException(quiz_id)
        return quiz

    async def get_by_company(
        self, company_id: UUID, skip: int, limit: int
    ) -> tuple[list[Quiz], int]:
        condition = Quiz.company_id == company_id
        total = await self.session.scalar(
            select(func.count()).select_from(Quiz).where(condition)
        )
        result = await self.session.execute(
            select(Quiz).where(condition).offset(skip).limit(limit)
        )
        return result.scalars().all(), total
