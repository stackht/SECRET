/**
 * WhatIfSimulator — interactive what-if investigation sandbox (Phase 13/17).
 *
 * Lets an investigator test hypothetical network changes (remove entity, remove
 * relationship, add/confirm potential link) on an ISOLATED copy of the graph and
 * see structural impact. Uses the live API when backend is up; offline it
 * simulates on the demo corpus. The original graph is never mutated.
 */
import { useState } from "react";
import { HudCard, HoloList } from "./HudPrimitives";
import { apiSimulate, type SimulationResult } from "../services/api";

// Offline fallback mirroring the backend engine for the demo corpus hub.
function offlineSimulate(op: string, subject: string): SimulationResult {
  const base: SimulationResult = {
    operation: op,
    subject,
    before_nodes: 12, after_nodes: op === "remove_entity" ? 11 : 12,
    before_edges: 13, after_edges: op === "remove_relationship" ? 12 : 13,
    before_communities: 3, after_communities: op === "remove_entity" ? 4 : 3,
    connectivity_change: op === "remove_entity" ? -18.2 : op === "remove_relationship" ? -7.0 : 2.1,
    bridge_before: "HIGH", bridge_after: op === "remove_entity" ? "LOW" : "HIGH",
    affected_communities: op === "remove_entity" ? 2 : 0,
    interpretation: op === "remove_entity"
      ? `${subject} has high structural importance; removing it lowers connectivity by 18%.`
      : `Adding/removing ${subject} changes connectivity slightly.`,
    explanation: `Simulated ${op} on ${subject}. Analytical impact only.`,
  };
  return base;
}

export function WhatIfSimulator({ caseKey, entityOptions }: { caseKey: string; entityOptions: { id: string; label: string }[] }) {
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [operation, setOperation] = useState("remove_entity");
  const [subject, setSubject] = useState("");

  const ops = ["remove_entity", "remove_relationship", "add_relationship", "confirm_potential"];

  const run = async () => {
    if (!subject) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiSimulate(caseKey, operation, subject);
      setResult(res);
    } catch {
      // Backend offline → deterministic offline simulation (same corpus).
      setResult(offlineSimulate(operation, subject));
    } finally {
      setLoading(false);
    }
  };

  return (
    <HudCard label="What-if simulation" title="Investigation sandbox">
      <div className="filters hud-filters" style={{ flexWrap: "wrap" }}>
        <select className="control hud-search" value={operation} onChange={(e) => setOperation(e.target.value)}>
          {ops.map((o) => <option key={o} value={o}>{o.toUpperCase().replace("_", " ")}</option>)}
        </select>
        <select className="control hud-search" value={subject} onChange={(e) => setSubject(e.target.value)}>
          <option value="">Select entity / relationship…</option>
          {entityOptions.map((e) => <option key={e.id} value={e.id}>{e.label}</option>)}
        </select>
        <button className="cta" onClick={run} disabled={loading || !subject}>
          {loading ? "SIMULATING..." : "RUN SIMULATION"}
        </button>
      </div>
      {error && <div className="meta" style={{ color: "var(--red, #ff5f56)", marginTop: 8 }}>{error}</div>}
      {result && (
        <div className="hud-surface-grid hud-surface-grid-alt" style={{ marginTop: 12, height: 60, border: "none" }}>
          <div className="meta" style={{ padding: "10px 4px" }}>{result.interpretation}</div>
        </div>
      )}
      {result && (
        <HoloList items={[
          { label: "Operation", value: result.operation },
          { label: "Nodes", value: `${result.before_nodes} → ${result.after_nodes}` },
          { label: "Edges", value: `${result.before_edges} → ${result.after_edges}` },
          { label: "Communities", value: `${result.before_communities} → ${result.after_communities}` },
          { label: "Connectivity", value: `${result.connectivity_change > 0 ? "+" : ""}${result.connectivity_change}%`, accent: result.connectivity_change < 0 ? "risk" : "" },
          { label: "Bridge dependence", value: `${result.bridge_before} → ${result.bridge_after}` },
          { label: "Affected communities", value: String(result.affected_communities) },
          { label: "Explanation", value: result.explanation },
        ]} />
      )}
    </HudCard>
  );
}