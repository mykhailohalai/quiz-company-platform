from app.routers import health_check
from app.schemas import HealthSchema

def test_health_check_correct_data():
    assert health_check() == HealthSchema(
        status_code= 200, detail="ok", result="working"
    )


def test_health_check_incorrect_data():
    assert health_check() != HealthSchema(
        status_code=500, detail="ok", result="waiting"
    )
