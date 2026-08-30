"""Backend end-to-end pipeline test (Phase 2).

Proves the real flow over uploaded data without any synthetic shortcuts:
upload -> process -> persist -> materialize -> graph -> analytics.
"""
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
        "/api/v1/cases", json={"title": "E2E Pipeline Case", "priority": "HIGH"}, headers=auth
    )
    assert case.status_code == 201, case.text
    return {"auth": auth, "client": db_client, "case_number": case.json()["case_number"]}


def test_upload_to_analytics_pipeline(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]

    # 1. Upload a real CDR file.
    csv_bytes = (
        b"caller,receiver,time,duration\n"
        b"N-4821,N-9044,2026-08-14T09:12,34\n"
        b"N-9044,N-7712,2026-08-14T10:00,12\n"
        b"N-7712,N-4821,2026-08-14T11:30,8\n"
    )
    up = client.post(
        f"/api/v1/cases/{case_number}/sources/upload",
        headers=auth,
        files={"file": ("cdr.csv", csv_bytes, "text/csv")},
        data={"source_type": "CDR"},
    )
    assert up.status_code == 201
    sid = up.json()["source_id"]

    # 2. Process -> persist entities + relationships.
    processed = client.post(f"/api/v1/cases/{case_number}/sources/{sid}/process", headers=auth)
    assert processed.status_code == 200
    assert processed.json()["metrics"]["entities_persisted"] == 3   # phones
    assert processed.json()["metrics"]["relationships_persisted"] == 6  # called + received_call per row

    # 3. Read-back persisted data with provenance.
    entities = client.get(f"/api/v1/cases/{case_number}/entities", headers=auth)
    assert entities.status_code == 200
    ids = {e["entity_id"] for e in entities.json()}
    assert {"N-4821", "N-9044", "N-7712"} <= ids
    assert all(e["source_ids"] == [sid] for e in entities.json())

    rels = client.get(f"/api/v1/cases/{case_number}/relationships", headers=auth)
    assert rels.status_code == 200
    assert all(r["source_ids"] == [sid] for r in rels.json())

    # 4. Materialize into the graph store.
    mat = client.post("/api/v1/graph/materialize", headers=auth)
    assert mat.status_code == 200
    assert mat.json()["edges"] >= 3

    # 5. Graph network reflects the ingested phones.
    network = client.get("/api/v1/graph/network", headers=auth)
    assert network.status_code == 200
    node_ids = {n["id"] for n in network.json()["nodes"]}
    assert "N-4821" in node_ids and "N-9044" in node_ids
    edge_types = {e["type"] for e in network.json()["edges"]}
    assert "CALLED" in edge_types

    # 6. Analytics over the real graph.
    centrality = client.get("/api/v1/graph/analytics/centrality", headers=auth)
    assert centrality.status_code == 200
    ranked = centrality.json().get("items", [])
    assert any(r.get("entity_id") == "N-4821" for r in ranked)

    key = client.get("/api/v1/graph/analytics/key-entities", headers=auth)
    assert key.status_code == 200
    assert len(key.json().get("items", [])) >= 1