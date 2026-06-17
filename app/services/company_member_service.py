from uuid import UUID

from fastapi import Depends

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.company_member_exceptions import CompanyMemberNotFoundException
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.utils.unit_of_work import UnitOfWork, get_uow
from app.schemas.company_member import CompanyMemberInvitationCreate, CompanyMemberRequestCreate


class CompanyMemberService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def send_invitation(
        self,
        current_user_id: UUID,
        company_id: UUID,
        data: CompanyMemberInvitationCreate,
    ) -> CompanyMember:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            invitation = CompanyMember(
                company_id=company_id,
                user_id=data.user_id,
                role=Role.Member,
                status=InviteStatus.Pending_invite,
            )
            await self.uow.company_members.create(invitation)
            await self.uow.commit()

        return invitation

    async def cancel_invitation(
        self, current_user_id: UUID, company_id: UUID, invitation_id: UUID
    ) -> None:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            await self.uow.company_members.delete(invitation_id)
            await self.uow.commit()

    async def accept_invitation(
        self, current_user_id: UUID, invitation_id: UUID
    ) -> CompanyMember:
        async with self.uow:
            invitation = await self.uow.company_members.get_by_id(invitation_id)
            if current_user_id != invitation.user_id:
                raise ForbiddenException()

            invitation.status = InviteStatus.Active
            await self.uow.commit()
        return invitation

    async def decline_invitation(
        self, current_user_id: UUID, invitation_id: UUID
    ) -> CompanyMember:
        async with self.uow:
            invitation = await self.uow.company_members.get_by_id(invitation_id)
            if current_user_id != invitation.user_id:
                raise ForbiddenException()

            invitation.status = InviteStatus.Rejected
            await self.uow.commit()
        return invitation

    async def send_join_request(self, user_id: UUID, data: CompanyMemberRequestCreate) -> CompanyMember:
        async with self.uow:
            request = CompanyMember(
                company_id=data.company_id,
                user_id=user_id,
                role=Role.Member,
                status=InviteStatus.Pending_request,
            )
            await self.uow.company_members.create(request)
            await self.uow.commit()
        return request

    async def cancel_join_request(self, user_id: UUID, join_request_id: UUID) -> None:
        async with self.uow:
            join_request = await self.uow.company_members.get_by_id(join_request_id)
            if user_id != join_request.user_id:
                raise ForbiddenException()

            await self.uow.company_members.delete(join_request_id)
            await self.uow.commit()

    async def accept_join_request(self, join_request_id: UUID, current_user_id: UUID) -> CompanyMember:
        async with self.uow:
            request = await self.uow.company_members.get_by_id(join_request_id)
            company = await self.uow.companies.get_by_id(request.company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            request.status = InviteStatus.Active
            await self.uow.commit()
        return request

    async def decline_join_request(self, join_request_id: UUID, current_user_id: UUID) -> CompanyMember:
        async with self.uow:
            request = await self.uow.company_members.get_by_id(join_request_id)
            company = await self.uow.companies.get_by_id(request.company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            request.status = InviteStatus.Rejected
            await self.uow.commit()
        return request

    async def remove_member(self, member_id: UUID, company_id: UUID, current_user_id: UUID) -> None:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            await self.uow.company_members.delete(member_id)
            await self.uow.commit()

    async def leave_company(self, company_id: UUID, current_user_id: UUID) -> None:
        async with self.uow:
            member = await self.uow.company_members.get_by_company_and_user(company_id, current_user_id)
            if member is None:
                raise CompanyMemberNotFoundException(current_user_id)

            await self.uow.company_members.delete(member.id)
            await self.uow.commit()

    async def get_members(self, company_id: UUID, skip: int, limit: int) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            return await self.uow.company_members.get_members_by_company(company_id, skip, limit)

    async def get_invitations_by_company(self, company_id: UUID, current_user_id: UUID, skip: int, limit: int) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()
            return await self.uow.company_members.get_invitations_by_company(company_id, skip, limit)

    async def get_requests_by_company(self, company_id: UUID, current_user_id: UUID, skip: int, limit: int) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()
            return await self.uow.company_members.get_request_by_company(company_id, skip, limit)

    async def get_invitations_by_user(self, current_user_id: UUID, skip: int, limit: int) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            return await self.uow.company_members.get_invitation_by_user_paginated(current_user_id, skip, limit)

    async def get_requests_by_user(self, current_user_id: UUID, skip: int, limit: int) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            return await self.uow.company_members.get_requests_by_user(current_user_id, skip, limit)


def get_company_member_service(uow=Depends(get_uow)) -> CompanyMemberService:
    return CompanyMemberService(uow)
