from uuid import UUID

from app.exceptions.quiz_exceptions import QuizNotFoundException, QuizAlreadyExistsException


class FakeQuizRepository:
    def __init__(self, quizzes=None):
        self.quizzes = {q.id: q for q in (quizzes or [])}

    async def get_by_id(self, quiz_id: UUID):
        quiz = self.quizzes.get(quiz_id)
        if quiz is None:
            raise QuizNotFoundException(quiz_id)
        return quiz

    async def create(self, quiz):
        self.quizzes[quiz.id] = quiz
        return quiz

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
