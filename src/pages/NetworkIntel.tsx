import { HudPage } from "../components/HudPage";
import { HudCard, HoloList } from "../components/HudPrimitives";

export function NetworkIntel() {
  return (
    <HudPage title="NETWORK INTELLIGENCE" subtitle="High-density relationship analysis" rightMeta={<><div>GRAPH ONLINE</div><div>7 ACTIVE CLUSTERS</div></>}>
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
            <div className="glass-strip">42 clusters mapped</div>
            <div className="glass-strip">16 active paths</div>
          </div>
        </HudCard>

        <div className="hud-network-side">
          <HudCard label="Entity details" title="Key Influencers">
            <HoloList items={[{ label: "Entity A", value: "94.8" }, { label: "Entity B", value: "89.2" }, { label: "Entity C", value: "81.7" }, { label: "Entity D", value: "76.2" }]} />
          </HudCard>
          <HudCard label="Pulse map" title="Hot nodes">
            <div className="mini-list">
              <div className="entity entity-tight"><div><div>North Cluster</div><div className="meta">18 links · 92 confidence</div></div><div className="risk">92</div></div>
              <div className="entity entity-tight"><div><div>Delta Relay</div><div className="meta">12 links · 84 confidence</div></div><div className="risk">84</div></div>
              <div className="entity entity-tight"><div><div>Sector 17</div><div className="meta">24 links · 97 confidence</div></div><div className="risk">97</div></div>
            </div>
          </HudCard>
        </div>
      </div>
    </HudPage>
  );
}
