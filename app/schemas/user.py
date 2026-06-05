from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID, uuid4


class UserSignInRequestSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=100)


class UserSignUpRequestSchema(BaseModel):
    fname: str | None = Field(default=None, max_length=50)
    sname: str | None = Field(default=None, max_length=50)
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdateRequestSchema(BaseModel):
    fname: str | None = Field(default=None, min_length=1, max_length=50)
    sname: str | None = Field(default=None, min_length=1, max_length=50)
    username: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=255)


class UserDetailResponseSchema(BaseModel):
    id: UUID
    fname: str | None = None
    sname: str | None = None
    username: str
    email: EmailStr | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponseSchema(BaseModel):
    users: list[UserDetailResponseSchema]
