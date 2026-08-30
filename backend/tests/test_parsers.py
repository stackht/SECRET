"""Parser + schema detection + quality metrics tests (Phase 1)."""
from app.ingestion.parsers import parse_source, detect_format


def test_csv_cdr_parsed_and_mapped() -> None:
    csv_bytes = (
        "caller,receiver,time,duration\n"
        "N-4821,N-9044,2026-08-14T09:12,34\n"
        "N-9044,N-7712,2026-08-14T10:00,12\n"
    ).encode()
    out = parse_source("cdr_august.csv", csv_bytes, "CDR")
    assert out.format == "CSV"
    assert out.error is None
    assert len(out.records) == 2
    assert out.records[0]["fields"]["caller_phone"] == "N-4821"
    assert out.records[0]["fields"]["receiver_phone"] == "N-9044"
    assert out.records[0]["timestamp"] == "2026-08-14T09:12"
    assert out.quality["total"] == 2
    assert out.quality["valid"] == 2
    assert out.quality["quality_score"] == 100


def test_csv_alias_headers_detected() -> None:
    csv_bytes = (
        "From,To,Date,Amt\n"
        "A-100,A-200,2026-08-01,50000\n"
        "A-200,A-100,2026-08-02,25000\n"
    ).encode()
    out = parse_source("txn.csv", csv_bytes, "TRANSACTION")
    assert out.records[0]["fields"]["sender"] == "A-100"
    assert out.records[0]["fields"]["receiver"] == "A-200"
    assert out.records[0]["fields"]["amount"] == "50000"


def test_csv_duplicate_and_invalid_quality() -> None:
    rows = (
        "caller,receiver,time\n"
        "N-1,N-2,2026-08-01T00:00\n"
        "N-1,N-2,2026-08-01T00:00\n"
        "N-3,,2026-08-01T00:00\n"
        "\n"
    )
    out = parse_source("dup.csv", rows.encode(), "CDR")
    assert out.error is None
    assert out.quality["total"] == 3
    assert out.quality["valid"] == 1        # first of the duplicated pair
    assert out.quality["duplicates"] == 1
    assert out.quality["invalid"] == 1     # N-3 missing receiver
    assert out.quality["quality_score"] == 33
    assert out.quality["invalid_samples"][0]["missing"] == ["receiver_phone"]


def test_csv_malformed_line_short_column() -> None:
    csv_bytes = (
        "caller,receiver,time\n"
        "N-1,N-2,2026-08-01T00:00\n"
        "onemissingfield\n"
    ).encode()
    out = parse_source("bad.csv", csv_bytes, "CDR")
    assert out.quality["malformed"] == 1
    assert out.records[0]["fields"]["caller_phone"] == "N-1"


def test_json_records_parsed() -> None:
    payload = {
        "records": [
            {"sender": "A-1", "receiver": "A-2", "amount": 100, "timestamp": "2026-08-01T00:00"},
            {"sender": "A-2", "receiver": "A-1", "amount": 50, "timestamp": "2026-08-01T01:00"},
        ]
    }
    out = parse_source("txn.json", __import__("json").dumps(payload).encode(), "TRANSACTION")
    assert out.format == "JSON"
    assert len(out.records) == 2
    assert out.records[0]["fields"]["sender"] == "A-1"


def test_json_single_text_document() -> None:
    payload = {"id": "INT-1", "text": "Subject X was observed meeting Y at Market Road."}
    out = parse_source("report.json", __import__("json").dumps(payload).encode(), "INTELLIGENCE")
    assert out.format == "JSON"
    assert len(out.records) == 1
    assert "meeting" in out.records[0]["text"]


def test_txt_extracted_as_text_record() -> None:
    out = parse_source("fir.txt", b"Complainant reported an incident near Sector 17.", "FIR")
    assert out.format == "TEXT"
    assert len(out.records) == 1
    assert out.records[0]["source_type"] == "FIR"
    assert "incident" in out.records[0]["text"]


def test_vehicle_schema_mapping() -> None:
    csv_bytes = "registration_no,owner_name\nVX-2048,A-0421\n".encode()
    out = parse_source("vehicles.csv", csv_bytes, "VEHICLE")
    assert out.records[0]["fields"]["vehicle"] == "VX-2048"
    assert out.records[0]["fields"]["owner"] == "A-0421"


def test_unsupported_pdf_clear_error() -> None:
    assert detect_format("a.pdf", b"%PDF-1.4")[0] == "PDF"
    out = parse_source("fir.pdf", b"%PDF-1.4 fake", "FIR")
    assert out.format == "PDF"
    assert out.error is not None
    assert "OCR" in out.error


def test_unsupported_docx_clear_error() -> None:
    out = parse_source("report.docx", b"PK\x03\x04 fake", "INTELLIGENCE")
    assert out.format == "DOCX"
    assert out.error is not None


def test_empty_and_oversized_csv() -> None:
    assert parse_source("empty.csv", b"", "CDR").error == "Empty file"
    big = b"caller,receiver,time\n" + b"N-1,N-2,2026-08-01T00:00\n" * 200_001
    out = parse_source("huge.csv", big, "CDR")
    assert "Too many rows" in out.error


def test_location_schema_mapping() -> None:
    csv_bytes = (
        "entity,lat,lon,area,time\n"
        "P-0421,19.07,72.87,Kandivali,2026-08-14T11:00\n"
    ).encode()
    out = parse_source("locations.csv", csv_bytes, "LOCATION")
    assert out.records[0]["fields"]["location"] == "Kandivali"
    assert out.records[0]["fields"]["entity"] == "P-0421"