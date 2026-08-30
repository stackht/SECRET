"""Source registry + ingestion tests (Phase 2-3)."""
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
        "/api/v1/cases", json={"title": "Source Test Case", "priority": "HIGH"}, headers=auth
    )
    assert case.status_code == 201, case.text
    return {"auth": auth, "client": db_client, "case_number": case.json()["case_number"]}


def test_register_and_list_source(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]
    data = {
        "source_id": "CDR-AUGUST",
        "filename": "cdr_august.csv",
        "file_type": "CSV",
        "source_type": "CDR",
        "record_count": 42182,
        "payload": {
            "records": [
                {"id": "1", "timestamp": "2026-08-14T09:12", "text": "call",
                 "fields": {"caller_phone": "N-4821", "receiver_phone": "N-9044"}},
            ]
        },
    }
    r = client.post(f"/api/v1/cases/{case_number}/sources", json=data, headers=auth)
    assert r.status_code == 201, r.text
    assert r.json()["source_id"] == "CDR-AUGUST"
    assert r.json()["status"] == "UPLOADED"
    lst = client.get(f"/api/v1/cases/{case_number}/sources", headers=auth)
    assert lst.status_code == 200
    assert any(s["source_id"] == "CDR-AUGUST" for s in lst.json())


def test_duplicate_source_rejected(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]
    data = {"source_id": "FIR-001", "filename": "fir.txt", "source_type": "FIR"}
    assert client.post(f"/api/v1/cases/{case_number}/sources", json=data, headers=auth).status_code == 201
    assert client.post(f"/api/v1/cases/{case_number}/sources", json=data, headers=auth).status_code == 409


def test_process_source(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]
    data = {
        "source_id": "CDR-001",
        "filename": "cdr.csv",
        "file_type": "CSV",
        "source_type": "CDR",
        "payload": {
            "records": [
                {"id": "1", "timestamp": "2026-08-14T09:12", "text": "call",
                 "fields": {"caller_phone": "N-4821", "receiver_phone": "N-9044"}},
                {"id": "2", "timestamp": "2026-08-14T10:00", "text": "call",
                 "fields": {"caller_phone": "N-9044", "receiver_phone": "N-7712"}},
            ]
        },
    }
    created = client.post(f"/api/v1/cases/{case_number}/sources", json=data, headers=auth)
    assert created.status_code == 201
    processed = client.post(f"/api/v1/cases/{case_number}/sources/CDR-001/process", headers=auth)
    assert processed.status_code == 200, processed.text
    body = processed.json()
    assert body["status"] == "PROCESSED"
    assert body["record_count"] == 2
    assert body["metrics"]["entities_extracted"] >= 1


def test_delete_source(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]
    data = {"source_id": "VEH-001", "filename": "vehicles.json", "source_type": "VEHICLE"}
    assert client.post(f"/api/v1/cases/{case_number}/sources", json=data, headers=auth).status_code == 201
    assert client.delete(f"/api/v1/cases/{case_number}/sources/VEH-001", headers=auth).status_code == 204


def test_sources_require_auth(ctx) -> None:
    case_number = ctx["case_number"]
    assert ctx["client"].get(f"/api/v1/cases/{case_number}/sources").status_code == 401


def test_upload_cdr_csv(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]
    csv_bytes = (
        b"caller,receiver,time,duration\n"
        b"N-4821,N-9044,2026-08-14T09:12,34\n"
        b"N-9044,N-7712,2026-08-14T10:00,12\n"
    )
    resp = client.post(
        f"/api/v1/cases/{case_number}/sources/upload",
        headers=auth,
        files={"file": ("cdr_august.csv", csv_bytes, "text/csv")},
        data={"source_type": "CDR"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["source_id"] == "CDR-AUGUST"
    assert body["format"] == "CSV"
    assert body["status"] == "READY"
    assert body["record_count"] == 2
    assert body["quality"]["valid"] == 2
    assert body["error"] is None

    # Listing shows the uploaded source.
    lst = client.get(f"/api/v1/cases/{case_number}/sources", headers=auth)
    assert any(s["source_id"] == "CDR-AUGUST" for s in lst.json())


def test_upload_process_persists_and_is_idempotent(ctx) -> None:
    """Upload -> process persists extracted entities/relationships; re-process does not duplicate."""
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]
    csv_bytes = (
        b"caller,receiver,time\n"
        b"N-4821,N-9044,2026-08-14T09:12\n"
        b"N-9044,N-7712,2026-08-14T10:00\n"
    )
    up = client.post(
        f"/api/v1/cases/{case_number}/sources/upload",
        headers=auth,
        files={"file": ("cdr.csv", csv_bytes, "text/csv")},
        data={"source_type": "CDR"},
    )
    assert up.status_code == 201
    sid = up.json()["source_id"]
    first = client.post(f"/api/v1/cases/{case_number}/sources/{sid}/process", headers=auth)
    assert first.status_code == 200, first.text
    body = first.json()
    assert body["status"] == "PROCESSED"
    assert body["record_count"] == 2
    assert body["metrics"]["entities_persisted"] > 0
    assert body["metrics"]["relationships_persisted"] >= 1

    # Reprocessing the same source must not grow the persisted set.
    second = client.post(f"/api/v1/cases/{case_number}/sources/{sid}/process", headers=auth)
    assert second.status_code == 200
    assert second.json()["metrics"]["entities_persisted"] == body["metrics"]["entities_persisted"]
    assert second.json()["metrics"]["relationships_persisted"] == body["metrics"]["relationships_persisted"]


def test_upload_duplicate_hash_rejected(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]
    csv_bytes = b"caller,receiver,time\nN-1,N-2,2026-08-01T00:00\n"
    files = {"file": ("a.csv", csv_bytes, "text/csv")}
    data = {"source_type": "CDR"}
    first = client.post(f"/api/v1/cases/{case_number}/sources/upload", headers=auth, files=files, data=data)
    assert first.status_code == 201
    dup = client.post(
        f"/api/v1/cases/{case_number}/sources/upload",
        headers=auth,
        files={"file": ("renamed.csv", csv_bytes, "text/csv")},
        data={"source_type": "CDR"},
    )
    assert dup.status_code == 409


def test_upload_unsupported_pdf_records_error(ctx) -> None:
    client = ctx["client"]
    auth = ctx["auth"]
    case_number = ctx["case_number"]
    resp = client.post(
        f"/api/v1/cases/{case_number}/sources/upload",
        headers=auth,
        files={"file": ("fir.pdf", b"%PDF-1.4 fake", "application/pdf")},
        data={"source_type": "FIR"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "ERROR"
    assert body["error"] is not None


def test_upload_requires_auth(ctx) -> None:
    case_number = ctx["case_number"]
    resp = ctx["client"].post(
        f"/api/v1/cases/{case_number}/sources/upload",
        files={"file": ("x.csv", b"a,b\n1,2\n", "text/csv")},
        data={"source_type": "CDR"},
    )
    assert resp.status_code == 401