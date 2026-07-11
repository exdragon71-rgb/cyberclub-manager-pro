from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["app"] == "CyberClub Manager Pro"
    assert response_data["version"] == "0.1.0"
    assert response_data["status"] == "running"


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_unknown_endpoint_returns_404() -> None:
    response = client.get("/this-endpoint-does-not-exist")

    assert response.status_code == 404