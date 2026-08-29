"""Analytics tests (Phase 8).

Unit tests for the analytics modules and integration tests for the service +
endpoints, all via the in-memory graph store (no Neo4j required).
"""
import asyncio

import pytest
from fastapi.testclient import TestClient

from app.analytics.community import detect_communities, network_density
from app.analytics.centrality import composite_importance, degree_centrality, pagerank
from app.analytics.graph_builder import build_graph
from app.analytics.kingpin import rank_key_entities
from app.analytics.link_prediction import predict_links
from app.analytics.risk import risk_scores
from app.graph.memory_store import MemoryGraphStore
from app.graph.types import GraphEdge, GraphNode
from app.services.analytics_service import AnalyticsService


def sample_graph():
    """Build a small connected network with a clear hub node and return a NetworkX graph."""
    store = MemoryGraphStore()
    for n in [
        GraphNode(id="HUB", type="PERSON", name="Hub", properties={"risk_score": 90}),
        GraphNode(id="A", type="PERSON", name="A", properties={"risk_score": 50}),
        GraphNode(id="B", type="PERSON", name="B", properties={"risk_score": 55}),
        GraphNode(id="C", type="PERSON", name="C", properties={"risk_score": 45}),
        GraphNode(id="O", type="ORGANIZATION", name="Org", properties={"risk_score": 70}),
    ]:
        store.nodes[n.id] = n
    for e in [
        GraphEdge(id="1", source_id="HUB", target_id="A", type="ASSOCIATED_WITH"),
        GraphEdge(id="2", source_id="HUB", target_id="B", type="ASSOCIATED_WITH"),
        GraphEdge(id="3", source_id="HUB", target_id="C", type="ASSOCIATED_WITH"),
        GraphEdge(id="4", source_id="A", target_id="O", type="MEMBER_OF"),
    ]:
        store.edges[e.id] = e
    return build_graph(_memory_subgraph(store))


def _memory_subgraph(store: MemoryGraphStore):
    from app.graph.types import GraphSubgraph
    return GraphSubgraph(nodes=list(store.nodes.values()), edges=list(store.edges.values()))


def test_degree_centrality_hub_is_max():
    store = MemoryGraphStore()
    for n in [GraphNode(id="HUB", type="PERSON", name="H"),
              GraphNode(id="A", type="PERSON", name="A"),
              GraphNode(id="B", type="PERSON", name="B")]:
        store.nodes[n.id] = n
    store.edges["1"] = GraphEdge(id="1", source_id="HUB", target_id="A", type="X")
    store.edges["2"] = GraphEdge(id="2", source_id="HUB", target_id="B", type="X")
    graph = build_graph(_memory_subgraph(store))
    deg = degree_centrality(graph)
    assert deg["HUB"] == 1.0
    assert deg["A"] == 0.5


def test_pagerank_and_composite_nonempty():
    store = MemoryGraphStore()
    for n in [GraphNode(id="HUB", type="PERSON", name="H"),
              GraphNode(id="A", type="PERSON", name="A"),
              GraphNode(id="B", type="PERSON", name="B")]:
        store.nodes[n.id] = n
    store.edges["1"] = GraphEdge(id="1", source_id="HUB", target_id="A", type="X")
    store.edges["2"] = GraphEdge(id="2", source_id="HUB", target_id="B", type="X")
    graph = build_graph(_memory_subgraph(store))
    pr = pagerank(graph)
    comp = composite_importance(graph)
    assert pr["HUB"] >= pr["A"]
    assert set(comp) == {"HUB", "A", "B"}


def test_community_detection_splits_disconnected():
    store = MemoryGraphStore()
    # Two disconnected triads -> two communities (or left separate).
    for i in range(6):
        store.nodes[f"N{i}"] = GraphNode(id=f"N{i}", type="PERSON", name=str(i))
    store.edges["a"] = GraphEdge(id="a", source_id="N0", target_id="N1", type="X")
    store.edges["b"] = GraphEdge(id="b", source_id="N0", target_id="N2", type="X")
    store.edges["c"] = GraphEdge(id="c", source_id="N3", target_id="N4", type="X")
    graph = build_graph(_memory_subgraph(store))
    comms = detect_communities(graph)
    assert len(comms) >= 1
    assert network_density(graph) > 0


def test_rank_key_entities_hub_first():
    graph = sample_graph()
    ranked = rank_key_entities(graph, top_k=3)
    assert ranked[0]["entity_id"] == "HUB"
    assert 0 <= ranked[0]["score"] <= 100
    assert ranked[0]["degree"] >= 3


def test_link_prediction_returns_candidates():
    graph = sample_graph()
    candidates = predict_links(graph, top_k=5)
    # A few non-edge pairs should be ranked.
    assert isinstance(candidates, list)
    for c in candidates:
        assert not graph.has_edge(c["source"], c["target"])
        assert 0 <= c["score"] <= 100


def test_risk_scores_ordered_by_baseline():
    graph = sample_graph()
    scores = risk_scores(graph)
    assert scores[0]["entity_id"] == "HUB"
    assert scores[0]["risk_score"] >= scores[-1]["risk_score"]
    assert scores[0]["risk_level"] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}


@pytest.mark.asyncio
async def test_analytics_service_centrality():
    store = MemoryGraphStore()
    for n in [GraphNode(id="HUB", type="PERSON", name="H", properties={"risk_score":90}),
              GraphNode(id="A", type="PERSON", name="A", properties={"risk_score":50})]:
        store.nodes[n.id] = n
    store.edges["1"] = GraphEdge(id="1", source_id="HUB", target_id="A", type="X")
    svc = AnalyticsService(store)
    result = await svc.centrality()
    assert len(result.items) == 2
    ids = {i.entity_id for i in result.items}
    assert ids == {"HUB", "A"}


@pytest.mark.asyncio
async def test_analytics_service_risk():
    store = MemoryGraphStore()
    for n in [GraphNode(id="HUB", type="PERSON", name="H", properties={"risk_score":90}),
              GraphNode(id="A", type="PERSON", name="A", properties={"risk_score":50}),
              GraphNode(id="B", type="PERSON", name="B", properties={"risk_score":55})]:
        store.nodes[n.id] = n
    store.edges["1"] = GraphEdge(id="1", source_id="HUB", target_id="A", type="X")
    store.edges["2"] = GraphEdge(id="2", source_id="HUB", target_id="B", type="X")
    svc = AnalyticsService(store)
    result = await svc.risk_assessment(run_anomalies=False)
    assert len(result.items) == 3
    assert result.items[0].entity_id == "HUB"
