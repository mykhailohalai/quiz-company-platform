from fastapi import status
from fastapi.testclient import TestClient

from app.schemas import HealthSchema
from main import app

client = TestClient(app)

def test_health_check_correct_data():
    response = client.get("/")
    assert response.json() == HealthSchema(
        status_code=status.HTTP_200_OK, detail="ok", result="working"
    ).model_dump()


def test_health_check_incorrect_data():
    response = client.get("/")
    assert response.json() != HealthSchema(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ok", result="waiting"
    ).model_dump()
