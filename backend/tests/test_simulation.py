"""Simulation (demo mode) tests (original Phase 15)."""
import pytest

from app.graph.memory_store import MemoryGraphStore
from app.services.simulation_service import SimulationService


@pytest.mark.asyncio
async def test_simulation_runs_full_pipeline():
    store = MemoryGraphStore()
    result = await SimulationService(store).run(scenario="NORMAL_NETWORK")

    assert len(result["steps"]) == 8
    assert result["entities"] > 0
    assert result["relationships"] > 0
    assert "insights" in result
    assert "elapsed_seconds" in result
    assert result["nodes_written"] > 0
    assert len(store.nodes) > 0


@pytest.mark.asyncio
async def test_simulation_detects_anomalies_in_comms_scenario():
    store = MemoryGraphStore()
    result = await SimulationService(store).run(scenario="COMMUNICATION_ANOMALY")
    assert result["scenario"] == "COMMUNICATION_ANOMALY"
    assert "anomalies" in result["insights"]
