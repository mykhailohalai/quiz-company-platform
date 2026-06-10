import jwt
from jwt import PyJWKClient
from fastapi import APIRouter, Depends, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core import settings
from app.exceptions.user_exceptions import InvalidCredentialsException
from app.schemas.user import UserDetailResponseSchema
from app.services.user_service import UserService, get_user_service

auth0_router = APIRouter(prefix="/auth0", tags=["auth0"])

jwks_client = PyJWKClient(f"https://{settings.auth0_domain}/.well-known/jwks.json")


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


@auth0_router.get(
    "/me",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def auth0_profile(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
):
    payload = decode_auth0_token(credentials.credentials)
    return await user_service.get_or_create_user_from_auth0(payload["email"])
