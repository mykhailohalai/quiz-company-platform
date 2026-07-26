from datetime import datetime, timezone
from uuid import uuid4

import pytest

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.notification_exceptions import NotificationNotFoundException
from app.models.company import Company, CompanyVisibility
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.models.notification import Notification, NotificationStatus


def make_company(**kwargs):
    defaults = dict(
        id=uuid4(),
        name="Acme",
        description="desc",
        owner_id=uuid4(),
        visibility=CompanyVisibility.VISIBLE_TO_ALL,
    )
    defaults.update(kwargs)
    return Company(**defaults)


def make_member(**kwargs):
    defaults = dict(
        id=uuid4(),
        company_id=uuid4(),
        user_id=uuid4(),
        role=Role.MEMBER,
        status=InviteStatus.ACTIVE,
    )
    defaults.update(kwargs)
    return CompanyMember(**defaults)


def make_notification(**kwargs):
    defaults = dict(
        id=uuid4(),
        user_id=uuid4(),
        message="New quiz was created",
        status=NotificationStatus.UNREAD,
        timestamp=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return Notification(**defaults)


# --- send_notification ---

async def test_send_notification_creates_notification_per_member(notification_service, uow):
    company = make_company()
    user1_id = uuid4()
    user2_id = uuid4()
    member1 = make_member(company_id=company.id, user_id=user1_id)
    member2 = make_member(company_id=company.id, user_id=user2_id)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member1.id] = member1
    uow.company_members.members[member2.id] = member2

    await notification_service.send_notification(company.id, "New quiz!")

    notifications = list(uow.notifications.notifications.values())
    assert len(notifications) == 2
    assert {n.user_id for n in notifications} == {user1_id, user2_id}
    assert all(n.message == "New quiz!" for n in notifications)
    assert all(n.status == NotificationStatus.UNREAD for n in notifications)


async def test_send_notification_no_members_creates_nothing(notification_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    await notification_service.send_notification(company.id, "New quiz!")

    assert len(uow.notifications.notifications) == 0


# --- send_notification_to_user ---

async def test_send_notification_to_user_creates_single_notification(notification_service, uow):
    user_id = uuid4()

    await notification_service.send_notification_to_user(user_id, "Time to retake quiz!")

    notifications = list(uow.notifications.notifications.values())
    assert len(notifications) == 1
    assert notifications[0].user_id == user_id
    assert notifications[0].message == "Time to retake quiz!"
    assert notifications[0].status == NotificationStatus.UNREAD


# --- get_notifications_by_user ---

async def test_get_notifications_by_user_returns_only_own(notification_service, uow):
    user_id = uuid4()
    n1 = make_notification(user_id=user_id)
    n2 = make_notification(user_id=user_id)
    other = make_notification()
    uow.notifications.notifications[n1.id] = n1
    uow.notifications.notifications[n2.id] = n2
    uow.notifications.notifications[other.id] = other

    notifications, total = await notification_service.get_notifications_by_user(user_id, skip=0, limit=10)

    assert total == 2
    assert all(n.user_id == user_id for n in notifications)


async def test_get_notifications_by_user_pagination(notification_service, uow):
    user_id = uuid4()
    for _ in range(5):
        n = make_notification(user_id=user_id)
        uow.notifications.notifications[n.id] = n

    notifications, total = await notification_service.get_notifications_by_user(user_id, skip=0, limit=3)

    assert total == 5
    assert len(notifications) == 3


async def test_get_notifications_by_user_returns_empty_when_none(notification_service, uow):
    notifications, total = await notification_service.get_notifications_by_user(uuid4(), skip=0, limit=10)

    assert notifications == []
    assert total == 0


# --- mark_as_read ---

async def test_mark_as_read_changes_status(notification_service, uow):
    user_id = uuid4()
    notification = make_notification(user_id=user_id, status=NotificationStatus.UNREAD)
    uow.notifications.notifications[notification.id] = notification

    result = await notification_service.mark_as_read(notification.id, user_id)

    assert result.status == NotificationStatus.READ


async def test_mark_as_read_raises_when_not_owner(notification_service, uow):
    notification = make_notification()
    uow.notifications.notifications[notification.id] = notification

    with pytest.raises(ForbiddenException):
        await notification_service.mark_as_read(notification.id, uuid4())


async def test_mark_as_read_raises_when_not_found(notification_service, uow):
    with pytest.raises(NotificationNotFoundException):
        await notification_service.mark_as_read(uuid4(), uuid4())
