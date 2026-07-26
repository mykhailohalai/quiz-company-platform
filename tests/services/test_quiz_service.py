from uuid import uuid4

import pytest

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.quiz_exceptions import QuizNotFoundException
from app.models.company import Company, CompanyVisibility
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.models.quiz import Quiz, QuestionType
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
                question_type=QuestionType.SingleAnswer,
                answers=[
                    AnswerCreateRequestSchema(text="A", is_correct=True),
                    AnswerCreateRequestSchema(text="B", is_correct=False),
                ],
            ),
            QuestionCreateRequestSchema(
                title="Question 2",
                question_type=QuestionType.SingleAnswer,
                answers=[
                    AnswerCreateRequestSchema(text="C", is_correct=False),
                    AnswerCreateRequestSchema(text="D", is_correct=True),
                ],
            ),
        ],
    )
    defaults.update(kwargs)
    return QuizCreateRequestSchema(**defaults)


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
    admin = make_member(company_id=company.id, user_id=admin_id, role=Role.Admin, status=InviteStatus.Active)
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
                question_type=QuestionType.MultipleAnswer,
                answers=[
                    AnswerCreateRequestSchema(text="A", is_correct=True),
                    AnswerCreateRequestSchema(text="B", is_correct=True),
                    AnswerCreateRequestSchema(text="C", is_correct=False),
                ],
            ),
            QuestionCreateRequestSchema(
                title="Question 2",
                question_type=QuestionType.MultipleAnswer,
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
