from uuid import UUID

from app.exceptions.company_member_exceptions import (
    CompanyMemberAlreadyExistsException,
    CompanyMemberNotFoundException,
)
from app.models.company_member import InviteStatus


class FakeCompanyMemberRepository:
    def __init__(self, members=None):
        self.members = {m.id: m for m in (members or [])}

    async def get_by_id(self, member_id: UUID):
        member = self.members.get(member_id)
        if member is None:
            raise CompanyMemberNotFoundException(member_id)
        return member

    async def get_by_company_and_user(self, company_id: UUID, user_id: UUID):
        for m in self.members.values():
            if m.company_id == company_id and m.user_id == user_id:
                return m
        return None

    async def create(self, member):
        self.members[member.id] = member
        return member

    async def delete(self, member_id: UUID):
        if member_id not in self.members:
            raise CompanyMemberNotFoundException(member_id)
        del self.members[member_id]
        return True

    async def get_members_by_company(self, company_id: UUID, skip: int = 0, limit: int = 10):
        result = [
            m for m in self.members.values()
            if m.company_id == company_id and m.status == InviteStatus.Active
        ]
        return result[skip:skip + limit], len(result)

    async def get_invitations_by_company(self, company_id: UUID, skip: int = 0, limit: int = 10):
        result = [
            m for m in self.members.values()
            if m.company_id == company_id and m.status == InviteStatus.Pending_invite
        ]
        return result[skip:skip + limit], len(result)

    async def get_request_by_company(self, company_id: UUID, skip: int = 0, limit: int = 10):
        result = [
            m for m in self.members.values()
            if m.company_id == company_id and m.status == InviteStatus.Pending_request
        ]
        return result[skip:skip + limit], len(result)

    async def get_invitation_by_user_paginated(self, user_id: UUID, skip: int = 0, limit: int = 10):
        result = [
            m for m in self.members.values()
            if m.user_id == user_id and m.status == InviteStatus.Pending_invite
        ]
        return result[skip:skip + limit], len(result)

    async def get_requests_by_user(self, user_id: UUID, skip: int = 0, limit: int = 10):
        result = [
            m for m in self.members.values()
            if m.user_id == user_id and m.status == InviteStatus.Pending_request
        ]
        return result[skip:skip + limit], len(result)
