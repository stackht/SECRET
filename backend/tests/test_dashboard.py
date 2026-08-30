"""Dashboard summary counters (Phase 7)."""
import pytest
from fastapi.testclient import TestClient

ADMIN = "admin"
PW = "admin-secret"


@pytest.fixture()
def auth(db_client: TestClient):
    resp = db_client.post("/api/v1/auth/login", json={"username": ADMIN, "password": PW})
    assert resp.status_code == 200
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_summary_reflects_real_counts(db_client: TestClient, auth: dict) -> None:
    summary = db_client.get("/api/v1/dashboard/summary", headers=auth)
    assert summary.status_code == 200, summary.text
    body = summary.json()
    assert body["cases"] == 0
    assert body["sources"] == 0
    assert isinstance(body["priority_distribution"], dict)

    # Create case + upload + process -> counters grow.
    case = db_client.post("/api/v1/cases", json={"title": "Dash Case", "priority": "HIGH"}, headers=auth)
    assert case.status_code == 201
    cn = case.json()["case_number"]
    csv = b"caller,receiver,time\nN-1,N-2,2026-08-14T09:00\n"
    up = db_client.post(
        f"/api/v1/cases/{cn}/sources/upload",
        headers=auth,
        files={"file": ("cdr.csv", csv, "text/csv")},
        data={"source_type": "CDR"},
    )
    assert up.status_code == 201
    db_client.post(f"/api/v1/cases/{cn}/sources/{up.json()['source_id']}/process", headers=auth)

    body = db_client.get("/api/v1/dashboard/summary", headers=auth).json()
    assert body["cases"] == 1
    assert body["sources"] == 1
    assert body["entities"] == 2
    assert body["relationships"] == 2
    assert body["priority_distribution"].get("HIGH") == 1


def test_summary_requires_auth(db_client: TestClient) -> None:
    assert db_client.get("/api/v1/dashboard/summary").status_code == 401