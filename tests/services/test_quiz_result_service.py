from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.quiz_exceptions import QuizFrequencyException
from app.models.company import Company, CompanyVisibility
from app.models.company_member import CompanyMember, InviteStatus, Role
from app.models.quiz import Quiz, Question, Answer, QuestionType
from app.models.quiz_result import QuizResult
from app.schemas.quiz_result import QuizSubmitSchema, QuestionAnswerSchema


def make_company(**kwargs):
    defaults = dict(
        id=uuid4(), name="Acme", description="desc",
        owner_id=uuid4(), visibility=CompanyVisibility.VISIBLE_TO_ALL,
    )
    defaults.update(kwargs)
    return Company(**defaults)


def make_member(**kwargs):
    defaults = dict(
        id=uuid4(), company_id=uuid4(), user_id=uuid4(),
        role=Role.MEMBER, status=InviteStatus.ACTIVE,
    )
    defaults.update(kwargs)
    return CompanyMember(**defaults)


def make_quiz(**kwargs):
    defaults = dict(
        id=uuid4(), title="Quiz", description="Desc",
        frequency=7, company_id=uuid4(),
    )
    defaults.update(kwargs)
    return Quiz(**defaults)


def make_question(quiz_id, **kwargs):
    defaults = dict(
        id=uuid4(), title="Q?",
        question_type=QuestionType.SINGLE_ANSWER, quiz_id=quiz_id,
    )
    defaults.update(kwargs)
    return Question(**defaults)


def make_answer(question_id, is_correct=False, **kwargs):
    defaults = dict(id=uuid4(), text="Ans", is_correct=is_correct, question_id=question_id)
    defaults.update(kwargs)
    return Answer(**defaults)


def make_quiz_result(**kwargs):
    defaults = dict(
        id=uuid4(), user_id=uuid4(), quiz_id=uuid4(),
        company_id=uuid4(), correct_answers=3, total_questions=5,
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return QuizResult(**defaults)


# --- get_quiz_by_company_member ---

async def test_get_quiz_by_company_member_returns_quiz(quiz_service, uow):
    user_id = uuid4()
    company = make_company()
    quiz = make_quiz(company_id=company.id)
    member = make_member(company_id=company.id, user_id=user_id)
    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member
    uow.quizzes.quizzes[quiz.id] = quiz

    result = await quiz_service.get_quiz_by_company_member(company.id, user_id, quiz.id)

    assert result.id == quiz.id


async def test_get_quiz_by_company_member_raises_when_not_member(quiz_service, uow):
    company = make_company()
    quiz = make_quiz(company_id=company.id)
    uow.companies.companies[company.id] = company
    uow.quizzes.quizzes[quiz.id] = quiz

    with pytest.raises(ForbiddenException):
        await quiz_service.get_quiz_by_company_member(company.id, uuid4(), quiz.id)


# --- submit_quiz ---

async def test_submit_quiz_saves_result(quiz_service, uow):
    user_id = uuid4()
    company = make_company()
    quiz = make_quiz(company_id=company.id, frequency=7)
    member = make_member(company_id=company.id, user_id=user_id)

    q1 = make_question(quiz.id)
    a1_correct = make_answer(q1.id, is_correct=True)
    a1_wrong = make_answer(q1.id, is_correct=False)
    q1.answers = [a1_correct, a1_wrong]

    q2 = make_question(quiz.id)
    a2_correct = make_answer(q2.id, is_correct=True)
    a2_wrong = make_answer(q2.id, is_correct=False)
    q2.answers = [a2_correct, a2_wrong]

    quiz.questions = [q1, q2]

    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member
    uow.quizzes.quizzes[quiz.id] = quiz

    data = QuizSubmitSchema(answers=[
        QuestionAnswerSchema(question_id=q1.id, answer_ids=[a1_correct.id]),
        QuestionAnswerSchema(question_id=q2.id, answer_ids=[a2_correct.id]),
    ])

    result = await quiz_service.submit_quiz(company.id, quiz.id, user_id, data)

    assert result.correct_answers == 2
    assert result.total_questions == 2
    assert uow.committed is True


async def test_submit_quiz_raises_when_not_member(quiz_service, uow):
    company = make_company()
    quiz = make_quiz(company_id=company.id)
    uow.companies.companies[company.id] = company
    uow.quizzes.quizzes[quiz.id] = quiz

    with pytest.raises(ForbiddenException):
        await quiz_service.submit_quiz(
            company.id, quiz.id, uuid4(),
            QuizSubmitSchema(answers=[])
        )


async def test_submit_quiz_raises_when_frequency_not_passed(quiz_service, uow):
    user_id = uuid4()
    company = make_company()
    quiz = make_quiz(company_id=company.id, frequency=7)
    member = make_member(company_id=company.id, user_id=user_id)
    last_attempt = make_quiz_result(
        user_id=user_id, quiz_id=quiz.id, company_id=company.id,
        created_at=datetime.now(timezone.utc) - timedelta(days=3),
    )

    uow.companies.companies[company.id] = company
    uow.company_members.members[member.id] = member
    uow.quizzes.quizzes[quiz.id] = quiz
    uow.quiz_results.results[last_attempt.id] = last_attempt

    quiz.questions = []

    with pytest.raises(QuizFrequencyException):
        await quiz_service.submit_quiz(
            company.id, quiz.id, user_id,
            QuizSubmitSchema(answers=[])
        )


# --- get_average_by_company ---

async def test_get_average_by_company(quiz_service, uow):
    user_id = uuid4()
    company_id = uuid4()
    r1 = make_quiz_result(user_id=user_id, company_id=company_id, correct_answers=3, total_questions=5)
    r2 = make_quiz_result(user_id=user_id, company_id=company_id, correct_answers=4, total_questions=5)
    uow.quiz_results.results[r1.id] = r1
    uow.quiz_results.results[r2.id] = r2

    avg = await quiz_service.get_average_by_company(user_id, company_id)

    assert avg == round(7 / 10 * 100, 2)


async def test_get_average_by_company_returns_zero_when_no_results(quiz_service, uow):
    avg = await quiz_service.get_average_by_company(uuid4(), uuid4())
    assert avg == 0.0


# --- get_average_by_system ---

async def test_get_average_by_system(quiz_service, uow):
    user_id = uuid4()
    r1 = make_quiz_result(user_id=user_id, company_id=uuid4(), correct_answers=2, total_questions=4)
    r2 = make_quiz_result(user_id=user_id, company_id=uuid4(), correct_answers=3, total_questions=4)
    uow.quiz_results.results[r1.id] = r1
    uow.quiz_results.results[r2.id] = r2

    avg = await quiz_service.get_average_by_system(user_id)

    assert avg == round(5 / 8 * 100, 2)


async def test_get_average_by_system_returns_zero_when_no_results(quiz_service, uow):
    avg = await quiz_service.get_average_by_system(uuid4())
    assert avg == 0.0
