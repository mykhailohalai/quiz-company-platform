from fastapi import Depends
from uuid import UUID, uuid4
import logging

from app.core import settings
from app.exceptions.user_exceptions import InvalidCredentialsException
from app.models.user import User
from app.schemas.user import UserSignUpRequestSchema, UserUpdateRequestSchema
from app.schemas.token import RefreshTokenRequestSchema, TokenResponseSchema
from app.utils.unit_of_work import UnitOfWork, get_uow
from app.utils.password import PasswordHelper
from app.utils.jwt import JWTHelper

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

    async def get_current_user(self, token: str) -> User:
        try:
            payload = JWTHelper.decode_access_token(token)
        except InvalidCredentialsException:
            auth0_payload = JWTHelper.decode_auth0_token(token)
            return await self.get_or_create_user_from_auth0(auth0_payload["email"])

        user_id = UUID(payload["user_id"])
        async with self.uow:
            return await self.uow.users.get_by_id(user_id)

    async def get_or_create_user_from_auth0(self, email: str) -> User:
        async with self.uow:
            user = await self.uow.users.get_by_email(email)
            if user is not None:
                return user

            username = email.split("@")[0]
            if await self.uow.users.get_by_username(username) is not None:
                username = f"{username}_{uuid4().hex[:8]}"

            user = User(
                username=username,
                email=email,
                password=PasswordHelper.hash_password(uuid4().hex),
            )
            await self.uow.users.create(user)
            await self.uow.commit()
        logger.info("User created from Auth0: id=%s email=%s", user.id, user.email)
        return user

    async def authenticate_user(self, username: str, password: str) -> TokenResponseSchema:
        async with self.uow:
            user = await self.uow.users.get_by_username(username)
        if user is None or not PasswordHelper.verify_password(user.password, password):
            raise InvalidCredentialsException()
        logger.info("User authenticated: id=%s username=%s", user.id, user.username)

        return TokenResponseSchema(
            access_token=JWTHelper.create_access_token(
                user.id, user.username, user.email
            ),
            refresh_token=JWTHelper.create_refresh_token(
                user.id, user.username, user.email
            ),
            expires_in=settings.jwt_expire_minutes * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponseSchema:
        payload = JWTHelper.decode_refresh_token(refresh_token)
        access_token = JWTHelper.create_access_token(
            UUID(payload["user_id"]),
            payload["username"],
            payload["email"]
        )

        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_expire_minutes * 60,
        )


def get_user_service(uow=Depends(get_uow)) -> UserService:
    return UserService(uow)
