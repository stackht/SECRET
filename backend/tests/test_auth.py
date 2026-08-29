"""Authentication endpoint tests (Phase 3).

Run against the SQLite-backed client fixture (no external DB required).
"""
from fastapi.testclient import TestClient

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin-secret"


def _login(client: TestClient) -> dict:
    resp = client.post("/api/v1/auth/login", json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_login_success(db_client: TestClient) -> None:
    body = _login(db_client)
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_password(db_client: TestClient) -> None:
    resp = db_client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_login_unknown_user(db_client: TestClient) -> None:
    resp = db_client.post(
        "/api/v1/auth/login",
        json={"username": "ghost", "password": "whatever1"},
    )
    assert resp.status_code == 401


def test_me_requires_auth(db_client: TestClient) -> None:
    resp = db_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_me_with_valid_token(db_client: TestClient) -> None:
    token = _login(db_client)["access_token"]
    resp = db_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == ADMIN_USERNAME
    assert body["role"] == "admin"
    assert "created_at" in body


def test_refresh_returns_new_pair(db_client: TestClient) -> None:
    refresh_token = _login(db_client)["refresh_token"]
    resp = db_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_refresh_rejects_access_token(db_client: TestClient) -> None:
    access_token = _login(db_client)["access_token"]
    resp = db_client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401


def test_me_rejects_garbage_token(db_client: TestClient) -> None:
    resp = db_client.get("/api/v1/auth/me", headers={"Authorization": "Bearer junk.token.value"})
    assert resp.status_code == 401
