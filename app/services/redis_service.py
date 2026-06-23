import json
from uuid import UUID

from fastapi import Depends
from redis.asyncio import Redis

from app.core.redis import get_redis
from app.schemas.quiz_result import QuizAnswerRedisSchema


class RedisService:

    def __init__(self, redis: Redis):
        self.redis = redis

    async def save_quiz_answers_redis(
        self,
        user_id: UUID,
        company_id: UUID,
        quiz_id: UUID,
        answers: list[QuizAnswerRedisSchema],
        ttl=172800,
    ):
        data = json.dumps([a.model_dump(mode="json") for a in answers])

        return await self.redis.set(
            f"answers:{company_id}:{quiz_id}:{user_id}", data, ex=ttl
        )
