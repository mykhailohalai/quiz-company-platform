from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from redis.asyncio import Redis

from app import schemas
from app.core.database import get_db
from app.core.redis import get_redis

router = APIRouter()


@router.get("/", response_model=schemas.HealthSchema)
async def health_check():
    return schemas.HealthSchema(status_code=200, detail="ok", result="working")


# check if db connected
@router.get("/db-health", response_model=schemas.HealthSchema)
async def db_health_check(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return schemas.HealthSchema(status_code=200, detail="ok", result="db connected")


# check if redis connected
@router.get("/redis-health", response_model=schemas.HealthSchema)
async def redis_health_check(redis: Redis = Depends(get_redis)):
    await redis.ping()
    return schemas.HealthSchema(status_code=200, detail="ok", result="redis connected")
