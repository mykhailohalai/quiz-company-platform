from unittest.mock import MagicMock

import pytest

from app.services.user_service import UserService, get_user_service
from main import app
from fakes.fake_unit_of_work import FakeUnitOfWork


@pytest.fixture
def uow():
    return FakeUnitOfWork()


@pytest.fixture
def service(uow):
    return UserService(uow)


@pytest.fixture
def mock_user_service(uow):
    user_service = MagicMock()
    app.dependency_overrides[get_user_service] = lambda: user_service

    yield user_service

    app.dependency_overrides.clear()
