from datetime import date, datetime
from uuid import UUID

from sqlalchemy import and_, func, select

from app.exceptions.quiz_exceptions import (
    QuizResultAlreadyExistsException,
    QuizResultNotFoundException,
)
from app.models.company_member import CompanyMember, InviteStatus
from app.models.quiz_result import QuizResult
from app.repositories.base_repository import BaseRepository
from app.schemas.quiz_result import QuizResultResponseSchema


class QuizResultRepository(BaseRepository[QuizResult, QuizResultResponseSchema]):
    model = QuizResult
    not_found_exception = QuizResultNotFoundException
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

    async def get_quiz_answers_by_company(self, company_id: UUID):
        quiz_results = await self.session.execute(
            select(QuizResult).where(QuizResult.company_id == company_id)
        )

        return quiz_results.scalars().all()

    async def get_results_by_user_and_company(self, user_id: UUID, company_id: UUID):
        quiz_results = await self.session.execute(
            select(QuizResult).where(
                and_(
                    QuizResult.company_id == company_id,
                    QuizResult.user_id == user_id
                )
            )
        )

        return quiz_results.scalars().all()

    async def get_results_by_quiz_and_company(self, quiz_id: UUID, company_id: UUID):
        results = await self.session.execute(
            select(QuizResult).where(
                and_(QuizResult.quiz_id == quiz_id, QuizResult.company_id == company_id)
            )
        )

        return results.scalars().all()

    async def get_average_for_all_quizzes_by_user(
        self, user_id: UUID, date_from: date | None = None, date_to: date | None = None
    ) -> list[tuple[UUID, UUID, int, int]]:
        conditions = [QuizResult.user_id == user_id]
        if date_from is not None:
            conditions.append(QuizResult.created_at >= date_from)

        if date_to is not None:
            conditions.append(QuizResult.created_at <= date_to)

        quiz_results = await self.session.execute(
            select(
                QuizResult.quiz_id,
                QuizResult.user_id,
                func.sum(QuizResult.correct_answers),
                func.sum(QuizResult.total_questions),
            )
            .where(and_(*conditions))
            .group_by(QuizResult.quiz_id, QuizResult.user_id)
        )

        return quiz_results.all()

    async def get_last_attempt_for_all_quizzes_by_user(
        self, user_id: UUID
    ) -> list[tuple[UUID, UUID, datetime]]:
        quizzes = await self.session.execute(
            select(
                QuizResult.quiz_id,
                QuizResult.user_id,
                func.max(QuizResult.created_at),
            )
            .where(QuizResult.user_id == user_id)
            .group_by(QuizResult.quiz_id, QuizResult.user_id)
            .order_by(func.max(QuizResult.created_at).desc())
        )

        return quizzes.all()

    async def get_weekly_results_by_company(
        self, company_id: UUID
    ) -> list[tuple[UUID, datetime, int, int]]:
        week = func.date_trunc("week", QuizResult.created_at)
        results = await self.session.execute(
            select(
                QuizResult.user_id,
                week,
                func.sum(QuizResult.correct_answers),
                func.sum(QuizResult.total_questions),
            )
            .where(QuizResult.company_id == company_id)
            .group_by(QuizResult.user_id, week)
            .order_by(week)
        )

        return results.all()

    async def get_weekly_user_results_by_company(
        self, company_id: UUID, user_id: UUID
    ) -> list[tuple[UUID, UUID, datetime, int, int]]:
        week = func.date_trunc("week", QuizResult.created_at)
        results = await self.session.execute(
            select(
                QuizResult.quiz_id,
                QuizResult.user_id,
                week,
                func.sum(QuizResult.correct_answers),
                func.sum(QuizResult.total_questions),
            )
            .where(
                and_(QuizResult.company_id == company_id, QuizResult.user_id == user_id)
            )
            .group_by(QuizResult.quiz_id, QuizResult.user_id, week)
            .order_by(week)
        )

        return results.all()

    async def get_last_attempt_time_of_user_by_company(
        self, company_id: UUID
    ) -> list[tuple[UUID, datetime | None]]:
        results = await self.session.execute(
            select(
                CompanyMember.user_id,
                func.max(QuizResult.created_at),
            )
            .outerjoin(
                QuizResult,
                and_(
                    QuizResult.user_id == CompanyMember.user_id,
                    QuizResult.company_id == CompanyMember.company_id,
                ),
            )
            .where(
                and_(
                    CompanyMember.status == InviteStatus.ACTIVE,
                    CompanyMember.company_id == company_id,
                )
            )
            .group_by(CompanyMember.user_id)
        )

        return results.all()
