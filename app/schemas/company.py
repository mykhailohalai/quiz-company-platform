from uuid import UUID

from pydantic import BaseModel, Field
from app.models.company import CompanyVisibility
from app.models.user import User

class CompanyCreateRequestSchema(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1500)  
    visibility: CompanyVisibility | None = Field(default=CompanyVisibility.Visible_to_all)


class CompanyUpdateRequestSchema(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1500)
    visibility: CompanyVisibility | None = Field(default=None)


class CompanyDetailResponseSchema(BaseModel):
    id: UUID 
    name: str 
    description: str | None = None
    owner_id: UUID 
    owner: User 
    visibility: CompanyVisibility 


class PaginatedUserDetailResponseSchema(BaseModel):
    companies: list[CompanyDetailResponseSchema]
    total: int
    skip: int
    limit: int
    has_more: bool
