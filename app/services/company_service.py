from fastapi import Depends
from uuid import UUID
import logging

from app.utils.unit_of_work import UnitOfWork, get_uow
from app.schemas.company import (
    CompanyCreateRequestSchema, 
    CompanyUpdateRequestSchema
)
from app.models.company import Company
from app.exceptions.general_exceptions import ForbiddenException

logger = logging.getLogger(__name__)


class CompanyService:

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_company(self, current_user_id: UUID, data: CompanyCreateRequestSchema) -> Company:
        data_dict = data.model_dump()
        company = Company(**data_dict, owner_id=current_user_id)
        async with self.uow:
            result = await self.uow.companies.create(company)
            await self.uow.commit()
        logger.info("Company created: id=%s owner_id=%s", result.id, current_user_id)
        return result

    async def get_company_by_id(self, company_id: UUID) -> Company:
        async with self.uow:
            return await self.uow.companies.get_by_id(company_id)

    async def get_all_companies(self, skip: int, limit: int) -> tuple[list[Company], int]:
        async with self.uow:
            return await self.uow.companies.get_all(skip, limit)

    async def update_company(
        self, current_user_id: UUID, company_id: UUID, data: CompanyUpdateRequestSchema
    ) -> Company:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            result = await self.uow.companies.update(company_id, data)
            await self.uow.commit()
            await self.uow.session.refresh(result)
        logger.info("Company updated: id=%s", company_id)
        return result

    async def delete_company(self, current_user_id: UUID, company_id: UUID) -> None:
        async with self.uow:
            company = await self.uow.companies.get_by_id(company_id)
            if not await self.uow.companies.is_owner(current_user_id, company):
                raise ForbiddenException()

            await self.uow.companies.delete(company_id)
            await self.uow.commit()
        logger.info("Company deleted: id=%s", company_id)


def get_company_service(uow=Depends(get_uow)) -> CompanyService:
    return CompanyService(uow)
