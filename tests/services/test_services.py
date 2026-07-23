from uuid import uuid4

import pytest

from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.models.user import User
from app.schemas.user import UserSignUpRequestSchema, UserUpdateRequestSchema



def make_user(**kwargs):
    defaults = dict(
        id=uuid4(),
        username="johndoe",
        email="john@example.com",
        password="hashed-password",
    )
    defaults.update(kwargs)
    return User(**defaults)


async def test_create_user_hashes_password_and_persists(service, uow):
    data = UserSignUpRequestSchema(username="johndoe", email="john@example.com", password="plain-password")

    user = await service.create_user(data)

    assert user.username == "johndoe"
    assert user.password != "plain-password"
    assert uow.users.users[user.id] is user
    assert uow.committed is True


async def test_create_user_raises_when_username_taken(service, uow):
    uow.users.users[uuid4()] = make_user(username="johndoe", email="other@example.com")
    data = UserSignUpRequestSchema(username="johndoe", email="new@example.com", password="plain-password")

    with pytest.raises(UserAlreadyExistsException):
        await service.create_user(data)


async def test_get_all_users_delegates_to_repository(service, uow):
    user = make_user()
    uow.users.users[user.id] = user

    users, total = await service.get_all_users(skip=0, limit=10)

    assert users == [user]
    assert total == 1


async def test_get_user_by_id_returns_user(service, uow):
    user = make_user()
    uow.users.users[user.id] = user

    result = await service.get_user_by_id(user.id)

    assert result is user


async def test_get_user_by_id_raises_when_missing(service):
    with pytest.raises(UserNotFoundException):
        await service.get_user_by_id(uuid4())


async def test_update_user_hashes_new_password(service, uow):
    user = make_user(password="old-hashed-password")
    uow.users.users[user.id] = user
    data = UserUpdateRequestSchema(password="new-plain-password")

    updated = await service.update_user(user.id, data)

    assert updated.password != "new-plain-password"
    assert updated.password != "old-hashed-password"
    assert uow.committed is True


async def test_update_user_keeps_password_when_not_provided(service, uow):
    user = make_user(password="old-hashed-password")
    uow.users.users[user.id] = user
    data = UserUpdateRequestSchema(username="newname")

    updated = await service.update_user(user.id, data)

    assert updated.username == "newname"
    assert updated.password == "old-hashed-password"


async def test_update_user_raises_when_missing(service):
    data = UserUpdateRequestSchema(username="newname")

    with pytest.raises(UserNotFoundException):
        await service.update_user(uuid4(), data)


async def test_delete_user_removes_from_repository(service, uow):
    user = make_user()
    uow.users.users[user.id] = user

    await service.delete_user(user.id)

    assert user.id not in uow.users.users
    assert uow.committed is True


async def test_delete_user_raises_when_missing(service):
    with pytest.raises(UserNotFoundException):
        await service.delete_user(uuid4())
