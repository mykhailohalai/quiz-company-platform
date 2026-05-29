from pydantic import BaseModel


class HealthSchema(BaseModel):
    status_code: int
    detail: str
    result: str
