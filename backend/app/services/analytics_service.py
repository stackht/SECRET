"""Analytics service (Phase 8).

Loads knowledge-graph data from a `GraphStore` into NetworkX and orchestrates
the analytics modules, returning typed response schemas.
"""
from __future__ import annotations

from app.analytics import centrality, community, kingpin, link_prediction, risk
from app.analytics.graph_builder import build_graph
from app.schemas.analytics import (
    CentralityResponse,
    CentralityResult,
    CommunityResponse,
    CommunityResult,
    KeyEntitiesResponse,
    KeyEntityResult,
    LinkPredictionResponse,
    LinkPredictionResult,
    RiskResponse,
    RiskResult,
)


class AnalyticsService:
    """Co-ordinates graph-analytics computations against a graph store."""

    def __init__(self, store) -> None:
        self._store = store

    async def _graph(self):
        network = await self._store.build_network(limit=2000)
        return build_graph(network)

    async def centrality(self) -> CentralityResponse:
        graph = await self._graph()
        deg = centrality.degree_centrality(graph)
        betw = centrality.betweenness_centrality(graph)
        close = centrality.closeness_centrality(graph)
        pr = centrality.pagerank(graph)
        keys = sorted(deg, key=lambda n: pr.get(n, 0.0), reverse=True)
        items = [
            CentralityResult(
                entity_id=n,
                degree=round(deg[n] * 100.0, 1),
                betweenness=round(betw.get(n, 0.0) * 100.0, 1),
                closeness=round(close.get(n, 0.0) * 100.0, 1),
                pagerank=round(pr.get(n, 0.0) * 100.0, 1),
            )
            for n in keys
        ]
        return CentralityResponse(items=items)

    async def communities(self) -> CommunityResponse:
        graph = await self._graph()
        comms = community.detect_communities(graph)
        results = [
            CommunityResult(community_id=i, size=len(c), entities=c)
            for i, c in enumerate(comms)
        ]
        return CommunityResponse(
            communities=results,
            count=len(results),
            network_density=round(community.network_density(graph), 4),
        )

    async def key_entities(self, top_k: int = 10) -> KeyEntitiesResponse:
        graph = await self._graph()
        ranked = kingpin.rank_key_entities(graph, top_k=top_k)
        items = [KeyEntityResult(**r) for r in ranked]
        return KeyEntitiesResponse(items=items)

    async def link_prediction(self, top_k: int = 20) -> LinkPredictionResponse:
        graph = await self._graph()
        candidates = link_prediction.predict_links(graph, top_k=top_k)
        items = [LinkPredictionResult(**c) for c in candidates]
        return LinkPredictionResponse(candidates=items)

    async def risk_assessment(self, run_anomalies: bool = True) -> RiskResponse:
        graph = await self._graph()
        scores = risk.risk_scores(graph)
        items = [RiskResult(**r) for r in scores]
        anomalies = (
            risk.isolation_forest_anomalies(graph) if run_anomalies else []
        )
        return RiskResponse(items=items, anomalies=anomalies)
