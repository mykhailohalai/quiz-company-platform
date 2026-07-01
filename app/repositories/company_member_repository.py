from uuid import UUID

from sqlalchemy import and_, func, select

from app.repositories.base_repository import BaseRepository
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.schemas.company_member import CompanyMemberUpdateRequestSchema
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
                    company_id == CompanyMember.company_id,
                    user_id == CompanyMember.user_id,
                )
            )
        )

        return requests.scalar_one_or_none()

    async def get_active_member_by_company_and_user(
        self, company_id: UUID, user_id: UUID
    ):
        result = await self.session.execute(
            select(CompanyMember).where(
                and_(
                    CompanyMember.company_id == company_id,
                    CompanyMember.user_id == user_id,
                    CompanyMember.status == InviteStatus.ACTIVE,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_members_by_company(self, company_id: UUID, skip: int, limit: int):
        total = await self.session.scalar(
            select(func.count())
            .select_from(CompanyMember)
            .where(
                and_(
                    CompanyMember.status == InviteStatus.ACTIVE,
                    CompanyMember.company_id == company_id,
                )
            )
        )

        result = await self.session.execute(
            select(CompanyMember)
            .where(
                and_(
                    CompanyMember.status == InviteStatus.ACTIVE,
                    CompanyMember.company_id == company_id,
                )
            )
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all(), total

    async def get_all_members_by_company(self, company_id: UUID) -> CompanyMember:
        result = await self.session.execute(
            select(CompanyMember)
            .where(
                and_(
                    CompanyMember.status == InviteStatus.ACTIVE,
                    CompanyMember.company_id == company_id,
                )
            )
        )

        return result.scalars().all()

    async def get_admins_by_company(self, company_id: UUID, skip: int, limit: int):
        total = await self.session.scalar(
            select(func.count())
            .select_from(CompanyMember)
            .where(
                and_(
                    CompanyMember.status == InviteStatus.ACTIVE,
                    CompanyMember.company_id == company_id,
                    CompanyMember.role == Role.ADMIN,
                )
            )
        )

        result = await self.session.execute(
            select(CompanyMember)
            .where(
                and_(
                    CompanyMember.status == InviteStatus.ACTIVE,
                    CompanyMember.company_id == company_id,
                    CompanyMember.role == Role.ADMIN,
                )
            )
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all(), total

    async def get_admin_by_id(self, admin_id: UUID, company_id: UUID):
        admin = await self.session.execute(
            select(CompanyMember).where(
                and_(
                    CompanyMember.role == Role.ADMIN,
                    CompanyMember.user_id == admin_id,
                    CompanyMember.status == InviteStatus.ACTIVE,
                    CompanyMember.company_id == company_id,
                )
            )
        )

        return admin.scalar_one_or_none()

    # Owner invites user
    async def get_invitation_by_user(self, user_id: UUID):
        invatations = await self.session.execute(
            select(CompanyMember).where(
                and_(
                    CompanyMember.status == InviteStatus.PENDING_INVITE,
                    CompanyMember.user_id == user_id,
                )
            )
        )

        return invatations.scalars().all()

    async def get_request_by_company(
        self, company_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        condition = and_(
            CompanyMember.status == InviteStatus.PENDING_REQUEST,
            CompanyMember.company_id == company_id,
        )
        total = await self.session.scalar(
            select(func.count()).select_from(CompanyMember).where(condition)
        )
        result = await self.session.execute(
            select(CompanyMember).where(condition).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def get_invitations_by_company(
        self, company_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        condition = and_(
            CompanyMember.status == InviteStatus.PENDING_INVITE,
            CompanyMember.company_id == company_id,
        )
        total = await self.session.scalar(
            select(func.count()).select_from(CompanyMember).where(condition)
        )
        result = await self.session.execute(
            select(CompanyMember).where(condition).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def get_invitation_by_user_paginated(
        self, user_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        condition = and_(
            CompanyMember.status == InviteStatus.PENDING_INVITE,
            CompanyMember.user_id == user_id,
        )
        total = await self.session.scalar(
            select(func.count()).select_from(CompanyMember).where(condition)
        )
        result = await self.session.execute(
            select(CompanyMember).where(condition).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def get_requests_by_user(
        self, user_id: UUID, skip: int, limit: int
    ) -> tuple[list[CompanyMember], int]:
        condition = and_(
            CompanyMember.status == InviteStatus.PENDING_REQUEST,
            CompanyMember.user_id == user_id,
        )
        total = await self.session.scalar(
            select(func.count()).select_from(CompanyMember).where(condition)
        )
        result = await self.session.execute(
            select(CompanyMember).where(condition).offset(skip).limit(limit)
        )
        return result.scalars().all(), total
