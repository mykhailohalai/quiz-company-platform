from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.repositories.base_repository import BaseRepository
from app.models.company import Company, CompanyVisibility
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

    async def get_all_visible(self, skip: int = 0, limit: int = 10) -> tuple[list[Company], int]:
        condition = Company.visibility == CompanyVisibility.Visible_to_all
        total = await self.session.scalar(
            select(func.count()).select_from(Company).where(condition)
        )
        result = await self.session.execute(
            select(Company).where(condition).options(joinedload(Company.owner)). offset(skip).limit(limit)
        )
        return result.scalars().all(), total
