from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis.asyncio import Redis
from uuid import UUID
import logging

from app import schemas
from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.user import (
    UserSignUpRequestSchema,
    UserDetailResponseSchema,
    UserUpdateRequestSchema,
    PaginatedUserDetailResponseSchema,
)
from app.services.user_service import UserService, get_user_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=schemas.HealthSchema)
async def health_check():
    return schemas.HealthSchema(
        status_code=status.HTTP_200_OK, detail="ok", result="working"
    )


@router.get("/db-health", response_model=schemas.HealthSchema)
async def db_health_check(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return schemas.HealthSchema(
        status_code=status.HTTP_200_OK, detail="ok", result="db connected"
    )


@router.get("/redis-health", response_model=schemas.HealthSchema)
async def redis_health_check(redis: Redis = Depends(get_redis)):
    await redis.ping()
    return schemas.HealthSchema(
        status_code=status.HTTP_200_OK, detail="ok", result="redis connected"
    )


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
