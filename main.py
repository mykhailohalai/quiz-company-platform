from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.routers import router
from app.routers.user import user_router
from app.routers.company import company_router
from app.routers.company_member import company_member_router
from app.core import settings
from app.exceptions.general_exceptions import ForbiddenException
from app.exceptions.user_exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    InvalidCredentialsException,
)
from app.exceptions.company_exceptions import (
    CompanyAlreadyExistsException,
    CompanyNotFoundException,
)
from app.exceptions.company_member_exceptions import (
    CompanyMemberNotFoundException,
    CompanyMemberAlreadyExistsException,
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
app.include_router(company_member_router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


_HTTP_EXCEPTION_MAP: dict[type[Exception], int] = {
    UserNotFoundException: status.HTTP_404_NOT_FOUND,
    UserAlreadyExistsException: status.HTTP_409_CONFLICT,
    InvalidCredentialsException: status.HTTP_401_UNAUTHORIZED,
    CompanyNotFoundException: status.HTTP_404_NOT_FOUND,
    CompanyAlreadyExistsException: status.HTTP_409_CONFLICT,
    CompanyMemberNotFoundException: status.HTTP_404_NOT_FOUND,
    CompanyMemberAlreadyExistsException: status.HTTP_409_CONFLICT,
    ForbiddenException: status.HTTP_403_FORBIDDEN,
}

for _exc_class, _status_code in _HTTP_EXCEPTION_MAP.items():
    def _make_handler(code: int):
        async def handler(_: Request, ex: Exception):
            logger.warning("%s", ex)
            return JSONResponse(status_code=code, content={"detail": str(ex)})
        return handler
    app.add_exception_handler(_exc_class, _make_handler(_status_code))


@app.exception_handler(Exception)
async def server_error_handler(request: Request, ex: Exception):
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Server error"}
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
