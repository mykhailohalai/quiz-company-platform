from pydantic import BaseModel
from typing import Optional


class HealthSchema(BaseModel):
    status_code: Optional[int] = None
    detail: Optional[str] = None
    result: Optional[str] = None
