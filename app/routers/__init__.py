from fastapi import APIRouter
from app import schemas

router = APIRouter()


@router.get("/", response_model=schemas.HealthSchema)
def health_check():
    return schemas.HealthSchema(status_code=200, detail="ok", result="working")
