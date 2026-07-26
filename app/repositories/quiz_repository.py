from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.exceptions.quiz_exceptions import (
    QuizNotFoundException,
    QuizAlreadyExistsException,
)
from app.models.quiz import Quiz, Question, Answer
from app.repositories.base_repository import BaseRepository
from app.schemas.quiz import QuizUpdateRequestSchema, QuestionCreateRequestSchema


class QuizRepository(BaseRepository[Quiz, QuizUpdateRequestSchema]):
    model = Quiz
    not_found_exception = QuizNotFoundException
    already_exists_exception = QuizAlreadyExistsException

    async def create_with_questions(
        self, quiz: Quiz, questions_data: list[QuestionCreateRequestSchema]
    ) -> None:
        self.session.add(quiz)
        await self.session.flush()

        for q_data in questions_data:
            question = Question(
                title=q_data.title,
                quiz_id=quiz.id,
                question_type=q_data.question_type,
            )
            self.session.add(question)
            await self.session.flush()

            for a_data in q_data.answers:
                self.session.add(Answer(
                    text=a_data.text,
                    is_correct=a_data.is_correct,
                    question_id=question.id,
                ))

    async def update_questions(
        self, quiz_id: UUID, questions_data: list[QuestionCreateRequestSchema]
    ) -> None:
        quiz = await self.get_with_relations(quiz_id)
        for question in quiz.questions:
            await self.session.delete(question)
        await self.session.flush()

        for q_data in questions_data:
            question = Question(
                title=q_data.title,
                quiz_id=quiz_id,
                question_type=q_data.question_type,
            )
            self.session.add(question)
            await self.session.flush()

            for a_data in q_data.answers:
                self.session.add(Answer(
                    text=a_data.text,
                    is_correct=a_data.is_correct,
                    question_id=question.id,
                ))

    async def get_with_relations(self, quiz_id: UUID) -> Quiz:
        result = await self.session.execute(
            select(Quiz)
            .options(selectinload(Quiz.questions).selectinload(Question.answers))
            .where(Quiz.id == quiz_id)
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
