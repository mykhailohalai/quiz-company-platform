from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from fastapi import status

from app.models.company import Company, CompanyVisibility
from app.models.user import User
from main import app


client = TestClient(app)

now = datetime.now()


def make_owner(**kwargs):
    defaults = dict(
        id=uuid4(),
        username="owner",
        email="owner@example.com",
        password="hashed-password",
        created_at=now,
        updated_at=now,
    )
    defaults.update(kwargs)
    return User(**defaults)


def make_company(**kwargs):
    owner = kwargs.pop("owner", None) or make_owner()
    defaults = dict(
        id=uuid4(),
        name="Acme",
        description="desc",
        owner_id=owner.id,
        owner=owner,
        visibility=CompanyVisibility.Visible_to_all,
    )
    defaults.update(kwargs)
    return Company(**defaults)


async def get_current_user(token):
    return make_owner()


def test_create_company_return_company(mock_company_service, mock_user_service):
    async def create_company(current_user_id, data):
        return make_company(name=data.name, description=data.description, owner_id=current_user_id)

    mock_company_service.create_company = create_company
    mock_user_service.get_current_user = get_current_user

    response = client.post(
        "/companies",
        json={"name": "Acme", "description": "desc"},
        headers={"Authorization": "Bearer faketoken"},
    )

    assert response.status_code == status.HTTP_201_CREATED
    body = response.json()
    assert body["name"] == "Acme"
    assert body["description"] == "desc"


def test_get_company_by_id_should_success(mock_company_service):
    company = make_company()

    async def get_company_by_id(company_id):
        return company

    mock_company_service.get_company_by_id = get_company_by_id

    response = client.get(f"/companies/{company.id}")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(company.id)
    assert body["name"] == "Acme"


def test_get_all_companies_should_success(mock_company_service):
    company = make_company()

    async def get_all_companies(skip, limit):
        companies = [company]
        return companies, len(companies)

    mock_company_service.get_all_companies = get_all_companies

    response = client.get("/companies")

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["total"] == 1
    assert body["companies"][0]["id"] == str(company.id)


def test_update_company_should_success(mock_company_service, mock_user_service):
    company_id = uuid4()

    async def update_company(current_user_id, company_id_, data):
        return make_company(id=company_id_, name=data.name)

    mock_company_service.update_company = update_company
    mock_user_service.get_current_user = get_current_user

    response = client.patch(
        f"/companies/{company_id}",
        json={"name": "New name"},
        headers={"Authorization": "Bearer faketoken"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["id"] == str(company_id)
    assert body["name"] == "New name"


def test_delete_company_should_success(mock_company_service, mock_user_service):
    company_id = uuid4()

    async def delete_company(current_user_id, company_id_):
        return None

    mock_company_service.delete_company = delete_company
    mock_user_service.get_current_user = get_current_user

    response = client.delete(
        f"/companies/{company_id}",
        headers={"Authorization": "Bearer faketoken"},
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
