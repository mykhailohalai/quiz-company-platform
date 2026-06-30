from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.models.user import User
from app.services.company_member_service import CompanyMemberService
from app.services.company_service import CompanyService
from app.services.user_service import UserService
from app.utils.unit_of_work import UnitOfWork, get_uow


def get_user_service(uow: UnitOfWork = Depends(get_uow)) -> UserService:
    return UserService(uow)


async def get_current_user_dep(
    user_details: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    user_service: UserService = Depends(get_user_service),
) -> User:
    return await user_service.get_current_user(user_details.credentials)


def get_company_service(uow: UnitOfWork = Depends(get_uow)) -> CompanyService:
    return CompanyService(uow)


def get_company_member_service(uow: UnitOfWork = Depends(get_uow)) -> CompanyMemberService:
    return CompanyMemberService(uow)
