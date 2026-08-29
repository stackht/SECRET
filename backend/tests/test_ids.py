"""Tests for the typed entity-id helpers (Phase 2)."""
from app.utils.ids import (
    PREFIX_BY_TYPE,
    build_secret_id,
    parse_secret_id,
)


def test_build_secret_id_person():
    assert build_secret_id("PERSON", 421) == "P-0421"


def test_build_secret_id_vehicle():
    assert build_secret_id("VEHICLE", 2048) == "V-2048"


def test_build_secret_id_default_width():
    assert build_secret_id("ORGANIZATION", 3) == "O-0003"


def test_parse_secret_id():
    prefix, seq = parse_secret_id("P-0421")
    assert (prefix, seq) == ("P", 421)


def test_all_entity_types_have_prefixes():
    for entity_type in ["PERSON", "ORGANIZATION", "PHONE", "VEHICLE", "LOCATION", "ACCOUNT"]:
        assert entity_type in PREFIX_BY_TYPE
