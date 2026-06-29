import logging
from uuid import UUID

from fastapi import Depends

from app.exceptions.general_exceptions import ForbiddenException

from app.models.company_member import Role
from app.models.quiz import Quiz
from app.utils.unit_of_work import UnitOfWork, get_uow
from app.schemas.quiz import QuizCreateRequestSchema, QuizUpdateRequestSchema

logger = logging.getLogger(__name__)


class QuizService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _check_owner_or_admin(
        self, company_id: UUID, current_user_id: UUID
    ) -> None:
        company = await self.uow.companies.get_by_id(company_id)
        if await self.uow.companies.is_owner(current_user_id, company):
            return
        admin = await self.uow.company_members.get_admin_by_id(
            current_user_id, company_id
        )
        if admin is None:
            raise ForbiddenException()

    async def create_quiz(
        self, company_id: UUID, current_user_id: UUID, data: QuizCreateRequestSchema
    ) -> Quiz:
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)

            quiz = Quiz(
                title=data.title,
                description=data.description,
                frequency=data.frequency,
                company_id=company_id,
            )
            await self.uow.quizzes.create_with_questions(quiz, data.questions)
            await self.uow.commit()
            quiz = await self.uow.quizzes.get_with_relations(quiz.id)
            logger.info("Quiz created: id=%s company_id=%s", quiz.id, company_id)
            return quiz

    async def update_quiz(
        self,
        quiz_id: UUID,
        company_id: UUID,
        current_user_id: UUID,
        data: QuizUpdateRequestSchema,
    ) -> Quiz:
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)

            quiz = await self.uow.quizzes.get_by_id(quiz_id)
            if data.title is not None:
                quiz.title = data.title
            if data.description is not None:
                quiz.description = data.description
            if data.frequency is not None:
                quiz.frequency = data.frequency

            await self.uow.commit()
            logger.info("Quiz updated: id=%s", quiz_id)
            return quiz

    async def delete_quiz(
        self, quiz_id: UUID, company_id: UUID, current_user_id: UUID
    ) -> None:
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)
            await self.uow.quizzes.delete(quiz_id)
            await self.uow.commit()
            logger.info("Quiz deleted: id=%s", quiz_id)

    async def get_quizzes(
        self, company_id: UUID, skip: int, limit: int
    ) -> tuple[list[Quiz], int]:
        async with self.uow:
            return await self.uow.quizzes.get_by_company(company_id, skip, limit)
