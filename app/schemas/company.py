from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.models.company import CompanyVisibility
from app.schemas.user import UserDetailResponseSchema

class CompanyCreateRequestSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1500)  
    visibility: CompanyVisibility = Field(default=CompanyVisibility.Visible_to_all)


class CompanyUpdateRequestSchema(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=1500)
    visibility: CompanyVisibility | None = Field(default=None)


class CompanyDetailResponseSchema(BaseModel):
    id: UUID 
    name: str 
    description: str | None = None
    owner_id: UUID 
    owner: UserDetailResponseSchema
    visibility: CompanyVisibility 

    model_config = ConfigDict(from_attributes=True)


class PaginatedCompanyDetailResponseSchema(BaseModel):
    companies: list[CompanyDetailResponseSchema]
    total: int
    skip: int
    limit: int
    has_more: bool
