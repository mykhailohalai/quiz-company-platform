from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from app.models.company_member import InviteStatus
from app.models.quiz_result import QuizResult


class FakeQuizResultRepository:
    def __init__(self, results=None, company_members=None):
        self.results = {r.id: r for r in (results or [])}
        self.company_members = company_members

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

    async def get_results_by_user_and_company(self, user_id: UUID, company_id: UUID) -> list[QuizResult]:
        return [
            r for r in self.results.values()
            if r.user_id == user_id and r.company_id == company_id
        ]

    async def get_quiz_answers_by_company(self, company_id: UUID) -> list[QuizResult]:
        return [r for r in self.results.values() if r.company_id == company_id]

    async def get_results_by_quiz_and_company(self, quiz_id: UUID, company_id: UUID) -> list[QuizResult]:
        return [
            r for r in self.results.values()
            if r.quiz_id == quiz_id and r.company_id == company_id
        ]

    @staticmethod
    def _week_start(dt: datetime) -> datetime:
        day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        return day - timedelta(days=day.weekday())

    async def get_average_for_all_quizzes_by_user(
        self, user_id: UUID, date_from: date | None = None, date_to: date | None = None
    ) -> list[tuple[UUID, UUID, int, int]]:
        grouped = defaultdict(lambda: [0, 0])
        for r in self.results.values():
            if r.user_id != user_id:
                continue
            if date_from is not None and r.created_at.date() < date_from:
                continue
            if date_to is not None and r.created_at.date() > date_to:
                continue
            grouped[r.quiz_id][0] += r.correct_answers
            grouped[r.quiz_id][1] += r.total_questions

        return [(quiz_id, user_id, c, t) for quiz_id, (c, t) in grouped.items()]

    async def get_last_attempt_for_all_quizzes_by_user(
        self, user_id: UUID
    ) -> list[tuple[UUID, UUID, datetime]]:
        grouped = defaultdict(list)
        for r in self.results.values():
            if r.user_id == user_id:
                grouped[r.quiz_id].append(r.created_at)

        result = [(quiz_id, user_id, max(dates)) for quiz_id, dates in grouped.items()]
        result.sort(key=lambda row: row[2], reverse=True)
        return result

    async def get_weekly_results_by_company(
        self, company_id: UUID
    ) -> list[tuple[UUID, datetime, int, int]]:
        grouped = defaultdict(lambda: [0, 0])
        for r in self.results.values():
            if r.company_id != company_id:
                continue
            key = (r.user_id, self._week_start(r.created_at))
            grouped[key][0] += r.correct_answers
            grouped[key][1] += r.total_questions

        result = [(user_id, week, c, t) for (user_id, week), (c, t) in grouped.items()]
        result.sort(key=lambda row: row[1])
        return result

    async def get_weekly_user_results_by_company(
        self, company_id: UUID, user_id: UUID
    ) -> list[tuple[UUID, UUID, datetime, int, int]]:
        grouped = defaultdict(lambda: [0, 0])
        for r in self.results.values():
            if r.company_id != company_id or r.user_id != user_id:
                continue
            key = (r.quiz_id, self._week_start(r.created_at))
            grouped[key][0] += r.correct_answers
            grouped[key][1] += r.total_questions

        result = [
            (quiz_id, user_id, week, c, t)
            for (quiz_id, week), (c, t) in grouped.items()
        ]
        result.sort(key=lambda row: row[2])
        return result

    async def get_last_attempt_time_of_user_by_company(
        self, company_id: UUID
    ) -> list[tuple[UUID, datetime | None]]:
        members = self.company_members.members.values() if self.company_members else []
        active_user_ids = {
            m.user_id for m in members
            if m.company_id == company_id and m.status == InviteStatus.ACTIVE
        }

        last_attempts = defaultdict(list)
        for r in self.results.values():
            if r.company_id == company_id and r.user_id in active_user_ids:
                last_attempts[r.user_id].append(r.created_at)

        return [
            (user_id, max(last_attempts[user_id]) if user_id in last_attempts else None)
            for user_id in active_user_ids
        ]
