from collections.abc import AsyncGenerator
from redis.asyncio import Redis

from app.core import settings

redis_client = Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    decode_responses=True,
)


async def get_redis() -> AsyncGenerator[Redis, None]:
    async with redis_client as redis:
        yield redis
