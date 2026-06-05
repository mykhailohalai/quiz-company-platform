from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.user import UserUpdateRequestSchema
from app.exceptions.user_exceptions import UserNotFoundException, UserAlreadyExistsException


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[User]:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def get_by_id(self, user_id: UUID) -> User | None:
        user = await self.session.get(User, user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return user

    async def create(self, user: User) -> User:
        self.session.add(user)
        try:
            await self.session.flush()
        except IntegrityError as ex:
            field = "email" if "email" in str(ex.orig) else "username"
            raise UserAlreadyExistsException(field)
        return user

    async def delete(self, user_id: UUID) -> bool:
        user = await self.session.get(User, user_id)
        if user is None:
            raise UserNotFoundException(user_id)

        await self.session.delete(user)
        return True

    async def update(self, user_id: UUID, updated_user: UserUpdateRequestSchema) -> User | None:
        user = await self.session.get(User, user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        try:
            for field, value in updated_user.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            await self.session.flush()
        except IntegrityError as ex:
            field = "email" if "email" in str(ex.orig) else "username"
            raise UserAlreadyExistsException(field)
        return user
