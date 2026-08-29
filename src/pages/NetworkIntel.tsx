import { useMemo } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard, HoloList } from "../components/HudPrimitives";
import { useBackendStore } from "../store/backend";

/**
 * Network Intelligence (Phase 7).
 *
 * Visually unchanged. The Key Influencers / Hot nodes lists are now derived from
 * the live knowledge-graph (or the synthetic fallback) instead of hard-coded
 * values, so the screen reflects real application state.
 */
export function NetworkIntel() {
  const graph = useBackendStore((s) => s.graph);
  const mode = useBackendStore((s) => s.mode);

  // Rank nodes by risk to approximate influencer importance.
  const influencers = useMemo(() => {
    const scored = graph.nodes.map((node) => ({
      node,
      risk: (node.properties.risk as number) ?? (node.properties.risk_score as number) ?? 0,
    }));
    scored.sort((a, b) => b.risk - a.risk);
    return scored.slice(0, 4);
  }, [graph]);

  // Hot nodes: entities with the most connections.
  const hot = useMemo(() => {
    const degree: Record<string, number> = {};
    for (const edge of graph.edges) {
      degree[edge.source] = (degree[edge.source] ?? 0) + 1;
      degree[edge.target] = (degree[edge.target] ?? 0) + 1;
    }
    const byId = new Map(graph.nodes.map((n) => [n.id, n]));
    const ranked = graph.nodes
      .map((node) => ({ node, degree: degree[node.id] ?? 0 }))
      .filter((x) => x.degree > 0)
      .sort((a, b) => b.degree - a.degree)
      .slice(0, 4);
    return ranked;
  }, [graph]);

  const online = mode === "backend";

  return (
    <HudPage
      title="NETWORK INTELLIGENCE"
      subtitle="High-density relationship analysis"
      rightMeta={
        <>
          <div>{online ? "GRAPH ONLINE" : "SYNTHETIC MODE"}</div>
          <div>{graph.nodes.length} NODES · {graph.edges.length} LINKS</div>
        </>
      }
    >
      <div className="hud-network-layout">
        <HudCard label="Filters" title="Signal Controls" className="hud-network-controls">
          <div className="filters hud-filters">
            <button className="pill">ENTITY TYPE</button>
            <button className="pill">RELATIONSHIP TYPE</button>
            <button className="pill">TIME RANGE</button>
            <button className="pill">RISK LEVEL</button>
            <button className="pill">CONFIDENCE</button>
          </div>
          <div className="hud-network-mini">
            <div className="hud-network-orbit" />
            <div className="hud-network-axis">
              <span>Clustering</span>
              <span>Propagation</span>
              <span>Stability</span>
            </div>
          </div>
        </HudCard>

        <HudCard label="Graph surface" title="Network Mesh" className="hud-network-mesh">
          <div className="hud-surface-grid hud-surface-grid-nodes" />
          <div className="hud-network-overlay">
            <div className="glass-strip">{graph.nodes.length} clusters mapped</div>
            <div className="glass-strip">{graph.edges.length} active paths</div>
          </div>
        </HudCard>

        <div className="hud-network-side">
          <HudCard label="Entity details" title="Key Influencers">
            <HoloList
              items={influencers.map((entry, i) => ({
                label: `${String(i + 1).padStart(2, "0")}  ${entry.node.name}`,
                value: entry.risk.toFixed(1),
              }))}
            />
          </HudCard>
          <HudCard label="Pulse map" title="Hot nodes">
            <div className="mini-list">
              {hot.map((entry) => (
                <div key={entry.node.id} className="entity entity-tight">
                  <div>
                    <div>{entry.node.name}</div>
                    <div className="meta">{entry.node.type} · {entry.degree} links</div>
                  </div>
                  <div className="risk">{entry.degree}</div>
                </div>
              ))}
            </div>
          </HudCard>
        </div>
      </div>
    </HudPage>
  );
}
