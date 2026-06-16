from uuid import UUID

from sqlalchemy import and_, func, select

from app.repositories.base_repository import BaseRepository
from app.models.company_member import CompanyMember, InviteStatus
from app.schemas.company_members import CompanyMemberUpdateRequestSchema
from app.exceptions.company_member_exceptions import (
    CompanyMemberAlreadyExistsException,
    CompanyMemberNotFoundException,
)


class CompanyMemberRepository(
    BaseRepository[CompanyMember, CompanyMemberUpdateRequestSchema]
):
    model = CompanyMember
    not_found_exception = CompanyMemberNotFoundException
    already_exists_exception = CompanyMemberAlreadyExistsException

    async def get_by_company_and_user(self, company_id: UUID, user_id: UUID):
        requests = await self.session.execute(
            select(CompanyMember).where(
                and_(
                    company_id == CompanyMember.company_id
                    and user_id == CompanyMember.user_id
                )
            )
        )

        return requests.scalar_one_or_none()

    async def get_members_by_company(self, company_id: UUID, skip: int, limit: int):
        total = await self.session.scalar(
            select(func.count())
            .select_from(CompanyMember)
            .where(
                and_(
                    CompanyMember.status == InviteStatus.Active,
                    CompanyMember.company_id == company_id,
                )
            )
        )

        result = await self.session.execute(
            select(CompanyMember)
            .where(
                and_(
                    CompanyMember.status == InviteStatus.Active,
                    CompanyMember.company_id == company_id,
                )
            )
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all(), total

    # Owner invites user
    async def get_invitation_by_user(self, user_id: UUID):
        invatations = await self.session.execute(
            select(CompanyMember).where(
                and_(
                    CompanyMember.status == InviteStatus.Pending_invite,
                    CompanyMember.user_id == user_id,
                )
            )
        )

        return invatations.scalars().all()

    async def get_request_by_company(self, company_id: UUID):
        requests = await self.session.execute(
            select(CompanyMember).where(
                and_(
                    CompanyMember.status == InviteStatus.Pending_request,
                    CompanyMember.company_id == company_id,
                )
            )
        )

        return requests.scalars().all()

    # Invated by owner
    async def get_invitations_by_company(self, company_id: UUID):
        requests = await self.get_request_by_company(company_id)
        users = await self.session.execute(
            select(CompanyMember).where(
                and_(
                    CompanyMember.status == InviteStatus.Pending_invite,
                    CompanyMember.company_id == company_id,
                )
            )
        )

        return users.scalars().all()
