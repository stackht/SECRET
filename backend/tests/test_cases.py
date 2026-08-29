"""Case API tests (Phase 5).

Run against the SQLite-backed client fixture with the seeded admin.
"""
import pytest
from fastapi.testclient import TestClient

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin-secret"


@pytest.fixture()
def auth(db_client: TestClient) -> dict:
    resp = db_client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def profile(db_client: TestClient, auth: dict) -> dict:
    resp = db_client.post(
        "/api/v1/criminals",
        json={"profile_type": "PERSON", "name": "Person A", "risk_level": "HIGH", "risk_score": 80.0},
        headers=auth,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.fixture()
def created_case(db_client: TestClient, auth: dict) -> dict:
    resp = db_client.post(
        "/api/v1/cases",
        json={"title": "Organized Network Analysis", "priority": "HIGH", "status": "OPEN"},
        headers=auth,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_case_autogenerates_number(db_client: TestClient, auth: dict, created_case) -> None:
    assert created_case["case_number"].startswith("CASE-")
    assert created_case["priority"] == "HIGH"


def test_list_cases_contains_created(db_client: TestClient, auth: dict, created_case) -> None:
    resp = db_client.get("/api/v1/cases", headers=auth)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(item["id"] == created_case["id"] for item in data["items"])


def test_get_case_by_number(db_client: TestClient, auth: dict, created_case) -> None:
    resp = db_client.get(f"/api/v1/cases/{created_case['case_number']}", headers=auth)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == created_case["id"]
    assert body["profiles"] == []


def test_get_missing_case_404(db_client: TestClient, auth: dict) -> None:
    resp = db_client.get("/api/v1/cases/CASE-9999", headers=auth)
    assert resp.status_code == 404


def test_update_case(db_client: TestClient, auth: dict, created_case) -> None:
    resp = db_client.patch(
        f"/api/v1/cases/{created_case['case_number']}",
        json={"status": "IN_PROGRESS", "priority": "CRITICAL"},
        headers=auth,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "IN_PROGRESS"
    assert body["priority"] == "CRITICAL"


def test_associate_and_list_profiles(db_client: TestClient, auth: dict, created_case, profile) -> None:
    resp = db_client.post(
        f"/api/v1/cases/{created_case['case_number']}/profiles",
        json={"profile_id": profile["id"], "role_in_case": "PRIMARY"},
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    assert any(p["id"] == profile["id"] for p in resp.json()["profiles"])

    list_resp = db_client.get(f"/api/v1/cases/{created_case['case_number']}/profiles", headers=auth)
    assert list_resp.status_code == 200
    assert any(p["id"] == profile["id"] for p in list_resp.json())


def test_associate_duplicate_409(db_client: TestClient, auth: dict, created_case, profile) -> None:
    db_client.post(
        f"/api/v1/cases/{created_case['case_number']}/profiles",
        json={"profile_id": profile["id"]},
        headers=auth,
    )
    resp = db_client.post(
        f"/api/v1/cases/{created_case['case_number']}/profiles",
        json={"profile_id": profile["id"]},
        headers=auth,
    )
    assert resp.status_code == 409


def test_dissociate_profile(db_client: TestClient, auth: dict, created_case, profile) -> None:
    db_client.post(
        f"/api/v1/cases/{created_case['case_number']}/profiles",
        json={"profile_id": profile["id"]},
        headers=auth,
    )
    resp = db_client.delete(
        f"/api/v1/cases/{created_case['case_number']}/profiles/{profile['id']}",
        headers=auth,
    )
    assert resp.status_code == 204

    list_resp = db_client.get(f"/api/v1/cases/{created_case['case_number']}/profiles", headers=auth)
    assert all(p["id"] != profile["id"] for p in list_resp.json())


def test_associate_missing_profile_404(db_client: TestClient, auth: dict, created_case) -> None:
    resp = db_client.post(
        f"/api/v1/cases/{created_case['case_number']}/profiles",
        json={"profile_id": 999999},
        headers=auth,
    )
    assert resp.status_code == 404


def test_case_list_requires_auth(db_client: TestClient) -> None:
    resp = db_client.get("/api/v1/cases")
    assert resp.status_code == 401


def test_create_case_requires_privilege(db_client: TestClient) -> None:
    """A viewer role cannot create cases."""
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
            s.add(User(username="viewer2", email="viewer2@example.com",
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
                           json={"username": "viewer2", "password": "viewer-pass-1"})
            assert login.status_code == 200
            tok = login.json()["access_token"]
            resp = c.post("/api/v1/cases", json={"title": "X"},
                          headers={"Authorization": f"Bearer {tok}"})
            assert resp.status_code == 403
    finally:
        app.dependency_overrides.clear()
        asyncio.run(eng.dispose())
