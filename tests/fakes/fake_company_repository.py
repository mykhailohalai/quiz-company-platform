from app.exceptions.company_exceptions import (
    CompanyAlreadyExistsException,
    CompanyNotFoundException,
)
from app.models.company import CompanyVisibility


class FakeCompanyRepository:
    def __init__(self, companies=None):
        self.companies = {company.id: company for company in (companies or [])}

    async def get_all(self, skip=0, limit=10):
        companies = list(self.companies.values())
        return companies[skip : skip + limit], len(companies)

    async def get_all_visible(self, skip=0, limit=10):
        companies = [
            company
            for company in self.companies.values()
            if company.visibility == CompanyVisibility.Visible_to_all
        ]
        return companies[skip : skip + limit], len(companies)

    async def get_by_id(self, company_id):
        company = self.companies.get(company_id)
        if company is None:
            raise CompanyNotFoundException(company_id)
        return company

    async def get_by_company_name(self, company_name):
        for company in self.companies.values():
            if company.name == company_name:
                return company
        return None

    async def create(self, company):
        for existing in self.companies.values():
            if existing.name == company.name:
                raise CompanyAlreadyExistsException("name")
        self.companies[company.id] = company
        return company

    async def delete(self, company_id):
        if company_id not in self.companies:
            raise CompanyNotFoundException(company_id)
        del self.companies[company_id]
        return True

    async def update(self, company_id, updated_company):
        company = self.companies.get(company_id)
        if company is None:
            raise CompanyNotFoundException(company_id)
        for field, value in updated_company.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
        return company

    async def is_owner(self, user_id, company) -> bool:
        return user_id == company.owner_id
