from uuid import UUID

from app.routers import router
from app.schemas.user import (
    PaginatedUserDetailResponseSchema,
    UserDetailResponseSchema,
    UserSignUpRequestSchema,
    UserUpdateRequestSchema,
)
from fastapi import Depends, Query, status

from app.services.user_service import UserService, get_user_service


@router.post(
    "/users",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_request: UserSignUpRequestSchema,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.create_user(user_request)


@router.get(
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


@router.get(
    "/users/{user_id}",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    return await user_service.get_user_by_id(user_id)


@router.patch(
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


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    await user_service.delete_user(user_id)
