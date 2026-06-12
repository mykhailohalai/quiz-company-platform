from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID


class UserSignInRequestSchema(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=8, max_length=255)


class UserSignUpRequestSchema(BaseModel):
    fname: str | None = Field(default=None, max_length=50)
    lname: str | None = Field(default=None, max_length=50)
    username: str = Field(..., min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=100)
    password: str = Field(..., min_length=8, max_length=255)


class UserUpdateRequestSchema(BaseModel):
    fname: str | None = Field(default=None, min_length=1, max_length=50)
    lname: str | None = Field(default=None, min_length=1, max_length=50)
    username: str | None = Field(default=None, min_length=1, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=255)


class UserDetailResponseSchema(BaseModel):
    id: UUID
    fname: str | None = None
    lname: str | None = None
    username: str
    email: EmailStr | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedUserDetailResponseSchema(BaseModel):
    users: list[UserDetailResponseSchema]
    total: int 
    skip: int
    limit: int
    has_more: bool
