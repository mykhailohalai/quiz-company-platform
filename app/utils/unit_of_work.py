from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from app.repositories.user_repository import UserRepository
from app.repositories.company_repository import CompanyRepository
from app.repositories.company_member_repository import CompanyMember


class UnitOfWork:
    session: AsyncSession

    async def __aenter__(self):
        self.session = async_session()
        self.users = UserRepository(self.session)
        self.companies = CompanyRepository(self.session)
        self.company_members = CompanyMember(self.session)
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
