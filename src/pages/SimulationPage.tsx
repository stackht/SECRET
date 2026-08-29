import { useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard, StatRow } from "../components/HudPrimitives";
import { apiRunSimulation, type SimulationResponse } from "../services/api";

export function SimulationPage() {
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = async (scenario = "NORMAL_NETWORK") => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiRunSimulation(scenario);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Simulation unavailable");
    } finally {
      setLoading(false);
    }
  };

  return (
    <HudPage
      title="INTELLIGENCE SIMULATION"
      subtitle="Run the full pipeline over synthetic data"
      rightMeta={<>{result ? <div>{result.entities} ENTITIES</div> : <div>READY</div>}</>}
    >
      <div className="hud-simulation-layout" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div style={{ display: "grid", gap: 16 }}>
          <HudCard label="Control" title="Run Intelligence Simulation">
            <p className="meta">Executes: generate → ingest → extract → resolve → graph → analytics → anomalies → insights.</p>
            <button className="cta" onClick={() => run("NORMAL_NETWORK")} disabled={loading} style={{ marginTop: 12 }}>
              {loading ? "SIMULATING..." : "RUN INTELLIGENCE SIMULATION"}
            </button>
            <button className="pill" onClick={() => run("COMMUNICATION_ANOMALY")} disabled={loading} style={{ marginTop: 8 }}>
              ANOMALY SCENARIO
            </button>
          </HudCard>

          {error ? (
            <HudCard label="System" title="Unavailable">
              <div className="meta">{error}</div>
            </HudCard>
          ) : null}

          {result ? (
            <HudCard label="Output" title="Pipeline Summary">
              <div className="stack">
                <StatRow label="Records ingested" value={String(result.steps[0]?.count ?? 0)} />
                <StatRow label="Entities extracted" value={String(result.entities)} />
                <StatRow label="Nodes written" value={String(result.nodes_written)} />
                <StatRow label="Elapsed" value={`${result.elapsed_seconds}s`} />
              </div>
            </HudCard>
          ) : null}
        </div>

        <HudCard label="Pipeline steps" title="Simulation Log">
          {result ? (
            <div className="mini-list compact-feed">
              {result.steps.map((s, i) => (
                <div key={s.label} className="entity feed-row">
                  <div>
                    <div>{s.label}</div>
                    <div className="meta">step {i + 1} · {s.count} items</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="meta">Run a simulation to populate the pipeline log.</div>
          )}
        </HudCard>
      </div>
    </HudPage>
  );
}
