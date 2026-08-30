"""Global search (Phase 21)."""
import pytest
from fastapi.testclient import TestClient

ADMIN = "admin"
PW = "admin-secret"


@pytest.fixture()
def ctx(db_client: TestClient):
    resp = db_client.post("/api/v1/auth/login", json={"username": ADMIN, "password": PW})
    auth = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    case = db_client.post("/api/v1/cases", json={"title": "Orion Racketeering", "priority": "HIGH"}, headers=auth)
    cn = case.json()["case_number"]
    client = db_client
    # Add an entity via the real ingestion path.
    csv = b"caller,receiver,time\nN-4821,N-9044,2026-08-14T09:00\n"
    up = client.post(
        f"/api/v1/cases/{cn}/sources/upload",
        headers=auth,
        files={"file": ("cdr.csv", csv, "text/csv")},
        data={"source_type": "CDR"},
    )
    client.post(f"/api/v1/cases/{cn}/sources/{up.json()['source_id']}/process", headers=auth)
    return {"auth": auth, "client": client, "cn": cn}


def test_search_entities_and_sources(ctx) -> None:
    resp = ctx["client"].get("/api/v1/search", params={"q": "N-4821"}, headers=ctx["auth"])
    assert resp.status_code == 200
    body = resp.json()
    assert any(e["entity_id"] == "N-4821" for e in body["entities"])


def test_search_cases_by_title(ctx) -> None:
    resp = ctx["client"].get("/api/v1/search", params={"q": "orion"}, headers=ctx["auth"])
    assert resp.status_code == 200
    assert any(c["title"] == "Orion Racketeering" for c in resp.json()["cases"])


def test_search_requires_auth(ctx) -> None:
    assert ctx["client"].get("/api/v1/search", params={"q": "x"}).status_code == 401