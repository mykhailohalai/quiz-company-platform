from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pydantic import EmailStr
from app.core import settings
from app.exceptions.user_exceptions import InvalidCredentialsException

jwks_client = jwt.PyJWKClient(f"https://{settings.auth0_domain}/.well-known/jwks.json")

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

    @staticmethod
    def decode_auth0_token(token: str) -> dict:
        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token)
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
    def create_refresh_token(user_id: UUID, username: str, email: EmailStr | None):
        payload_data = {
            "username": username,
            "user_id": str(user_id),
            "email": email,
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.jwt_refresh_expire_minutes),
        }
        secret_key = settings.jwt_refresh_secret_key

        token = jwt.encode(
            payload=payload_data, key=secret_key, algorithm=settings.jwt_algorithm
        )

        return token

    @staticmethod
    def decode_refresh_token(token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.jwt_refresh_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            raise InvalidCredentialsException()
