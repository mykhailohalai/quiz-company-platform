from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest

from app.models.user import User
from app.schemas.user import UserSignUpRequestSchema, UserUpdateRequestSchema
from main import app
from fastapi import status


client = TestClient(app)

now = datetime.now()


async def get_all_users(skip, limit):
    users = [
        User(
            id=uuid4(),
            username="user2",
            email="user2@example.com",
            password="hashed-password",
            created_at=now,
            updated_at=now,
        )
    ]
    return users, len(users)

async def create_user(user_request: UserSignUpRequestSchema):
    user = User(
        id=uuid4(),
        username=user_request.username,
        email=user_request.email,
        password=user_request.password,
        created_at=now,
        updated_at=now,
    )
    return user


async def get_user_by_id(user_id):
    return User(
        id=user_id,
        username="user2",
        email="user2@example.com",
        password="hashed-password",
        created_at=now,
        updated_at=now,
    )


async def update_user(user_id, current_user_id, updated_data: UserUpdateRequestSchema):
    return User(
        id=user_id,
        username=updated_data.username,
        email="user2@example.com",
        password="hashed-password",
        created_at=now,
        updated_at=now,
    )


async def delete_user(user_id, current_user_id):
    return None


async def get_current_user(token):
    return User(
        id=uuid4(),
        username="user2",
        email="user2@example.com",
        password="hashed-password",
        created_at=now,
        updated_at=now,
    )


def test_get_all_users_should_success(mock_user_service):
    mock_user_service.get_all_users = get_all_users

    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK


def test_create_user_return_user(mock_user_service):
    mock_user_service.create_user = create_user

    response = client.post(
        "/users",
        json={
            "fname": "string",
            "sname": "string",
            "username": "stringehjekg2",
            "email": "usfewfefe2er@example.com",
            "password": "stringethethtehethst",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["username"] == "stringehjekg2"
    assert body["email"] == "usfewfefe2er@example.com"
    assert "password" not in body


def test_get_user_by_id_should_success(mock_user_service):
    mock_user_service.get_user_by_id = get_user_by_id
    user_id = uuid4()

    response = client.get(f"/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(user_id)
    assert body["username"] == "user2"
    assert body["email"] == "user2@example.com"
    assert "password" not in body


def test_update_user_details_should_success(mock_user_service):
    mock_user_service.update_user = update_user
    mock_user_service.get_current_user = get_current_user
    user_id = uuid4()

    response = client.patch(
        f"/users/{user_id}",
        json={"username": "updatedname"},
        headers={"Authorization": "Bearer faketoken"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(user_id)
    assert body["username"] == "updatedname"
    assert "password" not in body


def test_delete_user_by_id_should_success(mock_user_service):
    mock_user_service.delete_user = delete_user
    mock_user_service.get_current_user = get_current_user
    user_id = uuid4()

    response = client.delete(
        f"/users/{user_id}",
        headers={"Authorization": "Bearer faketoken"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
