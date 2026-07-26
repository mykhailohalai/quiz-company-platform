from uuid import uuid4

import pytest

from app.exceptions.company_exceptions import (
    CompanyAlreadyExistsException,
    CompanyNotFoundException,
)
from app.exceptions.general_exceptions import ForbiddenException
from app.models.company import Company, CompanyVisibility
from app.schemas.company import CompanyCreateRequestSchema, CompanyUpdateRequestSchema


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


async def test_create_company_persists_with_owner(company_service, uow):
    owner_id = uuid4()
    data = CompanyCreateRequestSchema(name="Acme", description="desc")

    company = await company_service.create_company(owner_id, data)

    assert company.name == "Acme"
    assert company.owner_id == owner_id
    assert uow.companies.companies[company.id] is company
    assert uow.committed is True


async def test_create_company_raises_when_name_taken(company_service, uow):
    uow.companies.companies[uuid4()] = make_company(name="Acme")
    data = CompanyCreateRequestSchema(name="Acme", description="other")

    with pytest.raises(CompanyAlreadyExistsException):
        await company_service.create_company(uuid4(), data)


async def test_get_company_by_id_returns_company(company_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    result = await company_service.get_company_by_id(company.id)

    assert result is company


async def test_get_company_by_id_raises_when_missing(company_service):
    with pytest.raises(CompanyNotFoundException):
        await company_service.get_company_by_id(uuid4())


async def test_get_all_companies_returns_only_visible(company_service, uow):
    visible = make_company(name="Visible", visibility=CompanyVisibility.VISIBLE_TO_ALL)
    hidden = make_company(name="Hidden", visibility=CompanyVisibility.HIDDEN)
    uow.companies.companies[visible.id] = visible
    uow.companies.companies[hidden.id] = hidden

    companies, total = await company_service.get_all_companies(skip=0, limit=10)

    assert companies == [visible]
    assert total == 1


async def test_update_company_updates_fields(company_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company
    data = CompanyUpdateRequestSchema(name="New name")

    updated = await company_service.update_company(company.owner_id, company.id, data)

    assert updated.name == "New name"
    assert uow.committed is True


async def test_update_company_raises_when_missing(company_service):
    data = CompanyUpdateRequestSchema(name="New name")

    with pytest.raises(CompanyNotFoundException):
        await company_service.update_company(uuid4(), uuid4(), data)


async def test_update_company_raises_when_not_owner(company_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company
    data = CompanyUpdateRequestSchema(name="New name")

    with pytest.raises(ForbiddenException):
        await company_service.update_company(uuid4(), company.id, data)


async def test_delete_company_removes_from_repository(company_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    await company_service.delete_company(company.owner_id, company.id)

    assert company.id not in uow.companies.companies
    assert uow.committed is True


async def test_delete_company_raises_when_missing(company_service):
    with pytest.raises(CompanyNotFoundException):
        await company_service.delete_company(uuid4(), uuid4())


async def test_delete_company_raises_when_not_owner(company_service, uow):
    company = make_company()
    uow.companies.companies[company.id] = company

    with pytest.raises(ForbiddenException):
        await company_service.delete_company(uuid4(), company.id)
