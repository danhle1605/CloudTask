# tests/test_health.py
from unittest.mock import patch
from sqlalchemy.exc import OperationalError


def test_health_live_endpoint(client):
    """Liveness probe /health/live should return 200 and healthy status."""
    response = client.get("/health/live")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "healthy"
    assert "app_version" in json_data


def test_health_ready_endpoint_success(client):
    """Readiness probe /health/ready should return 200 when database responds."""
    response = client.get("/health/ready")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "ready"
    assert json_data["database"] == "connected"


def test_health_ready_endpoint_db_failure(client):
    """Readiness probe /health/ready should return 503 if database fails."""
    with patch("app.routes.db.session.execute", side_effect=OperationalError("Connection failed", {}, Exception())):
        response = client.get("/health/ready")
        assert response.status_code == 503
        json_data = response.get_json()
        assert json_data["status"] == "not_ready"
        assert json_data["database"] == "disconnected"
