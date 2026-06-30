from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.models.user import User
from app.schemas.company_member import (
    CompanyMemberInvitationCreate,
    PaginatedCompanyMemberListResponse,
    CompanyMemberMembershipResponse,
    CompanyMemberRequestCreate,
)
from app.services.company_member_service import CompanyMemberService
from app.dependencies import get_current_user_dep, get_company_member_service

company_member_router = APIRouter()


@company_member_router.post(
    "/companies/{company_id}/invitations",
    response_model=CompanyMemberMembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invitation_to_user(
    data: CompanyMemberInvitationCreate,
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    invitation = await company_member_service.send_invitation(
        current_user.id, company_id, data
    )
    return CompanyMemberMembershipResponse.model_validate(invitation)


@company_member_router.delete(
    "/companies/{company_id}/invitations/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_invitation_by_owner(
    invitation_id: UUID,
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    await company_member_service.cancel_invitation(
        current_user.id, company_id, invitation_id
    )


@company_member_router.post(
    "/companies/{company_id}/invitations/{invitation_id}/accept",
    response_model=CompanyMemberMembershipResponse,
    status_code=status.HTTP_200_OK,
)
async def accept_invitation_by_user(
    invitation_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    invitation = await company_member_service.accept_invitation(
        current_user.id, invitation_id
    )
    return CompanyMemberMembershipResponse.model_validate(invitation)


@company_member_router.post(
    "/companies/{company_id}/invitations/{invitation_id}/decline",
    response_model=CompanyMemberMembershipResponse,
    status_code=status.HTTP_200_OK,
)
async def decline_invitation_by_user(
    invitation_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    invitation = await company_member_service.decline_invitation(
        current_user.id, invitation_id
    )
    return CompanyMemberMembershipResponse.model_validate(invitation)


@company_member_router.post(
    "/companies/{company_id}/requests",
    response_model=CompanyMemberMembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_join_request_by_user(
    data: CompanyMemberRequestCreate,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    request = await company_member_service.send_join_request(current_user.id, data)
    return CompanyMemberMembershipResponse.model_validate(request)


@company_member_router.delete(
    "/companies/{company_id}/requests/{join_request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def cancel_join_request_by_user(
    join_request_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    await company_member_service.cancel_join_request(current_user.id, join_request_id)


@company_member_router.post(
    "/companies/{company_id}/requests/{join_request_id}/accept",
    response_model=CompanyMemberMembershipResponse,
    status_code=status.HTTP_200_OK,
)
async def accept_join_request_by_owner(
    join_request_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    invitation = await company_member_service.accept_join_request(
        join_request_id, current_user.id
    )
    return CompanyMemberMembershipResponse.model_validate(invitation)


@company_member_router.post(
    "/companies/{company_id}/requests/{join_request_id}/decline",
    response_model=CompanyMemberMembershipResponse,
    status_code=status.HTTP_200_OK,
)
async def decline_join_request_by_owner(
    join_request_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    invitation = await company_member_service.decline_join_request(
        join_request_id, current_user.id
    )
    return CompanyMemberMembershipResponse.model_validate(invitation)


@company_member_router.delete(
    "/companies/{company_id}/members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_company_member(
    member_id: UUID,
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    await company_member_service.remove_member(member_id, company_id, current_user.id)


@company_member_router.delete(
    "/companies/{company_id}/members/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def leave_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    await company_member_service.leave_company(company_id, current_user.id)


@company_member_router.get(
    "/companies/{company_id}/members",
    response_model=PaginatedCompanyMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_company_members(
    company_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    members, total = await company_member_service.get_members(company_id, skip, limit)
    return PaginatedCompanyMemberListResponse(
        members=members,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@company_member_router.get(
    "/companies/{company_id}/invitations",
    response_model=PaginatedCompanyMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_invitations_by_company(
    company_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    invitations, total = await company_member_service.get_invitations_by_company(
        company_id, current_user.id, skip, limit
    )
    return PaginatedCompanyMemberListResponse(
        members=invitations,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@company_member_router.get(
    "/companies/{company_id}/requests",
    response_model=PaginatedCompanyMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_all_requests_by_company(
    company_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    requests, total = await company_member_service.get_requests_by_company(
        company_id, current_user.id, skip, limit
    )
    return PaginatedCompanyMemberListResponse(
        members=requests,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@company_member_router.get(
    "/me/invitations",
    response_model=PaginatedCompanyMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_invitations(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    invitations, total = await company_member_service.get_invitations_by_user(
        current_user.id, skip, limit
    )
    return PaginatedCompanyMemberListResponse(
        members=invitations,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@company_member_router.get(
    "/me/requests",
    response_model=PaginatedCompanyMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_my_requests(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    requests, total = await company_member_service.get_requests_by_user(
        current_user.id, skip, limit
    )
    return PaginatedCompanyMemberListResponse(
        members=requests,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@company_member_router.get(
    "/companies/{company_id}/admins",
    response_model=PaginatedCompanyMemberListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_admins(
    company_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    admins, total = await company_member_service.get_admins_by_company(
        company_id, current_user.id, skip, limit
    )
    return PaginatedCompanyMemberListResponse(
        members=admins,
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total,
    )


@company_member_router.patch(
    "/companies/{company_id}/members/{user_id}/appoint-admin",
    response_model=CompanyMemberMembershipResponse,
    status_code=status.HTTP_200_OK,
)
async def appoint_admin(
    user_id: UUID,
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    admin = await company_member_service.appoint_admin(company_id, user_id, current_user.id)
    return CompanyMemberMembershipResponse.model_validate(admin)


@company_member_router.patch(
    "/companies/{company_id}/members/{user_id}/remove-admin",
    response_model=CompanyMemberMembershipResponse,
    status_code=status.HTTP_200_OK,
)
async def remove_admin(
    user_id: UUID,
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_member_service: CompanyMemberService = Depends(get_company_member_service),
):
    admin = await company_member_service.remove_admin(
        company_id, user_id, current_user.id
    )
    return CompanyMemberMembershipResponse.model_validate(admin)
