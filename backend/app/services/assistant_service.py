"""AI assistant - local dataset analyst (original Phase 11).

Answers only questions the SECRET dataset can support, always attaching the
supporting source record ids. Never fabricates evidence; returns an explicit
"No supporting evidence" answer when the dataset has nothing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from app.analytics.graph_builder import build_graph
from app.graph.types import GraphNode


@dataclass
class AssistantAnswer:
    question: str
    answer: str
    source_ids: list[str]
    found: bool


class LocalDatasetAssistant:
    """Rule-based, evidence-grounded question answering over the graph store."""

    def __init__(self, store) -> None:
        self._store = store

    def _entity_by_id(self, nodes: list[GraphNode], entity_id: str) -> GraphNode | None:
        return next((n for n in nodes if n.id.lower() == entity_id.lower()), None)

    async def answer(self, question: str) -> AssistantAnswer:
        q = question.lower()
        qclean = re.sub(r"[^a-z0-9 \-_]", " ", q)

        # Identify referenced entity id if present (e.g. P-0421).
        m = re.search(r"([povnal]\-\d{3,})", q)
        entity_id = m.group(1).upper() if m else None

        network = await self._store.build_network(limit=2000)
        graph = build_graph(network)
        nodes = network.nodes

        if entity_id is None:
            return AssistantAnswer(
                question=question,
                answer=(
                    "I can only answer about entities present in the current dataset. "
                    "Try asking, for example, 'Show connections of P-0421'."
                ),
                source_ids=[],
                found=False,
            )

        node = self._entity_by_id(nodes, entity_id)
        if node is None:
            return AssistantAnswer(
                question=question,
                answer=f"No supporting evidence found in the current dataset for {entity_id}.",
                source_ids=[],
                found=False,
            )

        # "connections / relationships" intent.
        if "connection" in qclean or "relationship" in qclean or "neighbor" in qclean:
            neighbors = list(graph.neighbors(node.id))
            if not neighbors:
                return AssistantAnswer(
                    question=question,
                    answer=f"{entity_id} has no mapped connections in the current dataset.",
                    source_ids=[], found=False,
                )
            return AssistantAnswer(
                question=question,
                answer=f"{entity_id} ({node.name}) is connected to: {', '.join(sorted(neighbors))}.",
                source_ids=[f"GRAPH-{node.id}"],
                found=True,
            )

        # "which entities / events" generic profile question.
        types = {n.type for n in nodes}
        return AssistantAnswer(
            question=question,
            answer=(
                f"{entity_id} is a '{node.type}' entity named '{node.name}'. "
                f"Dataset contains {len(nodes)} entities and {len(network.edges)} relationships. "
                f"Ask for its 'connections' to list neighbors."
            ),
            source_ids=[f"GRAPH-{node.id}"],
            found=True,
        )
