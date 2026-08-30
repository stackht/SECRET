import { useEffect, useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";
import { apiGenerateReport, apiListReports, downloadReport, type ReportMeta, type ReportResponse } from "../services/api";
import { useCaseSelection } from "../services/useCaseSelection";

const MODULES: { report_type: string; label: string }[] = [
  { report_type: "investigation_summary", label: "Investigation Summary" },
  { report_type: "entity_intelligence", label: "Entity Intelligence Report" },
  { report_type: "network_analysis", label: "Network Analysis Report" },
  { report_type: "transaction_analysis", label: "Transaction Analysis" },
  { report_type: "communication_analysis", label: "Communication Analysis" },
];

export function ReportsPage() {
  const { backend, cases, caseKey, setCaseKey } = useCaseSelection();
  const [moduleType, setModuleType] = useState("network_analysis");
  const [generating, setGenerating] = useState(false);
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [meta, setMeta] = useState<ReportMeta[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (backend !== "backend") return;
    apiListReports()
      .then(setMeta)
      .catch(() => setMeta([]));
  }, [backend]);

  const generate = async () => {
    setError(null);
    setGenerating(true);
    try {
      const res = await apiGenerateReport({
        report_type: moduleType,
        case_number: caseKey || undefined,
        title: `${moduleType} — ${caseKey || "case"}`,
      });
      setReport(res);
      setMeta((prev) => [{ id: res.id, report_type: res.report_type, title: res.title, generated_at: res.generated_at, generated_by: res.generated_by, sections: res.sections.length }, ...prev]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Report generation failed");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <HudPage
      title="REPORTS"
      subtitle={backend === "backend" ? "Generated from live application state" : "Offline demo"}
      rightMeta={<>{report ? <div>EXPORT READY</div> : <div>STANDBY</div>}{backend === "backend" ? <div>LIVE</div> : <div>DEMO</div>}</>}
    >
      <div className="hud-reports-layout">
        <HudCard label="Report modules" title="Editorial Pack" className="hud-reports-list">
          <div className="stack">
            {MODULES.map((m) => (
              <button key={m.report_type} className={`entity entity-tight ${moduleType === m.report_type ? "selected" : ""}`} onClick={() => setModuleType(m.report_type)}>
                <div>
                  <div>{m.label}</div>
                  <div className="meta">{m.report_type}</div>
                </div>
              </button>
            ))}
            {backend === "backend" && (
              <select className="control hud-search" value={caseKey} onChange={(e) => setCaseKey(e.target.value)}>
                {cases.map((c) => <option key={c.case_number} value={c.case_number}>{c.case_number} · {c.title}</option>)}
              </select>
            )}
          </div>
        </HudCard>
        <HudCard label="Report preview" title="Composite Output" className="hud-reports-preview">
          <div className="hud-surface-grid hud-surface-grid-alt" />
          {backend === "backend" ? (
            <>
              <button className="cta hud-report-cta" onClick={generate} disabled={generating || !caseKey}>
                {generating ? "GENERATING..." : "GENERATE REPORT"}
              </button>
              {error && <div className="meta" style={{ color: "var(--red, #ff5f56)" }}>{error}</div>}
              {report && (
                <div className="stack" style={{ marginTop: 12 }}>
                  <div className="meta">{report.title} · {new Date(report.generated_at).toLocaleString()}</div>
                  <button className="cta" onClick={() => downloadReport(report)}>DOWNLOAD PDF</button>
                  <div className="stack" style={{ maxHeight: 260, overflowY: "auto" }}>
                    {report.sections.map((s) => (
                      <div key={s.heading} className="glass-strip"><b>{s.heading}</b><div className="meta">{s.body}</div></div>
                    ))}
                  </div>
                </div>
              )}
              {meta.length > 0 && (
                <div className="stack" style={{ marginTop: 12 }}>
                  <div className="meta">Previously generated:</div>
                  {meta.slice(0, 5).map((m) => <div key={m.id} className="meta">{m.title} · {m.sections} sections</div>)}
                </div>
              )}
            </>
          ) : (
            <div className="meta" style={{ marginTop: 12 }}>Start the backend to generate real reports. PDF export uses the native report writer.</div>
          )}
        </HudCard>
      </div>
    </HudPage>
  );
}