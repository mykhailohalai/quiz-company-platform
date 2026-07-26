from unittest.mock import AsyncMock, MagicMock

import pytest

from app.dependencies import get_company_member_service, get_company_service, get_user_service
from app.services.user_service import UserService
from app.services.company_service import CompanyService
from app.services.company_member_service import CompanyMemberService
from app.services.notification_service import NotificationService
from app.services.quiz_service import QuizService
from app.services.redis_service import RedisService
from main import app
from fakes.fake_unit_of_work import FakeUnitOfWork


@pytest.fixture
def uow():
    return FakeUnitOfWork()


@pytest.fixture
def service(uow):
    return UserService(uow)


@pytest.fixture
def company_service(uow):
    return CompanyService(uow)


@pytest.fixture
def mock_user_service(uow):
    user_service = MagicMock()
    app.dependency_overrides[get_user_service] = lambda: user_service

    yield user_service

    app.dependency_overrides.clear()


@pytest.fixture
def mock_company_service(uow):
    company_service = MagicMock()
    app.dependency_overrides[get_company_service] = lambda: company_service

    yield company_service

    app.dependency_overrides.clear()


@pytest.fixture
def company_member_service(uow):
    return CompanyMemberService(uow)


@pytest.fixture
def mock_redis_service():
    service = MagicMock(spec=RedisService)
    service.save_quiz_answers_redis = AsyncMock()
    return service


@pytest.fixture
def notification_service(uow):
    return NotificationService(uow)


@pytest.fixture
def quiz_service(uow, mock_redis_service, notification_service):
    return QuizService(uow, mock_redis_service, notification_service)


@pytest.fixture
def mock_company_member_service():
    company_member_service = MagicMock()
    app.dependency_overrides[get_company_member_service] = lambda: company_member_service

    yield company_member_service

    app.dependency_overrides.clear()
