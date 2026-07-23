from fastapi import Depends
from uuid import UUID
import logging

from app.models.user import User
from app.schemas.user import UserSignUpRequestSchema, UserUpdateRequestSchema
from app.utils.unit_of_work import UnitOfWork, get_uow
from app.utils.password import PasswordHelper

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_user(
        self, data: UserSignUpRequestSchema
    ) -> User:
        data_dict = data.model_dump()
        data_dict["password"] = PasswordHelper.hash_password(data_dict["password"])
        user = User(**data_dict)
        async with self.uow:
            await self.uow.users.create(user)
            await self.uow.commit()
        logger.info("User created: id=%s username=%s", user.id, user.username)
        return user

    async def get_all_users(self, skip: int, limit: int) -> tuple[list[User], int]:
        async with self.uow:
            return await self.uow.users.get_all(skip, limit)

    async def get_user_by_id(self, user_id: UUID) -> User:
        async with self.uow:
            return await self.uow.users.get_by_id(user_id)

    async def update_user(self, user_id: UUID, data: UserUpdateRequestSchema) -> User:
        if data.password is not None:
            data.password = PasswordHelper.hash_password(data.password)
        async with self.uow:
            user = await self.uow.users.update(user_id, data)
            await self.uow.commit()
            await self.uow.session.refresh(user)
        logger.info("User updated: id=%s", user_id)
        return user

    async def delete_user(self, user_id: UUID) -> None:
        async with self.uow:
            await self.uow.users.delete(user_id)
            await self.uow.commit()
        logger.info("User deleted: id=%s", user_id)

def get_user_service(uow=Depends(get_uow)) -> UserService:
    return UserService(uow)
