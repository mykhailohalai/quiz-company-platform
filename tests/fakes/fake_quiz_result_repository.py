from datetime import datetime, timezone
from uuid import UUID

from app.models.quiz_result import QuizResult


class FakeQuizResultRepository:
    def __init__(self, results=None):
        self.results = {r.id: r for r in (results or [])}

    async def create(self, result: QuizResult) -> QuizResult:
        self.results[result.id] = result
        return result

    async def get_last_attempt(self, quiz_id: UUID, user_id: UUID) -> QuizResult | None:
        attempts = [
            r for r in self.results.values()
            if r.quiz_id == quiz_id and r.user_id == user_id
        ]
        if not attempts:
            return None
        return max(attempts, key=lambda r: r.created_at)

    async def get_average_by_company(self, user_id: UUID, company_id: UUID) -> float:
        results = [
            r for r in self.results.values()
            if r.user_id == user_id and r.company_id == company_id
        ]
        if not results:
            return 0.0
        correct = sum(r.correct_answers for r in results)
        total = sum(r.total_questions for r in results)
        return round(correct / total * 100, 2) if total else 0.0

    async def get_average_by_system(self, user_id: UUID) -> float:
        results = [r for r in self.results.values() if r.user_id == user_id]
        if not results:
            return 0.0
        correct = sum(r.correct_answers for r in results)
        total = sum(r.total_questions for r in results)
        return round(correct / total * 100, 2) if total else 0.0
