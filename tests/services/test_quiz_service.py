from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.quiz_exceptions import QuizNotFoundException
from app.models.company import Company, CompanyVisibility
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.models.quiz import Quiz, QuestionType
from app.models.quiz_result import QuizResult
from app.models.user import User
from app.schemas.quiz import (
    QuizCreateRequestSchema,
    QuizUpdateRequestSchema,
    QuestionCreateRequestSchema,
    AnswerCreateRequestSchema,
)


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


def make_quiz(**kwargs):
    defaults = dict(
        id=uuid4(),
        title="Test Quiz",
        description="Description",
        frequency=7,
        company_id=uuid4(),
    )
    defaults.update(kwargs)
    return Quiz(**defaults)


def make_quiz_data(**kwargs):
    defaults = dict(
        title="Test Quiz",
        description="Description",
        frequency=7,
        questions=[
            QuestionCreateRequestSchema(
                title="Question 1",
                question_type=QuestionType.SINGLE_ANSWER,
                answers=[
                    AnswerCreateRequestSchema(text="A", is_correct=True),
                    AnswerCreateRequestSchema(text="B", is_correct=False),
                ],
            ),
            QuestionCreateRequestSchema(
                title="Question 2",
                question_type=QuestionType.SINGLE_ANSWER,
                answers=[
                    AnswerCreateRequestSchema(text="C", is_correct=False),
                    AnswerCreateRequestSchema(text="D", is_correct=True),
                ],
            ),
        ],
    )
    defaults.update(kwargs)
    return QuizCreateRequestSchema(**defaults)


def make_user(**kwargs):
    defaults = dict(
        id=uuid4(),
        username="johndoe",
        email="john@example.com",
        password="hashed-password",
    )
    defaults.update(kwargs)
    return User(**defaults)


