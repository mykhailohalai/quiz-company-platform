from pydantic import BaseModel, Field


class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str
