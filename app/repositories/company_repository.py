from uuid import UUID

from sqlalchemy import select

from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.models.company import Company
from app.schemas.company import CompanyUpdateRequestSchema

# TODO: CHANGE THE EXCEPTIONS FROM USER TO COMPANY
from app.exceptions.user_exceptions import UserNotFoundException, UserAlreadyExistsException


class CompanyRepository(BaseRepository[Company, CompanyUpdateRequestSchema]):
    model = Company
    not_found_exception = UserNotFoundException
    already_exists_exception = UserAlreadyExistsException

    @property
    async def is_owner(self, user_id: UUID, company_id: UUID) -> bool:
        company_owner_id = await self.session.execute(
            select(User).where(Company.owner.id == user_id)
        )
        if user_id == company_owner_id:
            return True
        
        return False
        

    async def get_by_company_name(self, company_name: str) -> Company | None:
        result = await self.session.execute(
            select(Company).where(Company.name == company_name)
        )
        return result.scalar_one_or_none()


