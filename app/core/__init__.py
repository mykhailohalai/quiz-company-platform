from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Meduzzen back-end"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_reload: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