def make_quiz_result(**kwargs):
    defaults = dict(
        id=uuid4(),
        user_id=uuid4(),
        company_id=uuid4(),
        quiz_id=uuid4(),
        correct_answers=5,
        total_questions=10,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return QuizResult(**defaults)


# --- create_quiz ---

async def test_create_quiz_by_owner(quiz_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    uow.companies.companies[company.id] = company

    quiz = await quiz_service.create_quiz(company.id, owner_id, make_quiz_data())

    assert quiz.title == "Test Quiz"
    assert quiz.company_id == company.id
    assert uow.committed is True


async def test_create_quiz_by_admin(quiz_service, uow):
    company = make_company()
    admin_id = uuid4()
    admin = make_member(company_id=company.id, user_id=admin_id, role=Role.ADMIN, status=InviteStatus.ACTIVE)
    uow.companies.companies[company.id] = company
    uow.company_members.members[admin.id] = admin

    quiz = await quiz_service.create_quiz(company.id, admin_id, make_quiz_data())

    assert quiz.company_id == company.id
    assert uow.committed is True


async def test_create_quiz_raises_when_not_owner_or_admin(quiz_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    with pytest.raises(ForbiddenException):
        await quiz_service.create_quiz(company.id, uuid4(), make_quiz_data())


# --- update_quiz ---

async def test_update_quiz_updates_fields(quiz_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    quiz = make_quiz(company_id=company.id)
    uow.companies.companies[company.id] = company
    uow.quizzes.quizzes[quiz.id] = quiz

    data = QuizUpdateRequestSchema(title="Updated Title", frequency=14)
    result = await quiz_service.update_quiz(quiz.id, company.id, owner_id, data)

    assert result.title == "Updated Title"
    assert result.frequency == 14
    assert result.description == quiz.description
    assert uow.committed is True


async def test_update_quiz_raises_when_not_owner_or_admin(quiz_service, uow):
    company = make_company()
    quiz = make_quiz(company_id=company.id)
    uow.companies.companies[company.id] = company
    uow.quizzes.quizzes[quiz.id] = quiz

    with pytest.raises(ForbiddenException):
        await quiz_service.update_quiz(quiz.id, company.id, uuid4(), QuizUpdateRequestSchema(title="X"))


# --- delete_quiz ---

async def test_delete_quiz_removes_record(quiz_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    quiz = make_quiz(company_id=company.id)
    uow.companies.companies[company.id] = company
    uow.quizzes.quizzes[quiz.id] = quiz

    await quiz_service.delete_quiz(quiz.id, company.id, owner_id)

    assert quiz.id not in uow.quizzes.quizzes
    assert uow.committed is True


async def test_delete_quiz_raises_when_not_owner_or_admin(quiz_service, uow):
    company = make_company()
    quiz = make_quiz(company_id=company.id)
    uow.companies.companies[company.id] = company
    uow.quizzes.quizzes[quiz.id] = quiz

    with pytest.raises(ForbiddenException):
        await quiz_service.delete_quiz(quiz.id, company.id, uuid4())


# --- multiple correct answers ---

async def test_create_quiz_with_multiple_correct_answers(quiz_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    uow.companies.companies[company.id] = company

    data = QuizCreateRequestSchema(
        title="Multi Quiz",
        description="Description",
        frequency=7,
        questions=[
            QuestionCreateRequestSchema(
                title="Question 1",
                question_type=QuestionType.MULTIPLE_ANSWER,
                answers=[
                    AnswerCreateRequestSchema(text="A", is_correct=True),
                    AnswerCreateRequestSchema(text="B", is_correct=True),
                    AnswerCreateRequestSchema(text="C", is_correct=False),
                ],
            ),
            QuestionCreateRequestSchema(
                title="Question 2",
                question_type=QuestionType.MULTIPLE_ANSWER,
                answers=[
                    AnswerCreateRequestSchema(text="D", is_correct=True),
                    AnswerCreateRequestSchema(text="E", is_correct=True),
                ],
            ),
        ],
    )

    quiz = await quiz_service.create_quiz(company.id, owner_id, data)

    assert quiz.title == "Multi Quiz"
    assert uow.committed is True


# --- get_quizzes ---

async def test_get_quizzes_returns_company_quizzes(quiz_service, uow):
    company_id = uuid4()
    quiz1 = make_quiz(company_id=company_id)
    quiz2 = make_quiz(company_id=company_id)
    other_quiz = make_quiz()
    uow.quizzes.quizzes[quiz1.id] = quiz1
    uow.quizzes.quizzes[quiz2.id] = quiz2
    uow.quizzes.quizzes[other_quiz.id] = other_quiz

    quizzes, total = await quiz_service.get_quizzes(company_id, skip=0, limit=10)

    assert total == 2
    assert all(q.company_id == company_id for q in quizzes)


# --- get_average_by_system / get_average_by_company ---

async def test_get_average_by_system_returns_weighted_average_across_companies(quiz_service, uow):
    user_id = uuid4()
    r1 = make_quiz_result(user_id=user_id, correct_answers=3, total_questions=10)
    r2 = make_quiz_result(user_id=user_id, correct_answers=9, total_questions=10)
    other_user_result = make_quiz_result(correct_answers=1, total_questions=1)
    uow.quiz_results.results[r1.id] = r1
    uow.quiz_results.results[r2.id] = r2
    uow.quiz_results.results[other_user_result.id] = other_user_result

    average_score = await quiz_service.get_average_by_system(user_id)

    assert average_score == 60.0


async def test_get_average_by_system_returns_zero_when_no_results(quiz_service, uow):
    average_score = await quiz_service.get_average_by_system(uuid4())

    assert average_score == 0.0


async def test_get_average_by_company_returns_average_for_company_only(quiz_service, uow):
    user_id = uuid4()
    company_id = uuid4()
    in_company = make_quiz_result(
        user_id=user_id, company_id=company_id, correct_answers=4, total_questions=10
    )
    other_company = make_quiz_result(
        user_id=user_id, correct_answers=0, total_questions=10
    )
    uow.quiz_results.results[in_company.id] = in_company
    uow.quiz_results.results[other_company.id] = other_company

    average_score = await quiz_service.get_average_by_company(user_id, company_id)

    assert average_score == 40.0


async def test_get_average_by_company_returns_zero_when_no_results(quiz_service, uow):
    average_score = await quiz_service.get_average_by_company(uuid4(), uuid4())

    assert average_score == 0.0


# --- get_average_score_by_user ---

async def test_get_average_score_by_user_returns_per_quiz_average(quiz_service, uow):
    user_id = uuid4()
    quiz_id = uuid4()
    r1 = make_quiz_result(user_id=user_id, quiz_id=quiz_id, correct_answers=3, total_questions=10)
    r2 = make_quiz_result(user_id=user_id, quiz_id=quiz_id, correct_answers=9, total_questions=10)
    other_user_result = make_quiz_result(correct_answers=1, total_questions=1)
    uow.quiz_results.results[r1.id] = r1
    uow.quiz_results.results[r2.id] = r2
    uow.quiz_results.results[other_user_result.id] = other_user_result

    result = await quiz_service.get_average_score_by_user(user_id)

    assert len(result) == 1
    assert result[0].quiz_id == quiz_id
    assert result[0].user_id == user_id
    assert result[0].average_score == 60.0


async def test_get_average_score_by_user_filters_by_date_range(quiz_service, uow):
    user_id = uuid4()
    quiz_id = uuid4()
    old = make_quiz_result(
        user_id=user_id,
        quiz_id=quiz_id,
        correct_answers=0,
        total_questions=10,
        created_at=datetime.now(timezone.utc) - timedelta(days=30),
    )
    recent = make_quiz_result(
        user_id=user_id, quiz_id=quiz_id, correct_answers=5, total_questions=10
    )
    uow.quiz_results.results[old.id] = old
    uow.quiz_results.results[recent.id] = recent

    result = await quiz_service.get_average_score_by_user(
        user_id, date_from=(datetime.now(timezone.utc) - timedelta(days=1)).date()
    )

    assert len(result) == 1
    assert result[0].average_score == 50.0


# --- get_quizzes_last_attempt_by_user ---

async def test_get_quizzes_last_attempt_by_user_returns_latest_per_quiz(quiz_service, uow):
    user_id = uuid4()
    quiz_id = uuid4()
    earlier = make_quiz_result(
        user_id=user_id,
        quiz_id=quiz_id,
        created_at=datetime.now(timezone.utc) - timedelta(days=5),
    )
    latest = make_quiz_result(user_id=user_id, quiz_id=quiz_id)
    uow.quiz_results.results[earlier.id] = earlier
    uow.quiz_results.results[latest.id] = latest

    result = await quiz_service.get_quizzes_last_attempt_by_user(user_id)

    assert len(result) == 1
    assert result[0].quiz_id == quiz_id
    assert result[0].last_attempt_at == latest.created_at


# --- get_weekly_results_by_company ---

async def test_get_weekly_results_by_company_by_owner(quiz_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    member_user_id = uuid4()
    r1 = make_quiz_result(
        company_id=company.id, user_id=member_user_id, correct_answers=4, total_questions=10
    )
    r2 = make_quiz_result(
        company_id=company.id, user_id=member_user_id, correct_answers=8, total_questions=10
    )
    uow.companies.companies[company.id] = company
    uow.quiz_results.results[r1.id] = r1
    uow.quiz_results.results[r2.id] = r2

    result = await quiz_service.get_weekly_results_by_company(company.id, owner_id)

    assert len(result) == 1
    assert result[0].user_id == member_user_id
    assert result[0].average_score == 60.0


async def test_get_weekly_results_by_company_raises_when_not_owner_or_admin(quiz_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    with pytest.raises(ForbiddenException):
        await quiz_service.get_weekly_results_by_company(company.id, uuid4())


# --- get_weekly_results_by_user_and_company ---

async def test_get_weekly_results_by_user_and_company_by_admin(quiz_service, uow):
    company = make_company()
    admin_id = uuid4()
    admin = make_member(
        company_id=company.id, user_id=admin_id, role=Role.ADMIN, status=InviteStatus.ACTIVE
    )
    target_user_id = uuid4()
    quiz_id = uuid4()
    r1 = make_quiz_result(
        company_id=company.id,
        user_id=target_user_id,
        quiz_id=quiz_id,
        correct_answers=2,
        total_questions=10,
    )
    uow.companies.companies[company.id] = company
    uow.company_members.members[admin.id] = admin
    uow.quiz_results.results[r1.id] = r1

    result = await quiz_service.get_weekly_results_by_user_and_company(
        company.id, target_user_id, admin_id
    )

    assert len(result) == 1
    assert result[0].quiz_id == quiz_id
    assert result[0].user_id == target_user_id
    assert result[0].average_score == 20.0


async def test_get_weekly_results_by_user_and_company_raises_when_not_owner_or_admin(quiz_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    with pytest.raises(ForbiddenException):
        await quiz_service.get_weekly_results_by_user_and_company(
            company.id, uuid4(), uuid4()
        )


# --- get_last_attempts_by_company ---

async def test_get_last_attempts_by_company_includes_members_without_attempts(quiz_service, uow):
    owner_id = uuid4()
    company = make_company(owner_id=owner_id)
    active_user_with_attempt = uuid4()
    active_user_without_attempt = uuid4()
    member1 = make_member(
        company_id=company.id, user_id=active_user_with_attempt, status=InviteStatus.ACTIVE
    )
    member2 = make_member(
        company_id=company.id, user_id=active_user_without_attempt, status=InviteStatus.ACTIVE
    )
    result_record = make_quiz_result(company_id=company.id, user_id=active_user_with_attempt)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member1.id] = member1
    uow.company_members.members[member2.id] = member2
    uow.quiz_results.results[result_record.id] = result_record

    result = await quiz_service.get_last_attempts_by_company(company.id, owner_id)

    by_user = {item.user_id: item.last_attempt_at for item in result}
    assert by_user[active_user_with_attempt] == result_record.created_at
    assert by_user[active_user_without_attempt] is None


async def test_get_last_attempts_by_company_raises_when_not_owner_or_admin(quiz_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    with pytest.raises(ForbiddenException):
        await quiz_service.get_last_attempts_by_company(company.id, uuid4())


# --- notify_all_overdue_quizzes ---

async def test_notify_all_overdue_quizzes_notifies_when_never_completed(quiz_service, uow):
    user = make_user()
    company = make_company()
    member = make_member(company_id=company.id, user_id=user.id)
    quiz = make_quiz(company_id=company.id, frequency=1)
    uow.users.users[user.id] = user
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member
    uow.quizzes.quizzes[quiz.id] = quiz

    await quiz_service.notify_all_overdue_quizzes()

    notifications = list(uow.notifications.notifications.values())
    assert len(notifications) == 1
    assert notifications[0].user_id == user.id
    assert quiz.title in notifications[0].message


async def test_notify_all_overdue_quizzes_skips_when_completed_recently(quiz_service, uow):
    user = make_user()
    company = make_company()
    member = make_member(company_id=company.id, user_id=user.id)
    quiz = make_quiz(company_id=company.id, frequency=7)
    result = make_quiz_result(user_id=user.id, quiz_id=quiz.id, company_id=company.id)
    uow.users.users[user.id] = user
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member
    uow.quizzes.quizzes[quiz.id] = quiz
    uow.quiz_results.results[result.id] = result

    await quiz_service.notify_all_overdue_quizzes()

    assert len(uow.notifications.notifications) == 0


async def test_notify_all_overdue_quizzes_notifies_when_overdue(quiz_service, uow):
    user = make_user()
    company = make_company()
    member = make_member(company_id=company.id, user_id=user.id)
    quiz = make_quiz(company_id=company.id, frequency=1)
    result = make_quiz_result(
        user_id=user.id,
        quiz_id=quiz.id,
        company_id=company.id,
        created_at=datetime.now(timezone.utc) - timedelta(days=5),
    )
    uow.users.users[user.id] = user
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member
    uow.quizzes.quizzes[quiz.id] = quiz
    uow.quiz_results.results[result.id] = result

    await quiz_service.notify_all_overdue_quizzes()

    notifications = list(uow.notifications.notifications.values())
    assert len(notifications) == 1
    assert notifications[0].user_id == user.id


async def test_notify_all_overdue_quizzes_ignores_quizzes_from_other_companies(quiz_service, uow):
    user = make_user()
    other_company = make_company()
    quiz = make_quiz(company_id=other_company.id, frequency=1)
    uow.users.users[user.id] = user
    uow.companies.companies[other_company.id] = other_company
    uow.quizzes.quizzes[quiz.id] = quiz

    await quiz_service.notify_all_overdue_quizzes()

    assert len(uow.notifications.notifications) == 0


async def test_notify_all_overdue_quizzes_notifies_every_user(quiz_service, uow):
    company = make_company()
    user1 = make_user(username="user1", email="user1@example.com")
    user2 = make_user(username="user2", email="user2@example.com")
    member1 = make_member(company_id=company.id, user_id=user1.id)
    member2 = make_member(company_id=company.id, user_id=user2.id)
    quiz = make_quiz(company_id=company.id, frequency=1)
    uow.companies.companies[company.id] = company
    uow.users.users[user1.id] = user1
    uow.users.users[user2.id] = user2
    uow.company_members.members[member1.id] = member1
    uow.company_members.members[member2.id] = member2
    uow.quizzes.quizzes[quiz.id] = quiz

    await quiz_service.notify_all_overdue_quizzes()

    notifications = list(uow.notifications.notifications.values())
    assert len(notifications) == 2
    assert {n.user_id for n in notifications} == {user1.id, user2.id}


async def test_notify_all_overdue_quizzes_does_nothing_when_no_users(quiz_service, uow):
    await quiz_service.notify_all_overdue_quizzes()

    assert len(uow.notifications.notifications) == 0
