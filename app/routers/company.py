from uuid import UUID

from fastapi import APIRouter, Query, status, Depends

from app.models.user import User
from app.schemas.company import CompanyDetailResponseSchema, CompanyUpdateRequestSchema, CompanyCreateRequestSchema, PaginatedCompanyDetailResponseSchema
from app.services.company_service import CompanyService
from app.dependencies import get_current_user_dep, get_company_service

company_router = APIRouter()

def to_company_response(company, owner) -> CompanyDetailResponseSchema:
    return CompanyDetailResponseSchema.model_validate(
        {**company.__dict__, "owner": owner}
    )


@company_router.post(
    "/companies",
    response_model=CompanyDetailResponseSchema,
    status_code=status.HTTP_201_CREATED
)
async def create_company(
    company_request: CompanyCreateRequestSchema,
    current_user: User = Depends(get_current_user_dep),
    company_service: CompanyService = Depends(get_company_service),
):
    company = await company_service.create_company(current_user.id, company_request)
    return to_company_response(company, current_user)


@company_router.get(
    "/companies/{company_id}",
    response_model=CompanyDetailResponseSchema,
    status_code=status.HTTP_200_OK
)
async def get_company_by_id(
    company_id: UUID,
    company_service: CompanyService = Depends(get_company_service)
):
    return await company_service.get_company_by_id(company_id)


@company_router.get(
    "/companies",
    response_model=PaginatedCompanyDetailResponseSchema,
    status_code=status.HTTP_200_OK    
)
async def get_all_companies(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100), 
    company_service: CompanyService = Depends(get_company_service)
):
    companies, total = await company_service.get_all_companies(skip, limit)
    return PaginatedCompanyDetailResponseSchema(
        companies=companies,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + limit) < total,
    )


@company_router.patch(
    "/companies/{company_id}",
    response_model=CompanyDetailResponseSchema,
    status_code=status.HTTP_200_OK
)
async def update_company(
    company_id: UUID,
    data: CompanyUpdateRequestSchema,
    current_user: User = Depends(get_current_user_dep),
    company_service: CompanyService = Depends(get_company_service),
):
    updated_company = await company_service.update_company(current_user.id, company_id, data)
    return to_company_response(updated_company, current_user)


@company_router.delete(
    "/companies/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_company(
    company_id: UUID,
    current_user: User = Depends(get_current_user_dep),
    company_service: CompanyService = Depends(get_company_service),
):
    await company_service.delete_company(current_user.id, company_id)
