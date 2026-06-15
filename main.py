from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.routers import router
from app.routers.user import user_router
from app.routers.company import company_router
from app.core import settings
from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
)
from app.exceptions.company_exceptions import (
    CompanyAlreadyExistsException, 
    CompanyNotFoundException
)

app = FastAPI(title=settings.app_name)

origins = settings.allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(router)
app.include_router(user_router)
app.include_router(company_router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, ex: UserNotFoundException):
    logger.warning("User not found: %s", ex)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content= {"detail": str(ex)}
    )


@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_handler(request: Request, ex: UserAlreadyExistsException):
    logger.warning("User creation conflict: %s", ex)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content = {"detail": str(ex)}
    )


@app.exception_handler(InvalidCredentialsException)
async def invalid_credentials_handler(request: Request, ex: InvalidCredentialsException):
    logger.warning("Invalid credentials: %s", ex)
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(ex)}
    )


@app.exception_handler(CompanyNotFoundException)
async def company_not_found_handler(request: Request, ex: CompanyNotFoundException):
    logger.warning("Company not found: %s", ex)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(ex)}
    )


@app.exception_handler(CompanyAlreadyExistsException)
async def company_already_exists_handler(
    request: Request, ex: CompanyAlreadyExistsException
):
    logger.warning("Company creation conflict: %s", ex)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT, content={"detail": str(ex)}
    )


@app.exception_handler(ForbiddenException)
async def forbidden_exception(request: Request, ex: ForbiddenException):
    logger.warning("Invalid user: %s", ex)
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(ex)}
    )
@app.exception_handler(Exception)
async def server_error_handler(request: Request, ex: Exception):
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
