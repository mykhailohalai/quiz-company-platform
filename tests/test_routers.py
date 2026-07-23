from fastapi import status

from app.routers import health_check
from app.schemas import HealthSchema

def test_health_check_correct_data():
    assert health_check() == HealthSchema(
        status_code=status.HTTP_200_OK, detail="ok", result="working"
    )


def test_health_check_incorrect_data():
    assert health_check() != HealthSchema(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ok", result="waiting"
    )
