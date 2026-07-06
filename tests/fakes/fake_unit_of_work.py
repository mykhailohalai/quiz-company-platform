from fakes.fake_notification_repository import FakeNotificationRepository
from fakes.fake_session import FakeSession
from fakes.fake_user_repository import FakeUserRepository
from fakes.fake_company_repository import FakeCompanyRepository
from fakes.fake_company_member_repository import FakeCompanyMemberRepository
from fakes.fake_quiz_repository import FakeQuizRepository
from fakes.fake_quiz_result_repository import FakeQuizResultRepository


class FakeUnitOfWork:
    def __init__(self, users=None, companies=None, company_members=None, quizzes=None, quiz_results=None, notifications=None):
        self.users = FakeUserRepository(users)
        self.companies = FakeCompanyRepository(companies)
        self.company_members = FakeCompanyMemberRepository(company_members)
        self.quizzes = FakeQuizRepository(quizzes, self.company_members)
        self.quiz_results = FakeQuizResultRepository(quiz_results, self.company_members)
        self.notifications = FakeNotificationRepository(notifications)
        self.session = FakeSession()
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass
