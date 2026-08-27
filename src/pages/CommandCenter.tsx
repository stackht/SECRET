import { dashboardMetrics, feed, entities, alerts } from "../data/mock";
import { useEffect, useMemo, useState } from "react";
import { GlobeScene } from "../components/GlobeScene";
import { Activity, BarChart3, Radar, Shield, Users, Globe, Layers3, ChevronRight, Play, Pin, ArrowUpRight, Waves } from "lucide-react";
import { HoloList, HudCard, StatRow } from "../components/HudPrimitives";

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
  useEffect(() => { const t = setInterval(() => setTick((v) => v + 1), 2500); return () => clearInterval(t); }, []);
  return (
    <div className="page command-center">
      <div className="command-header">
        <div>
          <div className="brand-lock">SECRET</div>
          <div className="subtle">Smart Entity &amp; Criminal Relationship Exploration Tool</div>
        </div>
        <div className="system-meta">
          <div> SYSTEM ONLINE </div>
          <div> 27 AUG 2026 </div>
          <div> {`21:${String((tick % 60) + 10).padStart(2, "0")}:14`} </div>
        </div>
      </div>
      <div className="hud-grid">
        <section className="hud-col">
          <HudCard label="Global overview" className="hud-hero">
            <div className="hud-total">1,812,020,001</div>
            <div className="hud-sublist">
              <StatRow label="Events" value="3,705" />
              <StatRow label="Alerts" value="12%" />
              <StatRow label="Growth" value="-11%" />
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
          <HudCard label="Core sphere" className="hud-globe-frame">
            <div className="hud-globe-wrap">
              <GlobeScene />
              <div className="hud-target-pill">
                <span>SECTOR 17</span>
                <strong>12,024,010</strong>
              </div>
            </div>
            <div className="hud-globe-footer">
              <div className="glass-strip"><Pin size={12} /> Global mesh locked</div>
              <div className="glass-strip"><Waves size={12} /> Signal sweep active</div>
              <div className="glass-strip"><ArrowUpRight size={12} /> 87.4% confidence</div>
            </div>
          </HudCard>
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
          <HoloList items={[
            { label: "Active investigations", value: String(dashboardMetrics[0].value) },
            { label: "Entities monitored", value: dashboardMetrics[1].value.toLocaleString() },
            { label: "Relationships", value: dashboardMetrics[2].value.toLocaleString() },
            { label: "High-risk alerts", value: String(dashboardMetrics[3].value) }
          ]} />
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
            {entities.slice(0, 4).map((entity) => (
              <div key={entity.id} className="entity entity-tight">
                <div>
                  <div>{entity.name}</div>
                  <div className="meta">{entity.type} · {entity.id}</div>
                </div>
                <div className="risk">Risk {entity.risk}</div>
              </div>
            ))}
          </div>
        </HudCard>
        <HudCard label="Alert pulse" title="Incoming signals">
          <div className="stack">
            {alerts.map((alert) => (
              <div key={alert.title} className={`alert ${alert.severity.toLowerCase()}`}>
                <div>
                  <div className="tag">{alert.severity}</div>
                  <div>{alert.title}</div>
                </div>
                <div className="meta">{alert.time}</div>
              </div>
            ))}
          </div>
        </HudCard>
      </div>
    </div>
  );
}
