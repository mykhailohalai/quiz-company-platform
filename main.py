from fastapi import FastAPI
import uvicorn

from app.routers import router
from app.core import settings

app = FastAPI(title=settings.app_name)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
    )
