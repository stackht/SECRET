"""Entity resolution tests (original Phase 5)."""
from app.ingestion.extraction import EntityMention
from app.ingestion.resolution import confirm, normalize_name, resolve, similarity


def test_normalize_name():
    assert normalize_name("  Rahul K. Kumar  ") == "rahul k kumar"
    assert normalize_name("Alpha") == "alpha"
    assert normalize_name("") == ""


def test_similarity_exact_and_partial():
    assert similarity("Alpha", "alpha") == 1.0
    assert similarity("Rahul Kumar", "Rahul K") >= 0.5
    assert similarity("Person A", "Organization Orion") == 0.0


def test_resolve_proposes_merge_on_alias_overlap():
    known = {
        "P-0421": ["Person A", "Alpha", "A. Khan"],
        "P-1000": ["Person B"],
    }
    mentions = [
        EntityMention(entity_id="P-0555", entity_type="PERSON", name="A. Khan", confidence=0.9)
    ]
    conflicts = resolve(known, mentions)
    assert len(conflicts) >= 1
    cand = conflicts[0].candidate
    assert cand.existing_id == "P-0421"
    assert cand.candidate_id == "P-0555"
    assert cand.confidence >= 60.0
    assert any("overlap" in e for e in cand.evidence)


def test_resolve_no_false_positive():
    known = {"P-0421": ["Person A", "Alpha"]}
    mentions = [EntityMention(entity_id="P-2000", entity_type="PERSON", name="Unrelated", confidence=0.9)]
    assert resolve(known, mentions) == []


def test_confirm_flow():
    known = {"P-0421": ["Person A"]}
    mentions = [EntityMention(entity_id="P-0555", entity_type="PERSON", name="Person A", confidence=0.9)]
    conflict = resolve(known, mentions)[0]
    assert conflict.status == "pending"
    confirmed = confirm(conflict, True)
    assert confirmed.status == "confirmed"
    assert confirm(conflict, False).status == "rejected"
