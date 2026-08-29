import { useEffect, useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard, HoloList, StatRow } from "../components/HudPrimitives";
import { apiTemporalLocation, type TemporalLocationResponse } from "../services/api";

const FALLBACK: TemporalLocationResponse = {
  windows: [
    { window_start: "2026-08-14T07:00", count: 3, sources: ["FIR", "VEHICLE"] },
    { window_start: "2026-08-14T09:00", count: 2, sources: ["INTELLIGENCE"] },
  ],
  event_sequence: [
    { record_id: "SR-0001", timestamp: "2026-08-14T09:00", source: "FIR", summary: "FIR reported. Person A at Sector 17.", location: "L-3007" },
  ],
  communication_bursts: [{ window_start: "2026-08-14T11:00", count: 4 }],
  location_activity: [
    { location: "Sector 17", events: 6, level: "HIGH" },
    { location: "Dock 4", events: 3, level: "MEDIUM" },
  ],
  movement: [
    { record_id: "SR-0004", timestamp: "2026-08-14T07:30", source: "VEHICLE", summary: "VX-2048 at Dock 4.", location: "L-4002" },
  ],
};

export function LocationsPage() {
  const [data, setData] = useState<TemporalLocationResponse>(FALLBACK);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let active = true;
    apiTemporalLocation({ scenario: "NORMAL_NETWORK" })
      .then((res) => {
        if (active) {
          setData(res);
          setLoaded(true);
        }
      })
      .catch(() => {
        if (active) {
          setData(FALLBACK);
          setLoaded(true);
        }
      });
    return () => {
      active = false;
    };
  }, []);

  const hotspots = [...data.location_activity].sort((a, b) => b.events - a.events).slice(0, 4);

  return (
    <HudPage
      title="LOCATION INTELLIGENCE"
      subtitle="Synthetic geospatial, movement paths, and activity clusters"
      rightMeta={<>{loaded ? <div>SYNTHETIC MAP ONLINE</div> : <div>LOADING</div>}</>}
    >
      <div className="hud-location-layout" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <HudCard label="Spatial surface" title="Activity Map" className="hud-location-map">
          <div className="hud-surface-grid hud-surface-grid-alt" />
          <div className="hud-location-overlay" style={{ marginTop: 12 }}>
            <div className="glass-strip">Hotspots: {hotspots.length}</div>
            <div className="glass-strip">Movement paths: {data.movement.length}</div>
          </div>
        </HudCard>

        <div style={{ display: "grid", gap: 16 }}>
          <HudCard label="Activity hotspots" title="Location Clusters">
            <div className="stack">
              {hotspots.map((h) => (
                <div key={h.location} className="entity entity-tight">
                  <div>
                    <div>{h.location}</div>
                    <div className="meta">{h.events} events · {h.level} activity</div>
                  </div>
                  <div className="risk">{h.events}</div>
                </div>
              ))}
            </div>
          </HudCard>

          <HudCard label="Movement sequence" title="Movement Paths">
            <div className="mini-list">
              {data.movement.slice(0, 5).map((m) => (
                <StatRow key={m.record_id} label={m.location ?? "?"} value={m.source} />
              ))}
            </div>
          </HudCard>

          <HudCard label="Temporal windows" title="Time Distribution">
            <HoloList
              items={data.windows.map((w) => ({
                label: w.window_start,
                value: `${w.count} events`,
              }))}
            />
          </HudCard>
        </div>
      </div>
    </HudPage>
  );
}
