import { entities } from "../data/mock";
import { useAppStore } from "../store";
import { HudPage } from "../components/HudPage";
import { HudCard, HoloList } from "../components/HudPrimitives";

export function Investigation() {
  const { selectedEntity, setSelectedEntity } = useAppStore();
  return (
    <HudPage title="CASE-2026-0817" subtitle="Organized Network Analysis" rightMeta={<><div>ACTIVE</div><div>HIGH PRIORITY</div></>}>
      <div className="hud-investigation-layout">
        <HudCard label="Case graph" title="Network View" className="hud-investigation-list">
          <div className="table">
            {entities.map((e) => (
              <button key={e.id} className={`entity ${selectedEntity?.id === e.id ? "selected" : ""}`} onClick={() => setSelectedEntity(e)}>
                <div>
                  <div>{e.name}</div>
                  <div className="meta">{e.type} · {e.id}</div>
                </div>
                <div className="risk">Risk {e.risk}</div>
              </button>
            ))}
          </div>
        </HudCard>
        <HudCard label="Entity profile" title={selectedEntity?.name ?? "No selection"} className="hud-investigation-profile">
          {selectedEntity && <HoloList items={[
            { label: "Entity type", value: selectedEntity.type },
            { label: "Risk score", value: String(selectedEntity.risk) },
            { label: "Aliases", value: selectedEntity.aliases.join(", ") },
            { label: "Relationships", value: String(selectedEntity.relationships) },
            { label: "Last activity", value: selectedEntity.lastActivity }
          ]} />}
          <div className="hud-investigation-bands">
            <div className="glass-strip">Evidence stream</div>
            <div className="glass-strip">Link confidence</div>
            <div className="glass-strip">Source integrity</div>
          </div>
        </HudCard>
      </div>
    </HudPage>
  );
}
