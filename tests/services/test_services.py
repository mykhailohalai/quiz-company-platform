from uuid import uuid4

import pytest

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.user_exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.models.user import User
from app.schemas.user import UserSignUpRequestSchema, UserUpdateRequestSchema
from app.utils.jwt import JWTHelper
from app.utils.password import PasswordHelper



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

    updated = await service.update_user(user.id, user.id, data)

    assert updated.password != "new-plain-password"
    assert updated.password != "old-hashed-password"
    assert uow.committed is True


async def test_update_user_keeps_password_when_not_provided(service, uow):
    user = make_user(password="old-hashed-password")
    uow.users.users[user.id] = user
    data = UserUpdateRequestSchema(username="newname")

    updated = await service.update_user(user.id, user.id, data)

    assert updated.username == "newname"
    assert updated.password == "old-hashed-password"


async def test_update_user_raises_when_missing(service):
    user_id = uuid4()
    data = UserUpdateRequestSchema(username="newname")

    with pytest.raises(UserNotFoundException):
        await service.update_user(user_id, user_id, data)


async def test_update_user_raises_when_not_owner(service, uow):
    user = make_user()
    uow.users.users[user.id] = user
    data = UserUpdateRequestSchema(username="newname")

    with pytest.raises(ForbiddenException):
        await service.update_user(user.id, uuid4(), data)


async def test_delete_user_removes_from_repository(service, uow):
    user = make_user()
    uow.users.users[user.id] = user

    await service.delete_user(user.id, user.id)

    assert user.id not in uow.users.users
    assert uow.committed is True


async def test_delete_user_raises_when_missing(service):
    user_id = uuid4()

    with pytest.raises(UserNotFoundException):
        await service.delete_user(user_id, user_id)


async def test_delete_user_raises_when_not_owner(service, uow):
    user = make_user()
    uow.users.users[user.id] = user

    with pytest.raises(ForbiddenException):
        await service.delete_user(user.id, uuid4())


async def test_authenticate_user_returns_token_for_valid_credentials(service, uow):
    user = make_user(password=PasswordHelper.hash_password("plain-password"))
    uow.users.users[user.id] = user

    token = await service.authenticate_user("johndoe", "plain-password")

    assert token.access_token
    assert token.token_type == "bearer"


async def test_authenticate_user_raises_when_user_missing(service):
    with pytest.raises(InvalidCredentialsException):
        await service.authenticate_user("johndoe", "plain-password")


async def test_authenticate_user_raises_when_password_invalid(service, uow):
    user = make_user(password=PasswordHelper.hash_password("plain-password"))
    uow.users.users[user.id] = user

    with pytest.raises(InvalidCredentialsException):
        await service.authenticate_user("johndoe", "wrong-password")


async def test_get_current_user_returns_user_for_valid_token(service, uow):
    user = make_user()
    uow.users.users[user.id] = user
    token = JWTHelper.create_access_token(user.id, user.username, user.email)

    result = await service.get_current_user(token)

    assert result is user


async def test_refresh_access_token_returns_new_access_token(service, uow):
    user = make_user()
    uow.users.users[user.id] = user
    refresh_token = JWTHelper.create_refresh_token(user.id, user.username, user.email)

    token = await service.refresh_access_token(refresh_token)

    assert token.access_token
    assert token.refresh_token == refresh_token


async def test_refresh_access_token_raises_for_invalid_token(service):
    with pytest.raises(InvalidCredentialsException):
        await service.refresh_access_token("invalid-token")


async def test_get_or_create_user_from_auth0_returns_existing_user(service, uow):
    user = make_user(email="existing@example.com")
    uow.users.users[user.id] = user

    result = await service.get_or_create_user_from_auth0("existing@example.com")

    assert result is user
    assert uow.committed is False


async def test_get_or_create_user_from_auth0_creates_new_user(service, uow):
    result = await service.get_or_create_user_from_auth0("newuser@example.com")

    assert result.email == "newuser@example.com"
    assert result.username == "newuser"
    assert uow.users.users[result.id] is result
    assert uow.committed is True


async def test_get_or_create_user_from_auth0_resolves_username_conflict(service, uow):
    existing = make_user(username="newuser", email="newuser_old@example.com")
    uow.users.users[existing.id] = existing

    result = await service.get_or_create_user_from_auth0("newuser@example.com")

    assert result.email == "newuser@example.com"
    assert result.username != "newuser"
    assert result.username.startswith("newuser_")
