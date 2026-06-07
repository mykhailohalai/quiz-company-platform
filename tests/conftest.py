from unittest.mock import MagicMock

import pytest

from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.services.user_service import UserService, get_user_service
from main import app

class FakeUserRepository:
    def __init__(self, users=None):
        self.users = {user.id: user for user in (users or [])}

    async def get_all(self, skip=0, limit=10):
        users = list(self.users.values())
        return users[skip : skip + limit], len(users)

    async def get_by_id(self, user_id):
        user = self.users.get(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        return user

    async def create(self, user):
        for existing in self.users.values():
            if existing.username == user.username:
                raise UserAlreadyExistsException("username")
            if user.email is not None and existing.email == user.email:
                raise UserAlreadyExistsException("email")
        self.users[user.id] = user
        return user

    async def delete(self, user_id):
        if user_id not in self.users:
            raise UserNotFoundException(user_id)
        del self.users[user_id]
        return True

    async def update(self, user_id, updated_user):
        user = self.users.get(user_id)
        if user is None:
            raise UserNotFoundException(user_id)
        for field, value in updated_user.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        return user


class FakeSession:
    async def refresh(self, instance):
        pass


class FakeUnitOfWork:
    def __init__(self, users=None):
        self.users = FakeUserRepository(users)
        self.session = FakeSession()
        self.committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()

    async def commit(self):
        self.committed = True

    async def rollback(self):
        pass


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
