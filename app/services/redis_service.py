import json
from uuid import UUID
import logging

from redis.asyncio import Redis

from app.schemas.quiz_result import QuizAnswerRedisSchema

logger = logging.getLogger(__name__)


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
        key = f"answers:{company_id}:{quiz_id}:{user_id}"
        data = json.dumps([a.model_dump(mode="json") for a in answers])

        await self.redis.set(key, data, ex=ttl)
        logger.info(
            "Quiz answers saved to Redis: key=%s answers=%d ttl=%d",
            key, len(answers), ttl,
        )
