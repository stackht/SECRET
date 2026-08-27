import { useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";

export function SettingsPage() {
  const [dense, setDense] = useState(true);
  return (
    <HudPage title="SETTINGS" subtitle="Appearance and visualization preferences" rightMeta={<><div>DENSITY {dense ? "COMPACT" : "COMFORTABLE"}</div></>}>
      <div className="hud-settings-layout">
        <HudCard label="Profile" title="Interface Core" className="hud-settings-profile">
          <div className="hud-settings-avatar" />
          <div className="meta">Professional desktop configuration surface.</div>
        </HudCard>
        <HudCard label="Preference module" title="Interface Density" className="hud-settings-controls">
          <div className="row">
            <div className="meta">Toggles between compact and comfortable modes.</div>
            <button className="pill" onClick={() => setDense((v) => !v)}>{dense ? "COMPACT" : "COMFORTABLE"}</button>
          </div>
          <div className="hud-settings-scale">
            <span />
            <span className={dense ? "active" : ""} />
            <span className={!dense ? "active" : ""} />
          </div>
        </HudCard>
        <div className="stack hud-settings-stack">
          {["Appearance","Notifications","Visualization preferences","Data refresh preferences","Security preferences","About SECRET"].map((x) => (
            <HudCard label="Preference module" title={x} key={x}>
              <div className="meta">Native system screen styling with restrained micro-ornaments.</div>
            </HudCard>
          ))}
        </div>
      </div>
    </HudPage>
  );
}
