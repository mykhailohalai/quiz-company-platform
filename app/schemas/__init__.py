from pydantic import BaseModel
from typing import Optional


class HealthSchema(BaseModel):
    status_code: int
    detail: str
    result: str