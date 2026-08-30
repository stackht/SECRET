"""Per-case analytics from real ingested data (comms/tx/timeline/locations)."""
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
        "/api/v1/cases", json={"title": "Analytics Case", "priority": "HIGH"}, headers=auth
    )
    assert case.status_code == 201
    return {"auth": auth, "client": db_client, "case_number": case.json()["case_number"]}


@pytest.fixture()
def ingested(ctx) -> str:
    """Upload + process CDR, transactions, vehicles and locations files."""
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]

    def upload(name, source_type, content):
        r = client.post(
            f"/api/v1/cases/{case_number}/sources/upload",
            headers=auth,
            files={"file": (name, content.encode(), "text/csv" if name.endswith(".csv") else "text/plain")},
            data={"source_type": source_type},
        )
        assert r.status_code == 201, r.text
        r2 = client.post(f"/api/v1/cases/{case_number}/sources/{r.json()['source_id']}/process", headers=auth)
        assert r2.status_code == 200, r2.text

    upload("cdr.csv", "CDR",
           "caller,receiver,time,duration\nN-1,N-2,2026-08-14T09:12,30\nN-2,N-1,2026-08-14T09:20,10\nN-1,N-3,2026-08-14T13:00,20\nN-1,N-2,2026-08-15T08:00,40\n")
    upload("txn.csv", "TRANSACTION",
           "sender,receiver,amount,time\nA-100,A-200,100000,2026-08-14T10:00\nA-200,A-100,25000,2026-08-15T11:00\n")
    upload("veh.csv", "VEHICLE",
           "registration_no,owner_name\nV-100,P-001\nV-200,P-002\n")
    upload("loc.csv", "LOCATION",
           "entity,area,lat,lon,time\nN-1,Sector 17,19.0,72.8,2026-08-14T09:00\nN-2,Sector 17,19.0,72.8,2026-08-14T09:30\nN-3,Old Town,19.1,72.9,2026-08-14T13:30\n")
    upload("fir.txt", "FIR", "Incident reported near Sector 17.")
    return case_number


def test_communications_analytics(ctx, ingested) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    r = client.get(f"/api/v1/cases/{ingested}/communications", headers=auth)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_communications"] == 4
    assert body["top_contacts"][0]["entity_id"] == "N-1"  # hub
    bursts = body["bursts"]
    assert any(b["entity_id"] == "N-1" for b in bursts)
    assert any(f["source"] == "N-1" and f["target"] == "N-2" for f in body["flows"])


def test_transactions_analytics(ctx, ingested) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    r = client.get(f"/api/v1/cases/{ingested}/transactions", headers=auth)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total_transactions"] == 2
    assert body["total_amount"] == 125000.0
    flows = {f["source"]: f for f in body["flows"]}
    assert flows["A-100"]["target"] == "A-200"
    assert flows["A-100"]["total_amount"] == 100000.0


def test_timeline_locations(ctx, ingested) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    tl = client.get(f"/api/v1/cases/{ingested}/timeline", headers=auth)
    assert tl.status_code == 200, tl.text
    events = tl.json()
    assert len(events) >= 9
    assert all(e["summary"].strip() and e["source_id"] for e in events)
    joined = " ".join(e["summary"] for e in events)
    assert "called" in joined and "transferred" in joined and "registered" in joined

    loc = client.get(f"/api/v1/cases/{ingested}/locations", headers=auth)
    assert loc.status_code == 200, loc.text
    body = loc.json()
    names = {l["name"] for l in body["locations"]}
    assert "Sector 17" in names
    assert body["visits"]


def test_analytics_require_auth(ctx, ingested) -> None:
    assert ctx["client"].get(f"/api/v1/cases/{ingested}/communications").status_code == 401