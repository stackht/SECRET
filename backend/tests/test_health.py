"""Health-check endpoint and app-bootstrap tests (Phase 2)."""
from fastapi.testclient import TestClient


def test_app_creates_and_serves_openapi(client: TestClient) -> None:
    """The app exposes OpenAPI schema."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "openapi" in resp.json()


def test_health_returns_ok(client: TestClient) -> None:
    """GET /health returns ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "SECRET API"
