"""Alert generation tests (Phase 18) — computed from persisted analytics."""
import pytest
from fastapi.testclient import TestClient

ADMIN = "admin"
PW = "admin-secret"


@pytest.fixture()
def ctx(db_client: TestClient):
    resp = db_client.post("/api/v1/auth/login", json={"username": ADMIN, "password": PW})
    assert resp.status_code == 200
    auth = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    case = db_client.post(
        "/api/v1/cases", json={"title": "Alert Case", "priority": "HIGH"}, headers=auth
    )
    assert case.status_code == 201
    return {"auth": auth, "client": db_client, "case_number": case.json()["case_number"]}


def _ingest(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    cn = ctx["case_number"]

    def upload(name, source_type, content):
        r = client.post(
            f"/api/v1/cases/{cn}/sources/upload",
            headers=auth,
            files={"file": (name, content.encode(), "text/csv")},
            data={"source_type": source_type},
        )
        assert r.status_code == 201, r.text
        r2 = client.post(f"/api/v1/cases/{cn}/sources/{r.json()['source_id']}/process", headers=auth)
        assert r2.status_code == 200, r2.text

    # Hub N-1 has an hourly burst (median 1, one hour has 4+).
    upload("cdr.csv", "CDR",
           "caller,receiver,time\n"
           "N-1,N-2,2026-08-14T09:00\n"
           "N-1,N-3,2026-08-14T09:15\n"
           "N-1,N-4,2026-08-14T09:30\n"
           "N-1,N-5,2026-08-14T09:45\n"
           "N-1,N-2,2026-08-15T10:00\n"
           "N-1,N-3,2026-08-15T11:00\n")
    # Big transfer above threshold.
    upload("txn.csv", "TRANSACTION",
           "sender,receiver,amount,time\n"
           "A-100,A-200,12000000,2026-08-14T10:00\n")


def test_generate_alerts_from_burst_and_transfer(ctx) -> None:
    _ingest(ctx)
    client = ctx["client"]
    auth = ctx["auth"]
    cn = ctx["case_number"]

    gen = client.post(f"/api/v1/cases/{cn}/alerts/generate", headers=auth)
    assert gen.status_code == 200, gen.text
    body = gen.json()
    assert body["created"] >= 2
    titles = {a["title"] for a in body["alerts"]}
    assert any("burst" in t for t in titles)
    assert any("High-value transfer" in t for t in titles)

    lst = client.get(f"/api/v1/cases/{cn}/alerts", headers=auth)
    assert lst.status_code == 200
    alerts = lst.json()
    assert len(alerts) >= 2
    target = next(a for a in alerts if "burst" in a["title"])
    assert target["severity"] == "HIGH"
    assert target["score"] >= 3
    assert target["status"] == "NEW"

    # Re-generate must not duplicate.
    gen2 = client.post(f"/api/v1/cases/{cn}/alerts/generate", headers=auth)
    assert gen2.json()["created"] == 0


def test_alert_status_transition(ctx) -> None:
    _ingest(ctx)
    client = ctx["client"]
    auth = ctx["auth"]
    cn = ctx["case_number"]

    client.post(f"/api/v1/cases/{cn}/alerts/generate", headers=auth)
    alerts = client.get(f"/api/v1/cases/{cn}/alerts", headers=auth).json()
    alert_id = alerts[0]["id"]

    update = client.patch(f"/api/v1/cases/{cn}/alerts/{alert_id}", json={"status": "DISMISSED"}, headers=auth)
    assert update.status_code == 200, update.text
    assert update.json()["status"] == "DISMISSED"
    assert update.json()["reviewed_by"] is not None

    bad = client.patch(f"/api/v1/cases/{cn}/alerts/{alert_id}", json={"status": "BOGUS"}, headers=auth)
    assert bad.status_code == 422


def test_alerts_require_auth(ctx) -> None:
    assert ctx["client"].get(f"/api/v1/cases/{ctx['case_number']}/alerts").status_code == 401