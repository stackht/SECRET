"""Investigation engine tests (original Phase 10)."""
import pytest

from app.graph.memory_store import MemoryGraphStore
from app.services.investigation_engine import InvestigationEngine


@pytest.mark.asyncio
async def test_engine_runs_full_workflow():
    store = MemoryGraphStore()
    engine = InvestigationEngine(store)
    summary = await engine.run(scenario="NORMAL_NETWORK")

    assert summary["records_ingested"] > 0
    assert summary["entities_extracted"] > 0
    assert summary["relationships_extracted"] > 0
    assert summary["graph"]["nodes"] > 0
    assert "communities" in summary["analytics"]
    assert len(store.nodes) > 0
    assert len(store.edges) > 0


@pytest.mark.asyncio
async def test_engine_anomaly_scenario_flags_bursts():
    store = MemoryGraphStore()
    engine = InvestigationEngine(store)
    summary = await engine.run(scenario="COMMUNICATION_ANOMALY")
    assert summary["analytics"]["communication_bursts"] > 0
