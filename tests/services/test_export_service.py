from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.exceptions.general_exceptions import ForbiddenException
from app.models.company import Company, CompanyVisibility
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.models.quiz_result import QuizResult
from app.schemas.quiz_result import QuizAnswerRedisSchema
from app.utils.formatter import Formatter


def make_company(**kwargs):
    defaults = dict(
        id=uuid4(), name="Acme", description="desc",
        owner_id=uuid4(), visibility=CompanyVisibility.Visible_to_all,
    )
    defaults.update(kwargs)
    return Company(**defaults)


def make_member(**kwargs):
    defaults = dict(
        id=uuid4(), company_id=uuid4(), user_id=uuid4(),
        role=Role.MEMBER, status=InviteStatus.ACTIVE,
    )
    defaults.update(kwargs)
    return CompanyMember(**defaults)


def make_quiz_result(**kwargs):
    defaults = dict(
        id=uuid4(), user_id=uuid4(), quiz_id=uuid4(),
        company_id=uuid4(), correct_answers=3, total_questions=5,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return QuizResult(**defaults)


def make_redis_answer(**kwargs):
    defaults = dict(
        user_id=uuid4(), company_id=uuid4(), quiz_id=uuid4(),
        question_id=uuid4(), answer_ids=[uuid4()],
        is_correct=True, answered_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return QuizAnswerRedisSchema(**defaults)


# --- Formatter ---

def test_formatter_generates_csv_headers():
    result = make_quiz_result()
    csv_output = Formatter.quiz_results_to_csv([result])
    assert "user_id" in csv_output
    assert "correct_answers" in csv_output
    assert "score_percentage" in csv_output


def test_formatter_generates_correct_row():
    result = make_quiz_result(correct_answers=4, total_questions=5)
    csv_output = Formatter.quiz_results_to_csv([result])
    assert "80.0" in csv_output


def test_formatter_handles_empty_list():
    csv_output = Formatter.quiz_results_to_csv([])
    lines = csv_output.strip().split("\n")
    assert len(lines) == 1


def test_formatter_generates_multiple_rows():
    results = [make_quiz_result() for _ in range(3)]
    csv_output = Formatter.quiz_results_to_csv(results)
    lines = csv_output.strip().split("\n")
    assert len(lines) == 4  # header + 3 rows


# --- get_quiz_results_for_export ---

async def test_get_quiz_results_for_export_returns_results(quiz_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    quiz_id = uuid4()
    r1 = make_quiz_result(company_id=company.id, quiz_id=quiz_id)
    r2 = make_quiz_result(company_id=company.id, quiz_id=quiz_id)
    uow.companies.companies[company.id] = company
    uow.quiz_results.results[r1.id] = r1
    uow.quiz_results.results[r2.id] = r2

    results = await quiz_service.get_quiz_results_for_export(owner_id, company.id, quiz_id)

    assert len(results) == 2


async def test_get_quiz_results_for_export_raises_when_not_owner_or_admin(quiz_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    with pytest.raises(ForbiddenException):
        await quiz_service.get_quiz_results_for_export(uuid4(), company.id, uuid4())


# --- get_my_quiz_result ---

async def test_get_my_quiz_result_returns_from_redis(quiz_service, mock_redis_service):
    user_id, company_id, quiz_id = uuid4(), uuid4(), uuid4()
    redis_answers = [make_redis_answer(user_id=user_id, company_id=company_id, quiz_id=quiz_id)]
    mock_redis_service.get_quiz_answers_redis = AsyncMock(return_value=redis_answers)

    result = await quiz_service.get_my_quiz_result(user_id, company_id, quiz_id)

    assert result == redis_answers
    mock_redis_service.get_quiz_answers_redis.assert_called_once_with(user_id, company_id, quiz_id)


async def test_get_my_quiz_result_falls_back_to_db_when_redis_empty(quiz_service, uow, mock_redis_service):
    user_id = uuid4()
    quiz_id = uuid4()
    company_id = uuid4()
    db_result = make_quiz_result(user_id=user_id, quiz_id=quiz_id, company_id=company_id)
    uow.quiz_results.results[db_result.id] = db_result
    mock_redis_service.get_quiz_answers_redis = AsyncMock(return_value=None)

    result = await quiz_service.get_my_quiz_result(user_id, company_id, quiz_id)

    assert result == db_result
