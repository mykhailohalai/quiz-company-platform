from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Meduzzen back-end"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_reload: bool = True
    allowed_origins: list[str] = []
    db_password: str = "postgres"
    db_user: str = "postgres"
    db_name: str = "python-back-end"
    db_host: str = "db"
    db_port: int = 5432
    redis_host: str = "redis"
    redis_port: int = 6379
    auth0_domain: str = ""
    auth0_audience: str = ""
    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60


    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
