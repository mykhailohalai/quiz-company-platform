from uuid import UUID

from app.schemas.token import RefreshTokenRequestSchema, TokenResponseSchema
from app.schemas.user import (
    PaginatedUserDetailResponseSchema,
    UserDetailResponseSchema,
    UserSignInRequestSchema,
    UserSignUpRequestSchema,
    UserUpdateRequestSchema,
)
from fastapi import APIRouter, Depends, Query, status

from app.models.user import User
from app.services.user_service import UserService
from app.dependencies import get_current_user_dep, get_user_service

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
    current_user: User = Depends(get_current_user_dep),
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.update_user(user_id, current_user.id, updated_data)


@user_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_user(user_id, current_user.id)


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
async def get_user_profile(
    current_user: User = Depends(get_current_user_dep),
):
    return current_user


@user_router.post(
    "/refresh",
    response_model= TokenResponseSchema,
    status_code=status.HTTP_200_OK
)
async def update_access_token(
    data: RefreshTokenRequestSchema, 
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.refresh_access_token(data.refresh_token)
