from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.repositories.user_repository import UserRepository


class UnitOfWork:
    session: AsyncSession

    async def __aenter__(self):
        self.session = async_session()
        self.users = UserRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


def get_uow() -> UnitOfWork:
    return UnitOfWork()
