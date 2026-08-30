import { useEffect, useMemo, useState } from "react";
import { dashboardMetrics, feed, entities, alerts } from "../data/mock";
import { Activity, BarChart3, Radar, Shield, Users, Globe, Layers3, ChevronRight, Play, Pin, ArrowUpRight, Waves } from "lucide-react";
import { HoloList, HudCard, StatRow } from "../components/HudPrimitives";
import { GlobeScene } from "../components/GlobeScene";
import { useBackendStore } from "../store/backend";
import { apiDashboardSummary, type DashboardSummary } from "../services/api";

const activity = [22, 34, 31, 46, 58, 49, 63, 77, 69, 84, 91, 88];
const entityMix = [
  { label: "People", value: 42 },
  { label: "Organizations", value: 24 },
  { label: "Vehicles", value: 12 },
  { label: "Phones", value: 9 },
  { label: "Locations", value: 8 },
  { label: "Accounts", value: 5 }
];

function Sparkline() {
  const d = useMemo(() => activity.map((v, i) => `${i === 0 ? "M" : "L"} ${i * 10} ${100 - v}`).join(" "), []);
  return (
    <svg viewBox="0 0 110 110" className="sparkline">
      <path d={d} />
      <path d={d} className="sparkline-fill" />
    </svg>
  );
}

function Donut() {
  return (
    <svg viewBox="0 0 120 120" className="donut">
      <circle cx="60" cy="60" r="42" />
      <circle cx="60" cy="60" r="42" className="donut-ring" />
      <circle cx="60" cy="60" r="42" className="donut-ring active" />
    </svg>
  );
}

