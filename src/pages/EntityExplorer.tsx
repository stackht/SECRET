import { useMemo, useState } from "react";
import { entities } from "../data/mock";
import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";

export function EntityExplorer() {
  const [query, setQuery] = useState("");
  const filtered = useMemo(() => entities.filter((e) => `${e.name} ${e.type}`.toLowerCase().includes(query.toLowerCase())), [query]);
  return (
    <HudPage title="ENTITY EXPLORER" subtitle="Search entity, identifier, organization..." rightMeta={<><div>{filtered.length} RESULTS</div></>}>
      <div className="hud-explorer-layout">
        <HudCard label="Search console" title="Entity Query" className="hud-explorer-search">
          <input className="control hud-search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search entity, identifier, organization..." />
          <div className="hud-search-hints">
            <span className="glass-strip">Try aliases</span>
            <span className="glass-strip">Try risk score</span>
            <span className="glass-strip">Try relationship tags</span>
          </div>
        </HudCard>
        <HudCard label="Result matrix" title="Matched Entities" className="hud-explorer-grid">
          <div className="hud-entity-grid">
            {filtered.map((e) => (
              <div className="hud-card hud-mini-card" key={e.id}>
                <div className="hud-label">{e.type}</div>
                <h3>{e.name}</h3>
                <div className="meta">Risk {e.risk} · Confidence {e.confidence}% · {e.relationships} links</div>
              </div>
            ))}
          </div>
        </HudCard>
      </div>
    </HudPage>
  );
}
