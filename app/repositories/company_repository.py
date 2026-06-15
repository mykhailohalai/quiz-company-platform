from uuid import UUID

from sqlalchemy import select

from app.repositories.base_repository import BaseRepository
from app.models.company import Company
from app.schemas.company import CompanyUpdateRequestSchema
from app.exceptions.company_exceptions import (
    CompanyNotFoundException,
    CompanyAlreadyExistsException,
)

class CompanyRepository(BaseRepository[Company, CompanyUpdateRequestSchema]):
    model = Company
    not_found_exception = CompanyNotFoundException
    already_exists_exception = CompanyAlreadyExistsException

    async def is_owner(self, user_id: UUID, company: Company) -> bool:
        if user_id == company.owner_id:
            return True
        return False

    async def get_by_company_name(self, company_name: str) -> Company | None:
        result = await self.session.execute(
            select(Company).where(Company.name == company_name)
        )
        return result.scalar_one_or_none()