export function CommandCenter() {
  const [tick, setTick] = useState(0);
  const backend = useBackendStore((s) => s.mode);
  const graph = useBackendStore((s) => s.graph);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  useEffect(() => { const t = setInterval(() => setTick((v) => v + 1), 2500); return () => clearInterval(t); }, []);
  useEffect(() => {
    if (backend !== "backend") return;
    apiDashboardSummary().then(setSummary).catch(() => {});
  }, [backend]);
  const live = backend === "backend";
  const today = new Date().toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" }).toUpperCase();
  const priorityTargets = useMemo(() => {
    if (!live) return entities.slice(0, 4);
    const degree: Record<string, number> = {};
    for (const e of graph.edges) { degree[e.source] = (degree[e.source] ?? 0) + 1; degree[e.target] = (degree[e.target] ?? 0) + 1; }
    return graph.nodes.slice().sort((a, b) => (degree[b.id] ?? 0) - (degree[a.id] ?? 0)).slice(0, 4)
      .map((n) => ({ id: n.id, name: n.name, type: n.type, risk: degree[n.id] ?? 0 }));
  }, [live, graph]);
  return (
    <div className="page command-center">
      <div className="app-background-globe" aria-hidden="true">
        <GlobeScene />
      </div>
      <div className="command-title-row">
        <div className="command-topline">
          <span>Project</span>
          <span className="command-year">2020</span>
        </div>
        <div className="command-hero">
          <div className="brand-lock">DATA VISUALIZATION</div>
          <div className="subtle">Smart Entity &amp; Criminal Relationship Exploration Tool</div>
        </div>
        <div className="system-meta command-clock">
          <div>SYSTEM {live ? "LIVE" : "ONLINE · DEMO DATA"}</div>
          <div>{today}</div>
          <div>{`21:${String((tick % 60) + 10).padStart(2, "0")}:14`}</div>
        </div>
      </div>
      <div className="hud-grid">
        <section className="hud-col">
          <HudCard label="Global overview" className="hud-hero">
            <div className="hud-total">{live && summary ? summary.relationships.toLocaleString() : "1,812,020,001"}</div>
            <div className="hud-sublist">
              {live && summary ? (
                <>
                  <StatRow label="Cases" value={String(summary.cases)} />
                  <StatRow label="Sources" value={String(summary.sources)} />
                  <StatRow label="Alerts" value={String(summary.alerts)} />
                </>
              ) : (
                <>
                  <StatRow label="Events" value="3,705" />
                  <StatRow label="Alerts" value="12%" />
                  <StatRow label="Growth" value="-11%" />
                </>
              )}
            </div>
            <div className="hud-hero-track">
              <span />
              <span />
              <span />
              <span />
              <span />
            </div>
          </HudCard>

          <HudCard label="Live metrics">
            <div className="hud-card-head">
              <h3>Regional Activity</h3>
              <Donut />
            </div>
            <HoloList items={[
              { label: "CIT", value: "12,020" },
              { label: "NFC", value: "11,018" },
              { label: "KUC", value: "4,205" }
            ]} />
          </HudCard>

          <HudCard label="Entity ranking" title="Signal Distribution">
            <HoloList items={[
              { label: "Orion Meridian", value: "12,020" },
              { label: "Sector 17", value: "11,016" },
              { label: "Phone 4821", value: "4,205" },
              { label: "VX-2048", value: "2,400" }
            ]} />
          </HudCard>
        </section>

        <section className="hud-center">
          <div className="hud-center-top">
            <div className="hud-title-bar">DATA STATISTICS PLATFORM</div>
          </div>
          <div className="hud-globe-anchors">
            <div className="glass-strip"><Pin size={12} /> Global mesh locked</div>
            <div className="glass-strip"><Waves size={12} /> Signal sweep active</div>
            <div className="glass-strip"><ArrowUpRight size={12} /> 87.4% confidence</div>
          </div>
        </section>

        <section className="hud-col">
          <HudCard label="Advertising trend">
            <div className="hud-card-head">
              <h3>Node Share</h3>
              <Layers3 size={16} color="var(--blue)" />
            </div>
            <div className="hud-pie-row">
              <div className="hud-pie-block">
                <div className="hud-pie-shape" />
                <HoloList items={[
                  { label: "People", value: "35.2%" },
                  { label: "Vehicles", value: "27.4%" },
                  { label: "Accounts", value: "10.1%" }
                ]} />
              </div>
            </div>
          </HudCard>

          <HudCard label="Signal capture">
            <div className="hud-card-head">
              <h3>Cluster Resonance</h3>
              <Radar size={16} color="var(--blue)" />
            </div>
            <div className="hud-radar-shell">
              <div className="hud-radar" />
            </div>
            <div className="hud-radar-legend">
              {entityMix.slice(0, 4).map((item) => <StatRow key={item.label} label={item.label} value={`${item.value}%`} />)}
            </div>
          </HudCard>

          <HudCard label="Alert media relay" className="hud-video">
            <div className="hud-preview">
              <div className="hud-play"><Play size={18} /></div>
            </div>
            <div className="stat-row">
              <span className="stat-label">Suspicious relay</span>
              <span className="stat-value">35.2%</span>
            </div>
          </HudCard>
        </section>
      </div>

      <div className="hud-bottom hud-bottom-command">
        <HudCard label="24 hour trend" title="Signal wave" className="hud-bottom-chart">
          <Sparkline />
        </HudCard>
        <HudCard label="Investigation summary">
          {live && summary ? (
            <HoloList items={[
              { label: "Active cases", value: String(summary.cases) },
              { label: "Entities", value: summary.entities.toLocaleString() },
              { label: "Relationships", value: summary.relationships.toLocaleString() },
              { label: "Source files", value: String(summary.sources) }
            ]} />
          ) : (
            <HoloList items={[
              { label: "Active investigations", value: String(dashboardMetrics[0].value) },
              { label: "Entities monitored", value: dashboardMetrics[1].value.toLocaleString() },
              { label: "Relationships", value: dashboardMetrics[2].value.toLocaleString() },
              { label: "High-risk alerts", value: String(dashboardMetrics[3].value) }
            ]} />
          )}
        </HudCard>
        <HudCard label="Recent intelligence">
          <div className="mini-list compact-feed">
            {feed.map((item, i) => (
              <div key={item} className="entity feed-row">
                <div>
                  <div>{item}</div>
                  <div className="meta">14:{32 - i}:{8 - i * 2}</div>
                </div>
                <ChevronRight size={14} color="var(--muted)" />
              </div>
            ))}
          </div>
        </HudCard>
      </div>

      <div className="hud-bottom hud-bottom-command hud-bottom-tight">
        <HudCard label="Live entity queue" title="Priority targets">
          <div className="stack">
            {priorityTargets.map((entity) => (
              <div key={entity.id} className="entity entity-tight">
                <div>
                  <div>{entity.name}</div>
                  <div className="meta">{entity.type} · {entity.id}</div>
                </div>
                <div className="risk">{live ? `${entity.risk} links` : `Risk ${entity.risk}`}</div>
              </div>
            ))}
          </div>
        </HudCard>
        <HudCard label="Alert pulse" title="Incoming signals">
          <div className="stack">
            {live ? (
              <div className="meta">{summary?.alerts ?? 0} persisted indicator alerts. Open Alert Center to review.</div>
            ) : (
              alerts.map((alert) => (
                <div key={alert.title} className={`alert ${alert.severity.toLowerCase()}`}>
                  <div>
                    <div className="tag">{alert.severity}</div>
                    <div>{alert.title}</div>
                  </div>
                  <div className="meta">{alert.time}</div>
                </div>
              ))
            )}
          </div>
        </HudCard>
      </div>
    </div>
  );
}
