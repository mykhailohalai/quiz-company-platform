from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID, uuid4


class UserSignInRequestSchema(BaseModel):
    username: str
    password: str
    email: EmailStr | None = None


class UserSignUpRequestSchema(BaseModel):
    fname: str
    sname: str
    username: str
    email: EmailStr | None = None
    password: str = Field(min_length=8)


class UserUpdateRequestSchema(BaseModel):
    fname: str | None = None
    sname: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)


class UserDetailResponseSchema(BaseModel):
    id: UUID
    fname: str
    sname: str
    username: str
    email: EmailStr | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponseSchema(BaseModel):
    users: list[UserDetailResponseSchema]