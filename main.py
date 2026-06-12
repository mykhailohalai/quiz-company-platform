from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from app.routers import router
from app.routers.user import user_router
from app.core import settings
from app.exceptions.user_exceptions import UserAlreadyExistsException, UserNotFoundException

app = FastAPI(title=settings.app_name)

# db mock
todos = {}

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
        content= {"details": str(ex)}
    )


@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_handler(request: Request, ex: UserAlreadyExistsException):
    logger.warning("User creation conflict: %s", ex)
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content = {"details": str(ex)}
    )


@app.exception_handler(Exception)
async def server_error_handler(request: Request, ex: Exception):
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"details": "Server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
