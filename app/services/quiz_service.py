from datetime import datetime, timezone
import logging
from uuid import UUID

from fastapi import Depends
from redis.asyncio import Redis

from app.exceptions.general_exceptions import ForbiddenException

from app.exceptions.quiz_exceptions import QuizFrequencyException
from app.models.quiz import Quiz, Question, Answer
from app.models.quiz_result import QuizResult
from app.schemas.quiz_result import QuizAnswerRedisSchema, QuizSubmitSchema
from app.utils.unit_of_work import UnitOfWork, get_uow
from app.schemas.quiz import QuizCreateRequestSchema, QuizUpdateRequestSchema
from app.core.redis import get_redis
from app.services.redis_service import RedisService

logger = logging.getLogger(__name__)


class QuizService:
    def __init__(self, uow: UnitOfWork, redis_service: RedisService):
        self.uow = uow
        self.redis_service = redis_service

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
            quiz = await self.uow.quizzes.get_with_relations(company_id, quiz.id)
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
            if data.questions is not None:
                await self.uow.quizzes.update_questions(company_id, quiz_id, data.questions)

            await self.uow.commit()
            quiz = await self.uow.quizzes.get_with_relations(company_id, quiz_id)
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

    async def get_quiz_by_company_member(
        self, company_id: UUID, user_id: UUID, quiz_id: UUID
    ) -> Quiz:
        async with self.uow:
            member = await self.uow.company_members.get_active_member_by_company_and_user(
                company_id, user_id
            )
            if member is None:
                raise ForbiddenException()
            return await self.uow.quizzes.get_with_relations(company_id, quiz_id)

    async def submit_quiz(
    self, company_id: UUID, quiz_id: UUID, user_id: UUID, data: QuizSubmitSchema
    ) -> QuizResult:
        async with self.uow:
            member = await self.uow.company_members.get_active_member_by_company_and_user(
                company_id, user_id
            )
            if member is None:
                raise ForbiddenException()

            quiz = await self.uow.quizzes.get_with_relations(company_id, quiz_id)

            last_attempt = await self.uow.quiz_results.get_last_attempt(quiz_id, user_id)
            if last_attempt:
                created_at = last_attempt.created_at
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                days_since = (datetime.now(timezone.utc) - created_at).days
                if days_since < quiz.frequency:
                    raise QuizFrequencyException()

            correct_map = {
                q.id: {a.id for a in q.answers if a.is_correct}
                for q in quiz.questions
            }
            answered_at = datetime.now(timezone.utc)
            redis_answers = [
                QuizAnswerRedisSchema(
                    user_id=user_id,
                    company_id=company_id,
                    quiz_id=quiz_id,
                    question_id=ua.question_id,
                    answer_ids=ua.answer_ids,
                    is_correct=set(ua.answer_ids) == correct_map.get(ua.question_id, set()),
                    answered_at=answered_at,
                )
                for ua in data.answers
            ]
            correct_answers = sum(1 for a in redis_answers if a.is_correct)

            result = QuizResult(
                user_id=user_id,
                quiz_id=quiz_id,
                company_id=company_id,
                correct_answers=correct_answers,
                total_questions=len(quiz.questions),
            )
            await self.uow.quiz_results.create(result)
            await self.uow.commit()

            await self.redis_service.save_quiz_answers_redis(
                user_id=user_id,
                company_id=company_id,
                quiz_id=quiz_id,
                answers=redis_answers,
            )

            return result
    
    async def get_average_by_company(self, user_id: UUID, company_id: UUID) -> float:
        async with self.uow:
            return await self.uow.quiz_results.get_average_by_company(user_id, company_id)

    async def get_average_by_system(self, user_id: UUID) -> float:
        async with self.uow:
            return await self.uow.quiz_results.get_average_by_system(user_id)


def get_quiz_service(
    uow: UnitOfWork = Depends(get_uow),
    redis: Redis = Depends(get_redis),
) -> QuizService:
    return QuizService(uow, RedisService(redis))
