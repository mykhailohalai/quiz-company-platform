from sqlalchemy import select
from uuid import UUID

from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.schemas.user import UserUpdateRequestSchema
from app.exceptions.user_exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
)


class UserRepository(BaseRepository[User, UserUpdateRequestSchema]):
    model = User
    not_found_exception = UserNotFoundException
    already_exists_exception = UserAlreadyExistsException

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_all_users(self) -> list[User]:
        users = await self.session.execute(select(User))

        return users.scalars().all()