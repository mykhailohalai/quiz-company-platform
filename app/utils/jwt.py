from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pydantic import EmailStr
from app.core import settings
from app.exceptions.user_exceptions import InvalidCredentialsException

class JWTHelper():
    @staticmethod
    def create_access_token(user_id: UUID, username: str, email: EmailStr | None):
        payload_data = {
            "username": username,
            "user_id": str(user_id),
            "email": email,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.jwt_expire_minutes),
        }
        secret_key = settings.jwt_secret_key
        
        token = jwt.encode(
            payload=payload_data,
            key=secret_key,
            algorithm=settings.jwt_algorithm
        )

        return token

    @staticmethod
    def decode_access_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise InvalidCredentialsException()
