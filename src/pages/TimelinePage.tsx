import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";

export function TimelinePage() {
  const events = ["08:42 Phone communication", "09:17 Location appearance", "10:03 Financial transaction", "11:46 Vehicle movement", "13:18 New relationship"];
  return (
    <HudPage title="TIMELINE" subtitle="Forensic chronological reconstruction" rightMeta={<><div>5 EVENTS</div></>}>
      <div className="hud-timeline-layout">
        <HudCard label="Event sequence" title="Investigation Timeline" className="hud-timeline-main">
          <div className="timeline-rail">
            {events.map((e, i) => (
              <div key={e} className="timeline-row">
                <div className="timeline-dot" />
                <div className="timeline-card">
                  <div className="tag">Step {i + 1}</div>
                  <div>{e.slice(6)}</div>
                  <div className="meta">{e.split(" ")[0]}</div>
                </div>
              </div>
            ))}
          </div>
        </HudCard>
        <HudCard label="Correlation" title="Temporal Spread" className="hud-timeline-side">
          <div className="hud-surface-grid hud-surface-grid-alt" />
        </HudCard>
      </div>
    </HudPage>
  );
}
