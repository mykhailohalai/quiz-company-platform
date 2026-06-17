from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.company_member import InviteStatus, Role


class CompanyMemberInvitationCreate(BaseModel):
    user_id: UUID


class CompanyMemberRequestCreate(BaseModel):
    company_id: UUID


class CompanyMemberUpdateRequestSchema(BaseModel):
    status: InviteStatus | None = None
    role: Role | None = None


class CompanyMemberMembershipResponse(BaseModel):
    id: UUID
    company_id: UUID
    user_id: UUID
    role: Role
    status: InviteStatus

    model_config = ConfigDict(from_attributes=True)


class PaginatedCompanyMemberListResponse(BaseModel):
    members: list[CompanyMemberMembershipResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
