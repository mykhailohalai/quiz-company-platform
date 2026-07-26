from datetime import datetime, timedelta, timezone
from fastapi import Depends
from uuid import UUID, uuid4
import logging

import bcrypt
import jwt
from pydantic import EmailStr

from app.core import settings
from app.exceptions.user_exceptions import InvalidCredentialsException
from app.exceptions.general_exceptions import ForbiddenException
from app.models.user import User
from app.schemas.user import UserSignUpRequestSchema, UserUpdateRequestSchema
from app.schemas.token import TokenResponseSchema
from app.utils.unit_of_work import UnitOfWork, get_uow

logger = logging.getLogger(__name__)

_jwks_client = jwt.PyJWKClient(f"https://{settings.auth0_domain}/.well-known/jwks.json")


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify_password(hashed_password: str, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def create_access_token(user_id: UUID, username: str, email: EmailStr | None) -> str:
        payload_data = {
            "username": username,
            "user_id": str(user_id),
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
        }
        return jwt.encode(payload=payload_data, key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise InvalidCredentialsException()

    @staticmethod
    def decode_auth0_token(token: str) -> dict:
        try:
            signing_key = _jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.auth0_audience,
                issuer=f"https://{settings.auth0_domain}/",
            )
        except (jwt.PyJWKClientError, jwt.InvalidTokenError):
            raise InvalidCredentialsException()
        return payload

    @staticmethod
    def create_refresh_token(user_id: UUID, username: str, email: EmailStr | None) -> str:
        payload_data = {
            "username": username,
            "user_id": str(user_id),
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_refresh_expire_minutes),
        }
        return jwt.encode(payload=payload_data, key=settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_refresh_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.jwt_refresh_secret_key, algorithms=[settings.jwt_algorithm])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise InvalidCredentialsException()

    async def create_user(self, data: UserSignUpRequestSchema) -> User:
        data_dict = data.model_dump()
        data_dict["password"] = UserService.hash_password(data_dict["password"])
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

    async def update_user(self, user_id: UUID, current_user_id: UUID, data: UserUpdateRequestSchema) -> User:
        if user_id != current_user_id:
            raise ForbiddenException()
        if data.password is not None:
            data.password = PasswordHelper.hash_password(data.password)

        async with self.uow:
            user = await self.uow.users.update(user_id, data)
            await self.uow.commit()
            await self.uow.session.refresh(user)
        logger.info("User updated: id=%s", user_id)
        return user

    async def delete_user(self, user_id: UUID, current_user_id: UUID) -> None:
        if user_id != current_user_id:
            raise ForbiddenException()

        async with self.uow:
            await self.uow.users.delete(user_id)
            await self.uow.commit()
        logger.info("User deleted: id=%s", user_id)

    async def get_current_user(self, token: str) -> User:
        try:
            payload = UserService.decode_access_token(token)
        except InvalidCredentialsException:
            auth0_payload = UserService.decode_auth0_token(token)
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
                password=UserService.hash_password(uuid4().hex),
            )
            await self.uow.users.create(user)
            await self.uow.commit()
        logger.info("User created from Auth0: id=%s email=%s", user.id, user.email)
        return user

    async def authenticate_user(self, username: str, password: str) -> TokenResponseSchema:
        async with self.uow:
            user = await self.uow.users.get_by_username(username)
        if user is None or not UserService.verify_password(user.password, password):
            raise InvalidCredentialsException()
        logger.info("User authenticated: id=%s username=%s", user.id, user.username)

        return TokenResponseSchema(
            access_token=UserService.create_access_token(user.id, user.username, user.email),
            refresh_token=UserService.create_refresh_token(user.id, user.username, user.email),
            expires_in=settings.jwt_expire_minutes * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponseSchema:
        payload = UserService.decode_refresh_token(refresh_token)
        access_token = UserService.create_access_token(
            UUID(payload["user_id"]),
            payload["username"],
            payload["email"],
        )

        return TokenResponseSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_expire_minutes * 60,
        )

