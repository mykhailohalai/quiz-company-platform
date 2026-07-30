from uuid import UUID, uuid4

from app.exceptions.quiz_exceptions import QuizNotFoundException, QuizAlreadyExistsException
from app.models.company_member import InviteStatus
from app.models.quiz import Answer, Question


class FakeQuizRepository:
    def __init__(self, quizzes=None, company_members=None):
        self.quizzes = {q.id: q for q in (quizzes or [])}
        self.company_members = company_members

    async def get_by_id(self, quiz_id: UUID):
        quiz = self.quizzes.get(quiz_id)
        if quiz is None:
            raise QuizNotFoundException(quiz_id)
        return quiz

    async def create(self, quiz):
        if quiz.id is None:
            quiz.id = uuid4()
        self.quizzes[quiz.id] = quiz
        return quiz

    async def create_with_questions(self, quiz, questions_data):
        if quiz.id is None:
            quiz.id = uuid4()
        quiz.questions = [self._build_question(quiz.id, q) for q in questions_data]
        self.quizzes[quiz.id] = quiz

    async def update_questions(self, company_id: UUID, quiz_id: UUID, questions_data):
        quiz = self.quizzes.get(quiz_id)
        if quiz is None or quiz.company_id != company_id:
            raise QuizNotFoundException(quiz_id)
        quiz.questions = [self._build_question(quiz_id, q) for q in questions_data]

    @staticmethod
    def _build_question(quiz_id, question_data):
        question = Question(
            id=uuid4(),
            title=question_data.title,
            quiz_id=quiz_id,
            question_type=question_data.question_type,
        )
        question.answers = [
            Answer(
                id=uuid4(),
                text=a.text,
                is_correct=a.is_correct,
                question_id=question.id,
            )
            for a in question_data.answers
        ]
        return question

    async def delete(self, quiz_id: UUID):
        if quiz_id not in self.quizzes:
            raise QuizNotFoundException(quiz_id)
        del self.quizzes[quiz_id]
        return True

    async def get_with_relations(self, company_id: UUID, quiz_id: UUID):
        quiz = self.quizzes.get(quiz_id)
        if quiz is None or quiz.company_id != company_id:
            raise QuizNotFoundException(quiz_id)
        return quiz

    async def get_by_company(self, company_id: UUID, skip: int = 0, limit: int = 10):
        result = [q for q in self.quizzes.values() if q.company_id == company_id]
        return result[skip:skip + limit], len(result)

    async def get_correct_answer_ids(self, quiz_id: UUID) -> dict[UUID, list[UUID]]:
        quiz = self.quizzes.get(quiz_id)
        if quiz is None:
            return {}
        return {
            q.id: [a.id for a in q.answers if a.is_correct]
            for q in quiz.questions
        }
        return [q for q in self.quizzes.values() if q.company_id in company_ids]

    async def get_by_company_and_title(self, company_id: UUID, title: str):
        for q in self.quizzes.values():
            if q.company_id == company_id and q.title == title:
                return q
        return None
