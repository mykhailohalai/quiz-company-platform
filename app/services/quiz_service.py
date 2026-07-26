from datetime import date, datetime, timezone
import logging
from uuid import UUID

from app.exceptions.general_exceptions import ForbiddenException

from app.exceptions.quiz_exceptions import QuizFrequencyException
from app.models.quiz import Quiz, Question, Answer
from app.models.quiz_result import QuizResult
from app.schemas.quiz_result import (
    CompanyMemberLastAttemptSchema,
    QuizAnswerRedisSchema,
    QuizAverageScoreSchema,
    QuizLastAttemptSchema,
    QuizSubmitSchema,
    WeeklyCompanyScoreSchema,
    WeeklyUserQuizScoreSchema,
)
from app.services.notification_service import NotificationService
from app.utils.unit_of_work import UnitOfWork
from app.schemas.quiz import QuizCreateRequestSchema, QuizUpdateRequestSchema
from app.services.redis_service import RedisService

logger = logging.getLogger(__name__)


class QuizService:
    def __init__(
        self,
        uow: UnitOfWork,
        redis_service: RedisService,
        notification_service: NotificationService,
    ):
        self.uow = uow
        self.redis_service = redis_service
        self.notification_service = notification_service

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
            await self.notification_service.send_notification(company_id, f"New quiz with name '{quiz.title}' was created")
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
                await self.uow.quizzes.update_questions(
                    company_id, quiz_id, data.questions
                )

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
            member = await self.uow.company_members.get_active_member(
                company_id, user_id
            )
            if member is None:
                raise ForbiddenException()
            return await self.uow.quizzes.get_with_relations(company_id, quiz_id)

    async def submit_quiz(
        self, company_id: UUID, quiz_id: UUID, user_id: UUID, data: QuizSubmitSchema
    ) -> QuizResult:
        async with self.uow:
            member = await self.uow.company_members.get_active_member(
                company_id, user_id
            )
            if member is None:
                raise ForbiddenException()

            quiz = await self.uow.quizzes.get_with_relations(company_id, quiz_id)

            last_attempt = await self.uow.quiz_results.get_last_attempt(
                quiz_id, user_id
            )
            if last_attempt:
                created_at = last_attempt.created_at
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                days_since = (datetime.now(timezone.utc) - created_at).days
                if days_since < quiz.frequency:
                    raise QuizFrequencyException()

            correct_map = await self.uow.quizzes.get_correct_answer_ids(quiz_id)
            answered_at = datetime.now(timezone.utc)
            redis_answers = []
            for ua in data.answers:
                is_correct = set(ua.answer_ids) == set(correct_map.get(ua.question_id, []))
                redis_answers.append(
                    QuizAnswerRedisSchema(
                        user_id=user_id,
                        company_id=company_id,
                        quiz_id=quiz_id,
                        question_id=ua.question_id,
                        answer_ids=ua.answer_ids,
                        is_correct=is_correct,
                        answered_at=answered_at,
                    )
                )
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
            return await self.uow.quiz_results.get_average_by_company(
                user_id, company_id
            )

    async def get_average_by_system(self, user_id: UUID) -> float:
        async with self.uow:
            return await self.uow.quiz_results.get_average_by_system(user_id)

    async def get_my_quiz_result(self, user_id: UUID, company_id: UUID, quiz_id: UUID):
        answers = await self.redis_service.get_quiz_answers_redis(
            user_id, company_id, quiz_id
        )
        if answers is None:
            async with self.uow:
                answers = await self.uow.quiz_results.get_last_attempt(quiz_id, user_id)

        return answers

    async def get_user_results_by_admin_and_owner(
        self, current_user_id: UUID, target_user_id: UUID, company_id: UUID
    ):
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)

            return await self.uow.quiz_results.get_results_by_user_and_company(
                target_user_id, company_id
            )

    async def get_all_results_by_admin_and_owner(
        self, current_user_id: UUID, company_id: UUID
    ):
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)

            return await self.uow.quiz_results.get_quiz_answers_by_company(company_id)

    async def get_quiz_results_for_export(
    self, current_user_id: UUID, company_id: UUID, quiz_id: UUID
    ):
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)
            return await self.uow.quiz_results.get_results_by_quiz_and_company(
                quiz_id, company_id
            )

    async def get_average_score_by_user(
        self,
        user_id: UUID,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[QuizAverageScoreSchema]:
        async with self.uow:
            results = await self.uow.quiz_results.get_average_for_all_quizzes_by_user(
                user_id, date_from, date_to
            )

            return [
                QuizAverageScoreSchema(
                    quiz_id=quiz_id,
                    user_id=user_id,
                    average_score=round(correct / total * 100, 2) if total else 0.0,
                )
                for quiz_id, user_id, correct, total in results
            ]

    async def get_quizzes_last_attempt_by_user(
        self, user_id: UUID
    ) -> list[QuizLastAttemptSchema]:
        async with self.uow:
            last_attempts = (
                await self.uow.quiz_results.get_last_attempt_for_all_quizzes_by_user(
                    user_id
                )
            )

            return [
                QuizLastAttemptSchema(
                    quiz_id=quiz_id, user_id=user_id, last_attempt_at=last_attempt_at
                )
                for quiz_id, user_id, last_attempt_at in last_attempts
            ]

    async def get_weekly_results_by_company(
        self, company_id: UUID, current_user_id: UUID
    ) -> list[WeeklyCompanyScoreSchema]:
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)
            results = await self.uow.quiz_results.get_weekly_results_by_company(
                company_id
            )

            return [
                WeeklyCompanyScoreSchema(
                    user_id=user_id,
                    week_start=week_start,
                    average_score=round(correct / total * 100, 2) if total else 0.0,
                )
                for user_id, week_start, correct, total in results
            ]

    async def get_weekly_results_by_user_and_company(
        self, company_id: UUID, target_user_id: UUID, current_user_id: UUID
    ) -> list[WeeklyUserQuizScoreSchema]:
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)
            results = await self.uow.quiz_results.get_weekly_user_results_by_company(
                company_id, target_user_id
            )

            return [
                WeeklyUserQuizScoreSchema(
                    quiz_id=quiz_id,
                    user_id=user_id,
                    week_start=week_start,
                    average_score=round(correct / total * 100, 2) if total else 0.0,
                )
                for quiz_id, user_id, week_start, correct, total in results
            ]

    async def get_last_attempts_by_company(
        self, company_id: UUID, current_user_id: UUID
    ) -> list[CompanyMemberLastAttemptSchema]:
        async with self.uow:
            await self._check_owner_or_admin(company_id, current_user_id)
            results = (
                await self.uow.quiz_results.get_last_attempt_time_of_user_by_company(
                    company_id
                )
            )

            return [
                CompanyMemberLastAttemptSchema(
                    user_id=user_id, last_attempt_at=last_attempt_at
                )
                for user_id, last_attempt_at in results
            ]


    async def _notify_overdue_quizzes_for_user(self, user_id: UUID):
        async with self.uow:
            available_quizzes = await self.uow.quizzes.get_available_quizzes_for_user(
                user_id
            )
            last_attempts = (
                await self.uow.quiz_results.get_last_attempt_for_all_quizzes_by_user(
                    user_id
                )
            )
            last_attempt_by_quiz = {
                quiz_id: last_at for quiz_id, _, last_at in last_attempts
            }

            for quiz in available_quizzes:
                last_attempt_at = last_attempt_by_quiz.get(quiz.id)
                if last_attempt_at is None:
                    overdue = True
                else:
                    if last_attempt_at.tzinfo is None:
                        last_attempt_at = last_attempt_at.replace(tzinfo=timezone.utc)
                    overdue = (
                        datetime.now(timezone.utc) - last_attempt_at
                    ).days >= quiz.frequency

                if overdue:
                    await self.notification_service.send_notification_to_user(
                        user_id, f"Time to retake quiz '{quiz.title}'"
                    )

    async def notify_all_overdue_quizzes(self) -> None:
        async with self.uow:
            users = await self.uow.users.get_all_users()

        for user in users:
            await self._notify_overdue_quizzes_for_user(user.id)
