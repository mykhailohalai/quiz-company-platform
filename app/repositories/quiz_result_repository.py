from uuid import UUID

from sqlalchemy import func, select

from app.models.quiz_result import QuizResult
from app.repositories.base_repository import BaseRepository
from app.schemas.quiz_result import QuizResultResponseSchema


class QuizResultRepository(BaseRepository[QuizResult, QuizResultResponseSchema]):
    model = QuizResult
    not_found_exception = Exception
    already_exists_exception = Exception

    async def get_last_attempt(self, quiz_id: UUID, user_id: UUID) -> QuizResult | None:
        result = await self.session.execute(
            select(QuizResult)
            .where(
                QuizResult.quiz_id == quiz_id,
                QuizResult.user_id == user_id,
            )
            .order_by(QuizResult.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_average_by_company(self, user_id: UUID, company_id: UUID) -> float:
        result = await self.session.execute(
            select(
                func.sum(QuizResult.correct_answers),
                func.sum(QuizResult.total_questions),
            ).where(
                QuizResult.user_id == user_id,
                QuizResult.company_id == company_id,
            )
        )
        correct, total = result.one()
        if not total:
            return 0.0
        return round(correct / total * 100, 2)

    async def get_average_by_system(self, user_id: UUID) -> float:
        result = await self.session.execute(
            select(
                func.sum(QuizResult.correct_answers),
                func.sum(QuizResult.total_questions),
            ).where(QuizResult.user_id == user_id)
        )
        correct, total = result.one()
        if not total:
            return 0.0
        return round(correct / total * 100, 2)
