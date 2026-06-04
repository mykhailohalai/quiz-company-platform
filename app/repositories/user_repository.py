from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserUpdateRequestSchema


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def create(self, user: User) -> User:
        self.session.add(user)
        return user

    async def delete(self, user_id: UUID) -> bool:
        user = await self.session.get(User, user_id)
        if user is None:
            return False

        await self.session.delete(user)
        return True

    async def update(self, user_id: UUID, updated_user: UserUpdateRequestSchema) -> User | None:
        user = await self.session.get(User, user_id)
        if user is None:
            return None

        for field, value in updated_user.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return user
