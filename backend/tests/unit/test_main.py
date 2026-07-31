# Test that the FastAPI app is importable and the health endpoint returns ok.
from app.main import app


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "The Daily Roast AI"
    assert response.json()["environment"] == "local"