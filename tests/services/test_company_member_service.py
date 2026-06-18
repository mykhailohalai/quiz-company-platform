from uuid import uuid4

import pytest

from app.exceptions.company_member_exceptions import CompanyMemberNotFoundException, CompanyMemberNotAdminException
from app.exceptions.general_exceptions import ForbiddenException
from app.models.company import Company, CompanyVisibility
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.schemas.company_member import CompanyMemberInvitationCreate, CompanyMemberRequestCreate


def make_company(**kwargs):
    defaults = dict(
        id=uuid4(),
        name="Acme",
        description="desc",
        owner_id=uuid4(),
        visibility=CompanyVisibility.Visible_to_all,
    )
    defaults.update(kwargs)
    return Company(**defaults)


def make_member(**kwargs):
    defaults = dict(
        id=uuid4(),
        company_id=uuid4(),
        user_id=uuid4(),
        role=Role.Member,
        status=InviteStatus.Active,
    )
    defaults.update(kwargs)
    return CompanyMember(**defaults)


# --- send_invitation ---

async def test_send_invitation_creates_pending_invite(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    uow.companies.companies[company.id] = company
    data = CompanyMemberInvitationCreate(user_id=uuid4())

    invitation = await company_member_service.send_invitation(owner_id, company.id, data)

    assert invitation.status == InviteStatus.Pending_invite
    assert invitation.role == Role.Member
    assert invitation.user_id == data.user_id
    assert uow.committed is True


async def test_send_invitation_raises_when_not_owner(company_member_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company
    data = CompanyMemberInvitationCreate(user_id=uuid4())

    with pytest.raises(ForbiddenException):
        await company_member_service.send_invitation(uuid4(), company.id, data)


# --- cancel_invitation ---

async def test_cancel_invitation_removes_record(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    invitation = make_member(company_id=company.id, status=InviteStatus.Pending_invite)
    uow.companies.companies[company.id] = company
    uow.company_members.members[invitation.id] = invitation

    await company_member_service.cancel_invitation(owner_id, company.id, invitation.id)

    assert invitation.id not in uow.company_members.members
    assert uow.committed is True


async def test_cancel_invitation_raises_when_not_owner(company_member_service, uow):
    company = make_company()
    invitation = make_member(company_id=company.id, status=InviteStatus.Pending_invite)
    uow.companies.companies[company.id] = company
    uow.company_members.members[invitation.id] = invitation

    with pytest.raises(ForbiddenException):
        await company_member_service.cancel_invitation(uuid4(), company.id, invitation.id)


# --- accept_invitation ---

async def test_accept_invitation_sets_active(company_member_service, uow):
    user_id = uuid4()
    invitation = make_member(user_id=user_id, status=InviteStatus.Pending_invite)
    uow.company_members.members[invitation.id] = invitation

    result = await company_member_service.accept_invitation(user_id, invitation.id)

    assert result.status == InviteStatus.Active
    assert uow.committed is True


async def test_accept_invitation_raises_when_not_addressee(company_member_service, uow):
    invitation = make_member(status=InviteStatus.Pending_invite)
    uow.company_members.members[invitation.id] = invitation

    with pytest.raises(ForbiddenException):
        await company_member_service.accept_invitation(uuid4(), invitation.id)


# --- decline_invitation ---

async def test_decline_invitation_sets_rejected(company_member_service, uow):
    user_id = uuid4()
    invitation = make_member(user_id=user_id, status=InviteStatus.Pending_invite)
    uow.company_members.members[invitation.id] = invitation

    result = await company_member_service.decline_invitation(user_id, invitation.id)

    assert result.status == InviteStatus.Rejected
    assert uow.committed is True


async def test_decline_invitation_raises_when_not_addressee(company_member_service, uow):
    invitation = make_member(status=InviteStatus.Pending_invite)
    uow.company_members.members[invitation.id] = invitation

    with pytest.raises(ForbiddenException):
        await company_member_service.decline_invitation(uuid4(), invitation.id)


# --- send_join_request ---

async def test_send_join_request_creates_pending_request(company_member_service, uow):
    user_id = uuid4()
    company_id = uuid4()
    data = CompanyMemberRequestCreate(company_id=company_id)

    request = await company_member_service.send_join_request(user_id, data)

    assert request.status == InviteStatus.Pending_request
    assert request.user_id == user_id
    assert request.company_id == company_id
    assert uow.committed is True


# --- cancel_join_request ---

async def test_cancel_join_request_removes_record(company_member_service, uow):
    user_id = uuid4()
    request = make_member(user_id=user_id, status=InviteStatus.Pending_request)
    uow.company_members.members[request.id] = request

    await company_member_service.cancel_join_request(user_id, request.id)

    assert request.id not in uow.company_members.members
    assert uow.committed is True


async def test_cancel_join_request_raises_when_not_owner(company_member_service, uow):
    request = make_member(status=InviteStatus.Pending_request)
    uow.company_members.members[request.id] = request

    with pytest.raises(ForbiddenException):
        await company_member_service.cancel_join_request(uuid4(), request.id)


# --- accept_join_request ---

async def test_accept_join_request_sets_active(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    request = make_member(company_id=company.id, status=InviteStatus.Pending_request)
    uow.companies.companies[company.id] = company
    uow.company_members.members[request.id] = request

    result = await company_member_service.accept_join_request(request.id, owner_id)

    assert result.status == InviteStatus.Active
    assert uow.committed is True


async def test_accept_join_request_raises_when_not_owner(company_member_service, uow):
    company = make_company()
    request = make_member(company_id=company.id, status=InviteStatus.Pending_request)
    uow.companies.companies[company.id] = company
    uow.company_members.members[request.id] = request

    with pytest.raises(ForbiddenException):
        await company_member_service.accept_join_request(request.id, uuid4())


# --- decline_join_request ---

async def test_decline_join_request_sets_rejected(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    request = make_member(company_id=company.id, status=InviteStatus.Pending_request)
    uow.companies.companies[company.id] = company
    uow.company_members.members[request.id] = request

    result = await company_member_service.decline_join_request(request.id, owner_id)

    assert result.status == InviteStatus.Rejected
    assert uow.committed is True


async def test_decline_join_request_raises_when_not_owner(company_member_service, uow):
    company = make_company()
    request = make_member(company_id=company.id, status=InviteStatus.Pending_request)
    uow.companies.companies[company.id] = company
    uow.company_members.members[request.id] = request

    with pytest.raises(ForbiddenException):
        await company_member_service.decline_join_request(request.id, uuid4())


# --- remove_member ---

async def test_remove_member_deletes_record(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    member = make_member(company_id=company.id, status=InviteStatus.Active)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member

    await company_member_service.remove_member(member.id, company.id, owner_id)

    assert member.id not in uow.company_members.members
    assert uow.committed is True


async def test_remove_member_raises_when_not_owner(company_member_service, uow):
    company = make_company()
    member = make_member(company_id=company.id)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member

    with pytest.raises(ForbiddenException):
        await company_member_service.remove_member(member.id, company.id, uuid4())


# --- leave_company ---

async def test_leave_company_deletes_member_record(company_member_service, uow):
    user_id = uuid4()
    company_id = uuid4()
    member = make_member(company_id=company_id, user_id=user_id, status=InviteStatus.Active)
    uow.company_members.members[member.id] = member

    await company_member_service.leave_company(company_id, user_id)

    assert member.id not in uow.company_members.members
    assert uow.committed is True


async def test_leave_company_raises_when_not_member(company_member_service, uow):
    with pytest.raises(CompanyMemberNotFoundException):
        await company_member_service.leave_company(uuid4(), uuid4())


# --- get_members ---

async def test_get_members_returns_only_active(company_member_service, uow):
    company_id = uuid4()
    active = make_member(company_id=company_id, status=InviteStatus.Active)
    pending = make_member(company_id=company_id, status=InviteStatus.Pending_invite)
    uow.company_members.members[active.id] = active
    uow.company_members.members[pending.id] = pending

    members, total = await company_member_service.get_members(company_id, skip=0, limit=10)

    assert members == [active]
    assert total == 1


# --- appoint_admin ---

async def test_appoint_admin_sets_role(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    member = make_member(company_id=company.id, status=InviteStatus.Active, role=Role.Member)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member

    result = await company_member_service.appoint_admin(company.id, member.user_id, owner_id)

    assert result.role == Role.Admin
    assert uow.committed is True


async def test_appoint_admin_raises_when_not_owner(company_member_service, uow):
    company = make_company()
    member = make_member(company_id=company.id, status=InviteStatus.Active)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member

    with pytest.raises(ForbiddenException):
        await company_member_service.appoint_admin(company.id, member.user_id, uuid4())


async def test_appoint_admin_raises_when_not_active_member(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    member = make_member(company_id=company.id, status=InviteStatus.Pending_invite)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member

    with pytest.raises(CompanyMemberNotFoundException):
        await company_member_service.appoint_admin(company.id, member.user_id, owner_id)


# --- remove_admin ---

async def test_remove_admin_sets_member_role(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    admin = make_member(company_id=company.id, status=InviteStatus.Active, role=Role.Admin)
    uow.companies.companies[company.id] = company
    uow.company_members.members[admin.id] = admin

    result = await company_member_service.remove_admin(company.id, admin.user_id, owner_id)

    assert result.role == Role.Member
    assert uow.committed is True


async def test_remove_admin_raises_when_not_owner(company_member_service, uow):
    company = make_company()
    admin = make_member(company_id=company.id, status=InviteStatus.Active, role=Role.Admin)
    uow.companies.companies[company.id] = company
    uow.company_members.members[admin.id] = admin

    with pytest.raises(ForbiddenException):
        await company_member_service.remove_admin(company.id, admin.user_id, uuid4())


async def test_remove_admin_raises_when_not_admin(company_member_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    member = make_member(company_id=company.id, status=InviteStatus.Active, role=Role.Member)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member

    with pytest.raises(CompanyMemberNotAdminException):
        await company_member_service.remove_admin(company.id, member.user_id, owner_id)


# --- get_admins_by_company ---

async def test_get_admins_returns_only_admins(company_member_service, uow):
    user_id = uuid4()
    company = make_company()
    admin = make_member(company_id=company.id, status=InviteStatus.Active, role=Role.Admin)
    member = make_member(company_id=company.id, status=InviteStatus.Active, role=Role.Member)
    current_user = make_member(company_id=company.id, user_id=user_id, status=InviteStatus.Active)
    uow.companies.companies[company.id] = company
    uow.company_members.members[admin.id] = admin
    uow.company_members.members[member.id] = member
    uow.company_members.members[current_user.id] = current_user

    admins, total = await company_member_service.get_admins_by_company(company.id, user_id, skip=0, limit=10)

    assert admins == [admin]
    assert total == 1


async def test_get_admins_raises_when_not_member(company_member_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    with pytest.raises(ForbiddenException):
        await company_member_service.get_admins_by_company(company.id, uuid4(), skip=0, limit=10)
