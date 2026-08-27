import { HudPage } from "../components/HudPage";
import { HudCard, HoloList } from "../components/HudPrimitives";

export function PlaceholderPage({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <HudPage title={title} subtitle={subtitle} rightMeta={<><div>LIVE MOCK DATA</div></>}>
      <div className="hud-placeholder-layout">
        <HudCard label="Primary surface" title="Operational View" className="hud-placeholder-surface">
          <div className="hud-surface-grid hud-surface-grid-alt" />
        </HudCard>
        <div className="hud-placeholder-side">
          <HudCard label="Summary" title="Signal Snapshot">
            <HoloList items={[{ label: "Priority entities", value: "24" }, { label: "Mapped links", value: "182,430" }, { label: "High-risk flags", value: "17", accent: "critical" }]} />
          </HudCard>
          <HudCard label="Recent events" title="Activity Stream">
            <HoloList items={[{ label: "21:03:14", value: "Cluster update" }, { label: "20:57:08", value: "Location event" }, { label: "20:41:52", value: "Transaction link" }]} />
          </HudCard>
        </div>
      </div>
    </HudPage>
  );
}
