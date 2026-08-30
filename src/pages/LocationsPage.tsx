import { useEffect, useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard, HoloList } from "../components/HudPrimitives";
import { apiCaseLocations, type LocationsResponse } from "../services/api";
import { useCaseSelection } from "../services/useCaseSelection";

const EMPTY: LocationsResponse = { locations: [], visits: [] };

export function LocationsPage() {
  const { backend, cases, caseKey, setCaseKey } = useCaseSelection();
  const [data, setData] = useState<LocationsResponse>(EMPTY);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (backend !== "backend" || !caseKey) return;
    apiCaseLocations(caseKey)
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, [backend, caseKey]);

  const hotspots = [...data.locations].sort((a, b) => b.observations - a.observations).slice(0, 6);

  return (
    <HudPage
      title="LOCATION INTELLIGENCE"
      subtitle={backend === "backend" ? "Location entities from ingested records" : "Offline demo"}
      rightMeta={<>{backend === "backend" ? <div>{data.visits.length} OBSERVATIONS</div> : <div>OFFLINE</div>}{backend === "backend" ? <div>LIVE</div> : <div>DEMO</div>}</>}
    >
      {backend === "backend" && (
        <HudCard label="Case" title="Investigation selector">
          <select className="control hud-search" value={caseKey} onChange={(e) => setCaseKey(e.target.value)}>
            {cases.map((c) => <option key={c.case_number} value={c.case_number}>{c.case_number} · {c.title}</option>)}
          </select>
          {error && <div className="meta" style={{ color: "var(--red, #ff5f56)" }}>{error}</div>}
        </HudCard>
      )}
      <div className="hud-location-layout" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <HudCard label="Spatial surface" title="Observed Locations" className="hud-location-map">
          <div className="hud-surface-grid hud-surface-grid-alt" />
          <div className="hud-location-overlay" style={{ marginTop: 12 }}>
            <div className="glass-strip">Hotspots: {backend === "backend" ? hotspots.length : 0}</div>
            <div className="glass-strip">Entity visits: {backend === "backend" ? data.visits.length : 0}</div>
          </div>
        </HudCard>
        <div style={{ display: "grid", gap: 16 }}>
          <HudCard label="Activity hotspots" title="Location Clusters">
            <div className="stack">
              {hotspots.map((h) => (
                <div key={h.name} className="entity entity-tight">
                  <div>
                    <div>{h.name}</div>
                    <div className="meta">{h.observations} observations</div>
                  </div>
                  <div className="risk">{h.observations}</div>
                </div>
              ))}
              {!hotspots.length && <div className="meta">No location entities yet for this case.</div>}
            </div>
          </HudCard>
          <HudCard label="Entity sightings" title="Who was observed where">
            <HoloList
              items={data.visits.slice(0, 12).map((v) => ({
                label: v.location,
                value: `${v.entity_id} · ${v.observations}`,
              }))}
            />
          </HudCard>
        </div>
      </div>
    </HudPage>
  );
}