import logging
from uuid import UUID

from fastapi import Depends

logger = logging.getLogger(__name__)

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.company_member_exceptions import (
    CompanyMemberNotFoundException,
    CompanyMemberNotAdminException,
    CompanyMemberAdminException,
)
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.utils.unit_of_work import UnitOfWork, get_uow
from app.schemas.company_member import (
    CompanyMemberInvitationCreate,
    CompanyMemberRequestCreate,
)


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
                role=Role.MEMBER,
                status=InviteStatus.PENDING_INVITE,
            )
            await self.uow.company_members.create(invitation)
            await self.uow.commit()
            logger.info("Invitation sent: company_id=%s user_id=%s", company_id, data.user_id)

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
            logger.info("Invitation cancelled: id=%s", invitation_id)

    async def accept_invitation(
        self, current_user_id: UUID, invitation_id: UUID
    ) -> CompanyMember:
        async with self.uow:
            invitation = await self.uow.company_members.get_by_id(invitation_id)
            if current_user_id != invitation.user_id:
                raise ForbiddenException()

            invitation.status = InviteStatus.ACTIVE
            await self.uow.commit()
            logger.info("Invitation accepted: id=%s user_id=%s", invitation_id, current_user_id)
        return invitation

    async def decline_invitation(
        self, current_user_id: UUID, invitation_id: UUID
    ) -> CompanyMember:
        async with self.uow:
            invitation = await self.uow.company_members.get_by_id(invitation_id)
            if current_user_id != invitation.user_id:
                raise ForbiddenException()

            invitation.status = InviteStatus.REJECTED
            await self.uow.commit()
            logger.info("Invitation declined: id=%s user_id=%s", invitation_id, current_user_id)
        return invitation

    async def send_join_request(
        self, user_id: UUID, data: CompanyMemberRequestCreate
    ) -> CompanyMember:
        async with self.uow:
            request = CompanyMember(
                company_id=data.company_id,
                user_id=user_id,
                role=Role.MEMBER,
                status=InviteStatus.PENDING_REQUEST,
            )
            await self.uow.company_members.create(request)
            await self.uow.commit()
            logger.info("Join request sent: company_id=%s user_id=%s", data.company_id, user_id)
        return request

    async def cancel_join_request(self, user_id: UUID, join_request_id: UUID) -> None:
        async with self.uow:
            join_request = await self.uow.company_members.get_by_id(join_request_id)
            if user_id != join_request.user_id:
                raise ForbiddenException()

            await self.uow.company_members.delete(join_request_id)
            await self.uow.commit()
            logger.info("Join request cancelled: id=%s user_id=%s", join_request_id, user_id)

    async def accept_join_request(
        self, join_request_id: UUID, current_user_id: UUID
    ) -> CompanyMember:
        async with self.uow:
            request = await self.uow.company_members.get_by_id(join_request_id)
            company = await self.uow.companies.get_by_id(request.company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            request.status = InviteStatus.ACTIVE
            await self.uow.commit()
            logger.info("Join request accepted: id=%s", join_request_id)
        return request

    async def decline_join_request(
        self, join_request_id: UUID, current_user_id: UUID
    ) -> CompanyMember:
        async with self.uow:
            request = await self.uow.company_members.get_by_id(join_request_id)
            company = await self.uow.companies.get_by_id(request.company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            request.status = InviteStatus.REJECTED
            await self.uow.commit()
            logger.info("Join request declined: id=%s", join_request_id)
        return request

    async def remove_member(
        self, member_id: UUID, company_id: UUID, current_user_id: UUID
    ) -> None:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            await self.uow.company_members.delete(member_id)
            await self.uow.commit()
            logger.info("Member removed: id=%s company_id=%s", member_id, company_id)

    async def leave_company(self, company_id: UUID, current_user_id: UUID) -> None:
        async with self.uow:
            member = await self.uow.company_members.get_by_company_and_user(
                company_id, current_user_id
            )
            if member is None:
                raise CompanyMemberNotFoundException(current_user_id)

            await self.uow.company_members.delete(member.id)
            await self.uow.commit()
            logger.info("User left company: user_id=%s company_id=%s", current_user_id, company_id)

    async def get_members(
        self, company_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            return await self.uow.company_members.get_members_by_company(
                company_id, skip, limit
            )

    async def get_all_members(
        self, company_id: UUID
    ):
        async with self.uow:
            return await self.uow.company_members.get_all_members_by_company(company_id)

    async def get_invitations_by_company(
        self, company_id: UUID, current_user_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()
            return await self.uow.company_members.get_invitations_by_company(
                company_id, skip, limit
            )

    async def get_requests_by_company(
        self, company_id: UUID, current_user_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()
            return await self.uow.company_members.get_request_by_company(
                company_id, skip, limit
            )

    async def get_invitations_by_user(
        self, current_user_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            return await self.uow.company_members.get_invitation_by_user_paginated(
                current_user_id, skip, limit
            )

    async def get_requests_by_user(
        self, current_user_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            return await self.uow.company_members.get_requests_by_user(
                current_user_id, skip, limit
            )

    async def appoint_admin(
        self, company_id: UUID, user_id: UUID, current_user_id: UUID
    ) -> CompanyMember:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            member = await self.uow.company_members.get_by_company_and_user(
                company.id, user_id
            )
            if member is None or member.status != InviteStatus.ACTIVE:
                raise CompanyMemberNotFoundException(user_id)

            if member.role == Role.ADMIN:
                raise CompanyMemberAdminException(user_id)

            member.role = Role.ADMIN
            await self.uow.commit()
            logger.info("Admin appointed: user_id=%s company_id=%s", user_id, company_id)

            return member

    async def is_admin(self, user_id: UUID, company_id: UUID) -> bool:
        async with self.uow:
            admin = await self.uow.company_members.get_admin_by_id(user_id, company_id)
            if admin is None:
                return False
            return True

    async def remove_admin(
        self, company_id: UUID, user_id: UUID, current_user_id: UUID
    ) -> CompanyMember:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            admin = await self.uow.company_members.get_admin_by_id(user_id, company.id)
            if admin is None:
                raise CompanyMemberNotAdminException(user_id)

            admin.role = Role.MEMBER
            await self.uow.commit()
            logger.info("Admin removed: user_id=%s company_id=%s", user_id, company_id)

            return admin

    async def get_admins_by_company(
        self, company_id: UUID, current_user_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)

            member = await self.uow.company_members.get_by_company_and_user(
                company_id, current_user_id
            )
            if member is None or member.status != InviteStatus.ACTIVE:
                raise ForbiddenException()

            return await self.uow.company_members.get_admins_by_company(
                company.id, skip, limit
            )
