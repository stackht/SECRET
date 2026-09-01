"""What-if investigation simulator (Phase 13).

Mutates an ISOLATED copy of the network (never the original) and reports
structural impact: before/after nodes, edges, communities, connectivity,
bridge dependence, and affected communities. Remaining analytical — never
judgmental about criminality.
"""
from __future__ import annotations

import networkx as nx

from app.analytics.centrality import betweenness_centrality
from app.analytics.community import detect_communities, connected_components
from app.intelligence.dna import _bridge_dependence
from app.intelligence.models import SimulationResult


def _snapshot(graph: nx.Graph) -> dict:
    comms = detect_communities(graph)
    components = connected_components(graph)
    _, bridge_ratio = _bridge_dependence(graph)
    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "communities": len(comms),
        "component_count": len(components),
        "bridge_ratio": bridge_ratio,
    }


def _connectivity(graph: nx.Graph) -> float:
    """Largest connected component share of nodes (0..1)."""
    if graph.number_of_nodes() == 0:
        return 0.0
    components = connected_components(graph)
    largest = max((len(c) for c in components), default=0)
    return largest / graph.number_of_nodes()


def _to_graph(data_nodes, data_edges) -> nx.Graph:
    graph = nx.Graph()
    for node in data_nodes:
        graph.add_node(node["id"], **node.get("properties", {}))
    for edge in data_edges:
        src, tgt, rtype = edge["source"], edge["target"], edge.get("type", "ASSOCIATED_WITH")
        graph.add_edge(src, tgt, type=rtype)
    return graph


def simulate(
    graph: nx.Graph,
    operation: str,          # remove_entity | remove_relationship | add_relationship | confirm_potential | hide_entity
    subject: str,            # entity id or "source<->target"
    data_nodes=None,
    data_edges=None,
) -> SimulationResult:
    """Run a what-if operation on an isolated copy and report impact."""
    if data_nodes is not None and data_edges is not None:
        working = _to_graph(data_nodes, data_edges)
    else:
        working = graph.copy()

    before = _snapshot(working)
    conn_before = _connectivity(working)

    params = subject.split("<->")
    if len(params) == 2:
        a, b = params[0], params[1]
    else:
        a = b = subject

    affected: set[str] = set()
    if operation in ("remove_entity", "hide_entity"):
        if working.has_node(a):
            for n in list(working.neighbors(a)):
                affected.add(n)
            working.remove_node(a)
    elif operation in ("remove_relationship",):
        if working.has_edge(a, b):
            working.remove_edge(a, b)
            affected = {a, b}
    elif operation in ("add_relationship", "confirm_potential"):
        if not working.has_edge(a, b):
            working.add_edge(a, b, type=("CONFIRMED" if operation == "confirm_potential" else "POTENTIAL"))
        affected = {a, b}

    after = _snapshot(working)
    conn_after = _connectivity(working)
    conn_change = round((conn_after - conn_before) * 100.0, 1)

    affected_communities = after["communities"] - before["communities"]

    # Bridge dependence before/after.
    bridge_before = _level_of(before["bridge_ratio"])
    bridge_after = _level_of(after["bridge_ratio"])

    interpretation = _interpret(operation, a, conn_change, bridge_before, bridge_after,
                                after["nodes"], before["nodes"])

    return SimulationResult(
        operation=operation,
        subject=subject,
        before_nodes=before["nodes"],
        after_nodes=after["nodes"],
        before_edges=before["edges"],
        after_edges=after["edges"],
        before_communities=before["communities"],
        after_communities=after["communities"],
        connectivity_change=conn_change,
        bridge_before=bridge_before,
        bridge_after=bridge_after,
        affected_communities=max(0, abs(affected_communities)),
        interpretation=interpretation,
        explanation=_explanation(operation, a, b, affected_communities, conn_change),
    )


def _level_of(ratio: float) -> str:
    return "HIGH" if ratio >= 0.3 else "MEDIUM" if ratio >= 0.15 else "LOW"


def _interpret(op: str, subject: str, conn_change: float, bb: str, ba: str, after_n: int, before_n: int) -> str:
    if op in ("remove_entity", "hide_entity"):
        if conn_change < -10:
            return f"{subject} has high structural importance; removing it lowers connectivity by {abs(conn_change):.0f}%."
        return f"{subject} removal has limited effect on overall connectivity (Δ{conn_change:+.0f}%)."
    if op in ("add_relationship", "confirm_potential"):
        if conn_change > 0:
            return f"Adding {subject} increases network cohesion (connectivity Δ{conn_change:+.0f}%)."
        return f"Adding {subject} does not materially change connectivity."
    return f"Removing relationship {subject} changes connectivity by {conn_change:+.0f}%."


def _explanation(op: str, a: str, b: str, affected: int, conn_change: float) -> str:
    verb = {
        "remove_entity": f"removing entity {a}",
        "hide_entity": f"hiding entity {a}",
        "remove_relationship": f"removing relationship {a}-{b}",
        "add_relationship": f"adding potential relationship {a}-{b}",
        "confirm_potential": f"confirming potential relationship {a}-{b}",
    }.get(op, op)
    return f"Simulated {verb}; connectivity changed {conn_change:+.0f}% and {affected} " \
           f"community membership(s) were affected. Analytical impact only."