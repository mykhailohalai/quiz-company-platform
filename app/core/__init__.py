from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    app_name: str = "Meduzzen back-end"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_reload: bool = True
    allowed_origins: List[str] = []

    class Config:
        env_file = ".env"


settings = Settings()
