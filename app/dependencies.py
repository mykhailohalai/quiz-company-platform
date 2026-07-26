from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.user import User
from app.services.user_service import UserService, get_user_service


async def get_current_user_dep(
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service)
) -> User:
    return await user_service.get_current_user(user_details.credentials)
    