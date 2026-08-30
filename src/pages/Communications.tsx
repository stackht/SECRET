import { useEffect, useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard, HoloList } from "../components/HudPrimitives";
import { apiCaseCommunications, type CommsResponse } from "../services/api";
import { useCaseSelection } from "../services/useCaseSelection";

const EMPTY: CommsResponse = { total_communications: 0, top_contacts: [], flows: [], bursts: [] };

export function CommunicationsPage() {
  const { backend, cases, caseKey, setCaseKey } = useCaseSelection();
  const [data, setData] = useState<CommsResponse>(EMPTY);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (backend !== "backend" || !caseKey) return;
    apiCaseCommunications(caseKey)
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, [backend, caseKey]);

  if (backend !== "backend") {
    return (
      <HudPage title="COMMUNICATION ANALYSIS" subtitle="Call and message cluster relationships" rightMeta={<><div>OFFLINE DEMO</div></>}>
        <HudCard label="Source" title="Synthetic mode">
          <div className="meta">Start the backend and ingest a case with CDR data to power live call graphs, top contacts, and burst detection.</div>
        </HudCard>
      </HudPage>
    );
  }

  return (
    <HudPage
      title="COMMUNICATION ANALYSIS"
      subtitle="Derived from persisted CDR relationships"
      rightMeta={<><div>{data.total_communications} LINKS</div><div>LIVE</div></>}
    >
      <div className="hud-explorer-layout">
        <HudCard label="Case" title="Investigation selector" className="hud-explorer-search">
          <select className="control hud-search" value={caseKey} onChange={(e) => setCaseKey(e.target.value)}>
            {cases.map((c) => <option key={c.case_number} value={c.case_number}>{c.case_number} · {c.title}</option>)}
          </select>
          {error && <div className="meta" style={{ color: "var(--red, #ff5f56)" }}>{error}</div>}
        </HudCard>
        <HudCard label="Traffic" title="Top contacts" className="hud-explorer-grid">
          <HoloList items={data.top_contacts.map((c, i) => ({ label: c.entity_id, value: `${c.count} contacts${i === 0 ? " · HUB" : ""}` }))} />
          {!data.top_contacts.length && <div className="meta">No CALLED relationships persisted yet.</div>}
        </HudCard>
      </div>
      {data.bursts.length > 0 && (
        <HudCard label="Temporal" title="Unusual communication bursts">
          <div className="hud-search-hints">
            {data.bursts.slice(0, 8).map((b) => (
              <span key={`${b.entity_id}-${b.window}`} className="glass-strip">
                {b.entity_id} @ {b.window} · {b.count}
              </span>
            ))}
          </div>
        </HudCard>
      )}
      {data.flows.length > 0 && (
        <HudCard label="Flows" title="Caller → receiver">
          <div className="table" style={{ maxHeight: 320, overflowY: "auto" }}>
            {data.flows.map((f) => (
              <div key={`${f.source}-${f.target}`} className="entity entity-tight">
                <div>
                  <div><b>{f.source}</b> → <b>{f.target}</b></div>
                  <div className="meta">count {f.count}</div>
                </div>
              </div>
            ))}
          </div>
        </HudCard>
      )}
    </HudPage>
  );
}