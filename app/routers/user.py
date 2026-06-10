from uuid import UUID

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.token import TokenResponseSchema
from app.schemas.user import (
    PaginatedUserDetailResponseSchema,
    UserDetailResponseSchema,
    UserSignInRequestSchema,
    UserSignUpRequestSchema,
    UserUpdateRequestSchema,
)
from fastapi import APIRouter, Depends, Query, Security, status

from app.services.user_service import UserService, get_user_service

user_router = APIRouter()


@user_router.post(
    "/users",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_request: UserSignUpRequestSchema,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_user(user_request)


@user_router.get(
    "/users",
    response_model=PaginatedUserDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    user_service: UserService = Depends(get_user_service),
):
    users, total = await user_service.get_all_users(skip, limit)
    return PaginatedUserDetailResponseSchema(
        users=users,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@user_router.get(
    "/users/{user_id}",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user_by_id(user_id)


@user_router.patch(
    "/users/{user_id}",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def update_user_details(
    user_id: UUID,
    updated_data: UserUpdateRequestSchema,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(user_id, updated_data)


@user_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_user(user_id)


@user_router.post(
    "/login", 
    response_model=TokenResponseSchema, 
    status_code=status.HTTP_200_OK
)
async def user_login(
    user: UserSignInRequestSchema,
    user_service: UserService = Depends(get_user_service),
):
    token = await user_service.authenticate_user(user.username, user.password)
    return token


@user_router.get(
    "/me",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def user_profile(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_current_user(credentials.credentials)
