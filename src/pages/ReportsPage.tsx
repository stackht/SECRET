import { useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";

export function ReportsPage() {
  const [generated, setGenerated] = useState(false);
  return (
    <HudPage title="REPORTS" subtitle="Investigation and analytics report generation" rightMeta={<><div>EXPORT READY</div></>}>
      <div className="hud-reports-layout">
        <HudCard label="Report modules" title="Editorial Pack" className="hud-reports-list">
          <div className="stack">
            {["Network Analysis Report","Entity Intelligence Report","Transaction Analysis","Communication Analysis","Investigation Summary"].map((x, i) => (
              <div key={x} className="entity entity-tight">
                <div>
                  <div>{x}</div>
                  <div className="meta">Section {String(i + 1).padStart(2, "0")}</div>
                </div>
                <div className="risk">Ready</div>
              </div>
            ))}
          </div>
        </HudCard>
        <HudCard label="Report preview" title="Composite Output" className="hud-reports-preview">
          <div className="hud-surface-grid hud-surface-grid-alt" />
          <button className="cta hud-report-cta" onClick={() => setGenerated(true)}>GENERATE REPORT</button>
          {generated && <div className="meta hud-report-note">This phase renders a polished preview only.</div>}
        </HudCard>
      </div>
    </HudPage>
  );
}
