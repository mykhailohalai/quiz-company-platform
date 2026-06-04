from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def create(self, user: User) -> User:
        self.session.add(user)
        return user
