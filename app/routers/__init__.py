from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis.asyncio import Redis
from uuid import UUID
import logging

from app import schemas
from app.core.database import get_db
from app.core.redis import get_redis
from app.schemas.user import UserSignUpRequestSchema, UserDetailResponseSchema, UserListResponseSchema, UserUpdateRequestSchema
from app.utils.unit_of_work import UnitOfWork
from app.models.user import User 

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=schemas.HealthSchema)
async def health_check():
    return schemas.HealthSchema(
        status_code=status.HTTP_200_OK, detail="ok", result="working"
    )


# check if db connected
@router.get("/db-health", response_model=schemas.HealthSchema)
async def db_health_check(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return schemas.HealthSchema(
        status_code=status.HTTP_200_OK, detail="ok", result="db connected"
    )


# check if redis connected
@router.get("/redis-health", response_model=schemas.HealthSchema)
async def redis_health_check(redis: Redis = Depends(get_redis)):
    await redis.ping()
    return schemas.HealthSchema(
        status_code=status.HTTP_200_OK, detail="ok", result="redis connected"
    )


@router.post(
    "/users", 
    response_model=UserDetailResponseSchema, 
    status_code=status.HTTP_201_CREATED
    )
async def create_user(user_request: UserSignUpRequestSchema):
    logger.info(f"Creating user: {user_request.__dict__}")
    async with UnitOfWork() as uow:
        user = User(**user_request.model_dump())
        await uow.users.create(user)
        await uow.commit()
    logger.info(f"User created: {user_request.__dict__}")

    return user


@router.get(
    "/users", 
    response_model=UserListResponseSchema,
    status_code=status.HTTP_200_OK
    )
async def get_all_users():
    async with UnitOfWork() as uow:
        users = await uow.users.get_all()
    return UserListResponseSchema(users=users)


@router.get(
    "/users/{user_id}",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: UUID):
    async with UnitOfWork() as uow:
        user = await uow.users.get_by_id(user_id)
    return user


@router.patch(
    "/users/{user_id}",
    response_model=UserDetailResponseSchema,
    status_code=status.HTTP_200_OK
    )
async def update_user_details(
    user_id: UUID, 
    updated_user: UserUpdateRequestSchema
    ):
    async with UnitOfWork() as uow:
        user = await uow.users.update(user_id, updated_user)
        await uow.commit()
        await uow.session.refresh(user)
    
    return user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
    )
async def delete_user_by_id(user_id: UUID):
    async with UnitOfWork() as uow:
        result = await uow.users.delete(user_id)
        await uow.commit()
        return result