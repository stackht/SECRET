import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";
import { WhatIfSimulator } from "../components/WhatIfSimulator";
import { InvestigativeLeadsPanel } from "../components/InvestigativeLeadsPanel";
import { RecommendationList } from "../components/IntelligenceUi";
import { useCaseIntelligence } from "../hooks/useCaseIntelligence";
import { useCaseSelection } from "../services/useCaseSelection";

export function SimulationPage() {
  const { backend, cases, caseKey, setCaseKey } = useCaseSelection();
  const { intel } = useCaseIntelligence(caseKey);

  const entityOptions = backend === "backend"
    ? (intel?.entity_priorities ?? []).map((p) => ({ id: p.subject, label: p.subject }))
    : (intel?.entity_priorities ?? []).slice(0, 5).map((p) => ({ id: p.subject, label: p.subject }));

  return (
    <HudPage
      title="INTELLIGENCE SIMULATION"
      subtitle="What-if sandbox, investigative leads and next-best-action"
      rightMeta={<>{intel ? <div>{intel.recommendations?.length ?? 0} ACTIONS</div> : <div>READY</div>}{backend === "backend" ? <div>LIVE</div> : <div>DEMO</div>}</>}
    >
      {backend === "backend" && (
        <HudCard label="Case" title="Investigation selector">
          <select className="control hud-search" value={caseKey} onChange={(e) => setCaseKey(e.target.value)}>
            {cases.map((c) => <option key={c.case_number} value={c.case_number}>{c.case_number} · {c.title}</option>)}
          </select>
        </HudCard>
      )}
      <div className="hud-simulation-layout" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
        <div style={{ display: "grid", gap: 16 }}>
          <WhatIfSimulator caseKey={caseKey} entityOptions={entityOptions} />
          <RecommendationList recs={intel?.recommendations ?? []} />
        </div>
        <InvestigativeLeadsPanel caseKey={caseKey} recommendations={intel?.recommendations ?? []} />
      </div>
    </HudPage>
  );
}