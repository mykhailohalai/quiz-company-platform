from fakes.fake_session import FakeSession
from fakes.fake_user_repository import FakeUserRepository


class FakeUnitOfWork:
    def __init__(self, users=None):
        self.users = FakeUserRepository(users)
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
