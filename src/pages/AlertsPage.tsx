import { useAppStore } from "../store";
import { alerts } from "../data/mock";
import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";

export function AlertsPage() {
  const { alertFilter, setAlertFilter } = useAppStore();
  const list = alerts.filter((a) => alertFilter === "ALL" || a.severity === alertFilter);
  return (
    <HudPage title="ALERT CENTER" subtitle="Professional alert management" rightMeta={<><div>{list.length} SIGNALS</div></>}>
      <div className="hud-alert-layout">
        <HudCard label="Alert queue" title="Severity Filter" className="hud-alert-filter">
          <div className="filters hud-filters">{["ALL","CRITICAL","HIGH","MEDIUM","LOW"].map((f) => <button key={f} className="pill" onClick={() => setAlertFilter(f as any)}>{f}</button>)}</div>
          <div className="hud-alert-ring" />
        </HudCard>
        <HudCard label="Alert stream" title="Incoming Signals" className="hud-alert-stream">
          <div className="stack">
            {list.map((a) => (
              <div key={a.title} className={`alert ${a.severity.toLowerCase()}`}>
                <div>
                  <div className="tag">{a.severity}</div>
                  <div>{a.title}</div>
                </div>
                <div className="meta">{a.time}</div>
              </div>
            ))}
          </div>
        </HudCard>
      </div>
    </HudPage>
  );
}
