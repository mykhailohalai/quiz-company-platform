from uuid import UUID

from sqlalchemy import and_, func, select

from app.exceptions.quiz_exceptions import (
    QuizNotFoundException,
    QuizAlreadyExistsException,
)
from app.models.quiz import Quiz
from app.repositories.base_repository import BaseRepository
from app.schemas.quiz import QuizUpdateRequestSchema


class QuizRepository(BaseRepository[Quiz, QuizUpdateRequestSchema]):
    model = Quiz
    not_found_exception = QuizNotFoundException
    already_exists_exception = QuizAlreadyExistsException

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
