"""Intelligence engine tests (Phase 19).

Pulls the coherent demo CaseData and runs each engine, verifying the results
are computed (explainable, non-hardcoded) — evidence fusion, temporal,
anomaly, potential links, gaps, DNA, priority, info-gain, actions, simulation.
"""
from app.intelligence import (actions, anomaly, dna, fusion, gaps, info_gain,
                              potential_links, priority, simulate, temporal)
from app.intelligence.models import RelData
from app.intelligence.offline import build_demo_case, location_observations


def _graph():
    import networkx as nx
    data = build_demo_case()
    g = nx.Graph()
    for e in data.entities:
        g.add_node(e.id, type=e.type)
    for r in data.relationships:
        g.add_edge(r.source, r.target, type=r.rel_type)
    return g


def test_evidence_fusion_relationship() -> None:
    data = build_demo_case()
    rel = next(r for r in data.relationships if r.source == "P-0421" and r.target == "V-2048")
    res = fusion.fuse_relationship(data, rel)
    assert res.level in ("HIGH", "MEDIUM", "LOW")
    assert res.score >= 0.0
    assert res.independent_source_count >= 0
    assert res.explanation  # explainable


def test_temporal_evolution_detects_changes() -> None:
    data = build_demo_case()
    boundary = temporal.default_boundary(data)
    changes = temporal.network_evolution(data, boundary)
    # P-0312->O-1101 member_of new after boundary + N-9044->L-3007
    assert any(c.kind == "NEW_REL" for c in changes)


def test_anomaly_detection() -> None:
    data = build_demo_case()
    ans = anomaly.detect_all(data, location_observations())
    comm = [a for a in ans if a.kind == "COMM_BURST"]
    tx = [a for a in ans if a.kind == "TX_AMOUNT"]
    assert any(a.deviation > 0 for a in comm + tx)
    for a in ans:
        assert a.baseline is not None and a.explanation


def test_potential_link_marquee() -> None:
    data = build_demo_case()
    links = potential_links.discover(data)
    assert any({"P-0421", "P-0312"} == {l.source, l.target} and l.score > 20 for l in links)


def test_evidence_gaps() -> None:
    data = build_demo_case()
    gaps_ = gaps.gaps_for_potential_links(data, potential_links.discover(data))
    assert len(gaps_) > 0
    assert all(g.recommended_source for g in gaps_)


def test_network_dna_and_compare() -> None:
    data = build_demo_case()
    g = _graph()
    antes = dna.compute_dna(g, data)
    asserts = dna.compute_dna(g, data)
    assert antes.community_count >= 1
    assert antes.bridge_dependence in ("HIGH", "MEDIUM", "LOW")
    diff = dna.compare_dna(antes, asserts)
    assert "density" in diff


def test_priority_ranks_entities() -> None:
    import networkx as nx
    from app.analytics import centrality as cent
    from app.analytics import community as comm
    data = build_demo_case()
    g = _graph()
    deg = cent.degree_centrality(g)
    betw = cent.betweenness_centrality(g)
    comms = comm.detect_communities(g)
    scored = priority.rank_entities(data, deg, betw, comms, {}, {}, {e.id: 1 for e in data.entities})
    assert scored[0].priority > 0
    assert scored[0].explanation  # explainable factors


def test_info_gain() -> None:
    data = build_demo_case()
    g = _graph()
    gain = info_gain.entity_gain(data, "P-0421", uncertainty=60.0, affected=len(data.neighbors("P-0421")))
    assert gain.score >= 0.0
    assert gain.explanation


def test_next_best_actions() -> None:
    import networkx as nx
    from app.analytics import centrality as cent
    from app.analytics import community as comm
    data = build_demo_case()
    g = _graph()
    links = potential_links.discover(data)
    gaps_ = gaps.gaps_for_potential_links(data, links)
    entity_gains = {e.id: info_gain.entity_gain(data, e.id, 50.0, len(data.neighbors(e.id))) for e in data.entities}
    link_gains = {f"{l.source}<->{l.target}": info_gain.potential_link_gain(data, l) for l in links}
    recs = actions.build(data, [], entity_gains, links, [], link_gains, gaps_, top_k=6)
    assert len(recs) >= 1
    for r in recs:
        assert r.recommended_data  # each action says what data to review


def test_what_if_simulation() -> None:
    g = _graph()
    res = simulate.simulate(g, "remove_entity", "P-0421")
    assert res.after_nodes == res.before_nodes - 1
    assert res.connectivity_change <= 0  # removing a hub should not raise connectivity
    assert res.interpretation


def test_offline_case_data() -> None:
    data = build_demo_case()
    assert len(data.entities) >= 10
    assert len(data.relationships) >= 8
    assert len(data.evidence) >= 4
    # Same canonical identifiers across sources (coherent data).
    assert any(e.id == "P-0421" for e in data.entities)
    assert any(e.source_id == "CDR-001" for e in data.evidence)