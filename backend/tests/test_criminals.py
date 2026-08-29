"""Criminal API tests (Phase 4).

Run against the SQLite-backed client fixture with the seeded admin user.
"""
import pytest
from fastapi.testclient import TestClient

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin-secret"


@pytest.fixture()
def auth(db_client: TestClient) -> dict:
    """Return an Authorization header for the seeded admin."""
    resp = db_client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def created_profile(db_client: TestClient, auth: dict):
    payload = {
        "profile_type": "PERSON",
        "name": "Person A",
        "aliases": ["A. Khan", "Alpha"],
        "risk_score": 94.0,
        "risk_level": "CRITICAL",
        "confidence": 96.0,
        "status": "MONITORED",
        "attributes": {"citizenship": "fictional"},
    }
    resp = db_client.post("/api/v1/criminals", json=payload, headers=auth)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_profile(db_client: TestClient, auth: dict) -> None:
    payload = {
        "profile_type": "PERSON",
        "name": "Person A",
        "aliases": ["A. Khan", "Alpha"],
        "risk_score": 94.0,
        "risk_level": "CRITICAL",
        "confidence": 96.0,
        "status": "MONITORED",
        "attributes": {"citizenship": "fictional"},
    }
    resp = db_client.post("/api/v1/criminals", json=payload, headers=auth)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "Person A"
    assert body["profile_type"] == "PERSON"
    assert body["risk_level"] == "CRITICAL"
    assert body["secret_id"].startswith("P-")


def test_list_profiles_contains_created(db_client: TestClient, auth: dict, created_profile) -> None:
    resp = db_client.get("/api/v1/criminals", headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    ids = [item["id"] for item in data["items"]]
    assert created_profile["id"] in ids


def test_search_by_name(db_client: TestClient, auth: dict, created_profile) -> None:
    resp = db_client.get("/api/v1/criminals", params={"q": "Person A"}, headers=auth)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert any(i["id"] == created_profile["id"] for i in items)


def test_filter_by_type(db_client: TestClient, auth: dict, created_profile) -> None:
    resp = db_client.get("/api/v1/criminals", params={"profile_type": "PERSON"}, headers=auth)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(i["profile_type"] == "PERSON" for i in items)


def test_get_by_secret_id(db_client: TestClient, auth: dict, created_profile) -> None:
    resp = db_client.get(f"/api/v1/criminals/{created_profile['secret_id']}", headers=auth)
    assert resp.status_code == 200
    assert resp.json()["id"] == created_profile["id"]


def test_get_missing_returns_404(db_client: TestClient, auth: dict) -> None:
    resp = db_client.get("/api/v1/criminals/P-9999", headers=auth)
    assert resp.status_code == 404


def test_update_profile(db_client: TestClient, auth: dict, created_profile) -> None:
    resp = db_client.patch(
        f"/api/v1/criminals/{created_profile['secret_id']}",
        json={"risk_score": 88.0, "risk_level": "HIGH"},
        headers=auth,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk_score"] == 88.0
    assert body["risk_level"] == "HIGH"


def test_list_requires_auth(db_client: TestClient) -> None:
    resp = db_client.get("/api/v1/criminals")
    assert resp.status_code == 401


def test_create_requires_privilege(db_client: TestClient) -> None:
    """A non-admin token should be rejected for writes."""
    # Seed a viewer user directly and login as them.
    import asyncio

    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.core.database import Base, get_db_session
    from app.core.security import hash_password
    from app.main import app
    from app.models.user import User, UserRole

    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    S = async_sessionmaker(eng, expire_on_commit=False)

    async def setup():
        async with eng.begin() as c:
            await c.run_sync(Base.metadata.create_all)
        async with S() as s:
            s.add(User(username="viewer", email="viewer@example.com",
                      password_hash=hash_password("viewer-pass-1"), role=UserRole.VIEWER.value))
            await s.commit()

    asyncio.run(setup())

    async def override():
        async with S() as s:
            yield s

    app.dependency_overrides[get_db_session] = override
    try:
        with TestClient(app) as c:
            login = c.post("/api/v1/auth/login",
                           json={"username": "viewer", "password": "viewer-pass-1"})
            assert login.status_code == 200
            tok = login.json()["access_token"]
            create = c.post("/api/v1/criminals",
                            json={"profile_type": "PERSON", "name": "X"},
                            headers={"Authorization": f"Bearer {tok}"})
            assert create.status_code == 403
    finally:
        app.dependency_overrides.clear()
        asyncio.run(eng.dispose())
