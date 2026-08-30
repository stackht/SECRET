import { useEffect, useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";
import { apiCaseTimeline, type TimelineEvent } from "../services/api";
import { useCaseSelection } from "../services/useCaseSelection";

export function TimelinePage() {
  const { backend, cases, caseKey, setCaseKey } = useCaseSelection();
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (backend !== "backend" || !caseKey) return;
    apiCaseTimeline(caseKey)
      .then(setEvents)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, [backend, caseKey]);

  return (
    <HudPage
      title="TIMELINE"
      subtitle={backend === "backend" ? "Forensic chronological reconstruction from ingested sources" : "Offline demo"}
      rightMeta={<><div>{events.length} EVENTS</div>{backend === "backend" ? <div>LIVE</div> : <div>DEMO</div>}</>}
    >
      {backend === "backend" && (
        <HudCard label="Case" title="Investigation selector">
          <select className="control hud-search" value={caseKey} onChange={(e) => setCaseKey(e.target.value)}>
            {cases.map((c) => <option key={c.case_number} value={c.case_number}>{c.case_number} · {c.title}</option>)}
          </select>
          {error && <div className="meta" style={{ color: "var(--red, #ff5f56)" }}>{error}</div>}
        </HudCard>
      )}
      <div className="hud-timeline-layout" style={{ marginTop: 16 }}>
        <HudCard label="Event sequence" title={backend === "backend" ? "Source-fused timeline" : "Investigation Timeline"} className="hud-timeline-main">
          <div className="timeline-rail">
            {events.map((e, i) => (
              <div key={`${e.source_id}-${e.record_id}-${i}`} className="timeline-row">
                <div className="timeline-dot" />
                <div className="timeline-card">
                  <div className="tag">{e.source_id}</div>
                  <div>{e.summary}</div>
                  <div className="meta">
                    {e.timestamp ? new Date(e.timestamp).toLocaleString() : "untimed"}
                    {e.location ? ` · ${e.location}` : ""}
                  </div>
                </div>
              </div>
            ))}
            {!events.length && backend === "backend" && <div className="meta">No events yet — ingest sources for this case.</div>}
          </div>
        </HudCard>
        <HudCard label="Correlation" title="Source mix" className="hud-timeline-side">
          <div className="hud-surface-grid hud-surface-grid-alt" />
          {backend === "backend" && (
            <div className="hud-search-hints" style={{ marginTop: 10 }}>
              {Array.from(new Set(events.map((e) => e.source_id))).map((s) => (
                <span key={s} className="glass-strip">{s}</span>
              ))}
            </div>
          )}
        </HudCard>
      </div>
    </HudPage>
  );
}