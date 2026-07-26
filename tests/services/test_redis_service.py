import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.schemas.quiz_result import QuizAnswerRedisSchema
from app.services.redis_service import RedisService


def make_redis_answer(**kwargs):
    defaults = dict(
        user_id=uuid4(),
        company_id=uuid4(),
        quiz_id=uuid4(),
        question_id=uuid4(),
        answer_ids=[uuid4()],
        is_correct=True,
        answered_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return QuizAnswerRedisSchema(**defaults)


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.set = AsyncMock()
    redis.get = AsyncMock()
    return redis


@pytest.fixture
def redis_service(mock_redis):
    return RedisService(mock_redis)


async def test_save_quiz_answers_uses_correct_key(redis_service, mock_redis):
    answer = make_redis_answer()
    user_id, company_id, quiz_id = answer.user_id, answer.company_id, answer.quiz_id

    await redis_service.save_quiz_answers_redis(user_id, company_id, quiz_id, [answer])

    call_args = mock_redis.set.call_args
    assert call_args[0][0] == f"answers:{company_id}:{quiz_id}:{user_id}"


async def test_save_quiz_answers_sets_correct_ttl(redis_service, mock_redis):
    answer = make_redis_answer()

    await redis_service.save_quiz_answers_redis(
        answer.user_id, answer.company_id, answer.quiz_id, [answer]
    )

    call_kwargs = mock_redis.set.call_args[1]
    assert call_kwargs["ex"] == 172800


async def test_save_quiz_answers_serializes_to_json(redis_service, mock_redis):
    answer = make_redis_answer()

    await redis_service.save_quiz_answers_redis(
        answer.user_id, answer.company_id, answer.quiz_id, [answer]
    )

    stored_data = mock_redis.set.call_args[0][1]
    parsed = json.loads(stored_data)

    assert len(parsed) == 1
    assert parsed[0]["question_id"] == str(answer.question_id)
    assert parsed[0]["is_correct"] == answer.is_correct
    assert parsed[0]["answer_ids"] == [str(a) for a in answer.answer_ids]


async def test_save_quiz_answers_stores_multiple_answers(redis_service, mock_redis):
    quiz_id = uuid4()
    company_id = uuid4()
    user_id = uuid4()
    answers = [
        make_redis_answer(quiz_id=quiz_id, company_id=company_id, user_id=user_id)
        for _ in range(3)
    ]

    await redis_service.save_quiz_answers_redis(user_id, company_id, quiz_id, answers)

    stored_data = mock_redis.set.call_args[0][1]
    parsed = json.loads(stored_data)
    assert len(parsed) == 3


async def test_get_quiz_answers_uses_correct_key(redis_service, mock_redis):
    user_id, company_id, quiz_id = uuid4(), uuid4(), uuid4()
    mock_redis.get.return_value = None

    await redis_service.get_quiz_answers_redis(user_id, company_id, quiz_id)

    mock_redis.get.assert_awaited_once_with(f"answers:{company_id}:{quiz_id}:{user_id}")


async def test_get_quiz_answers_returns_none_when_missing(redis_service, mock_redis):
    mock_redis.get.return_value = None

    result = await redis_service.get_quiz_answers_redis(uuid4(), uuid4(), uuid4())

    assert result is None


async def test_get_quiz_answers_deserializes_stored_answers(redis_service, mock_redis):
    answer = make_redis_answer()
    mock_redis.get.return_value = json.dumps([answer.model_dump(mode="json")])

    result = await redis_service.get_quiz_answers_redis(
        answer.user_id, answer.company_id, answer.quiz_id
    )

    assert len(result) == 1
    assert result[0].question_id == answer.question_id
    assert result[0].is_correct == answer.is_correct


async def test_get_quiz_answers_deserializes_multiple_answers(redis_service, mock_redis):
    answers = [make_redis_answer() for _ in range(3)]
    mock_redis.get.return_value = json.dumps([a.model_dump(mode="json") for a in answers])

    result = await redis_service.get_quiz_answers_redis(uuid4(), uuid4(), uuid4())

    assert len(result) == 3
