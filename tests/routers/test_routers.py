from fastapi import status
from fastapi.testclient import TestClient

from app.routers import health_check
from app.schemas import HealthSchema
from main import app

client = TestClient(app)

def test_health_check_correct_data():
    response = client.get("/")
    assert response.json() == {
        "status_code": status.HTTP_200_OK, 
        "detail": "ok", 
        "result": "working"
    }


def test_health_check_incorrect_data():
    response = client.get("/")
    assert response.json() != {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "detail": "ok",
        "result": "working",
    }
