"""Audit service tests (original Phase 13)."""
import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base, get_db_session
from app.core.security import hash_password
from app.main import app
from app.models.user import User, UserRole

ADMIN = "admin"
PW = "admin-secret"


@pytest.fixture()
def audit_client() -> TestClient:
    eng = create_async_engine("sqlite+aiosqlite:///:memory:")
    S = async_sessionmaker(eng, expire_on_commit=False)

    async def setup():
        async with eng.begin() as c:
            await c.run_sync(Base.metadata.create_all)
        async with S() as s:
            s.add(User(username="admin", email="admin@example.com",
                      password_hash=hash_password(PW), role=UserRole.ADMIN.value))
            await s.commit()

    asyncio.run(setup())

    async def override_db():
        async with S() as s:
            yield s

    app.dependency_overrides[get_db_session] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    asyncio.run(eng.dispose())


def _auth(client: TestClient) -> dict:
    resp = client.post("/api/v1/auth/login", json={"username": ADMIN, "password": PW})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_record_and_list_audit(audit_client: TestClient) -> None:
    auth = _auth(audit_client)
    record_resp = audit_client.post(
        "/api/v1/audit",
        json={"action": "case.created", "object_type": "case", "object_id": "CASE-1", "result": {"status": "ok"}},
        headers=auth,
    )
    assert record_resp.status_code == 201, record_resp.text
    body = record_resp.json()
    assert body["action"] == "case.created"

    list_resp = audit_client.get("/api/v1/audit", headers=auth)
    assert list_resp.status_code == 200
    assert any(e["action"] == "case.created" for e in list_resp.json())


def test_audit_requires_auth(audit_client: TestClient) -> None:
    resp = audit_client.get("/api/v1/audit")
    assert resp.status_code == 401
