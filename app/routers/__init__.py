from fastapi import APIRouter, status
from app import schemas

router = APIRouter()


@router.get("/", response_model=schemas.HealthSchema)
def health_check():
    return schemas.HealthSchema(status_code=status.HTTP_200_OK, detail="ok", result="working")
