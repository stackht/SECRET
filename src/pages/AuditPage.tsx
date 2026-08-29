import { useEffect, useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";
import { apiListAudit, type AuditEntry } from "../services/api";

export function AuditPage() {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let active = true;
    apiListAudit(50)
      .then((res) => active && setEntries(res))
      .catch(() => active && setEntries([]))
      .finally(() => active && setLoaded(true));
    return () => {
      active = false;
    };
  }, []);

  return (
    <HudPage
      title="AUDIT LOG"
      subtitle="Append-only record of significant actions"
      rightMeta={<>{loaded ? <div>{entries.length} ENTRIES</div> : <div>LOADING</div>}</>}
    >
      <HudCard label="System log" title="Recent Actions" className="hud-audit-list">
        {entries.length ? (
          <div className="stack">
            {entries.map((e) => (
              <div key={e.id} className="entity entity-tight">
                <div>
                  <div>{e.action}</div>
                  <div className="meta">{e.object_type ?? "system"} · {e.object_id ?? "-"} · created {new Date(e.created_at).toLocaleString()}</div>
                </div>
                <div className="risk">{e.id}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="meta">{loaded ? "No audit entries recorded yet in this environment." : "Loading audit log..."}</div>
        )}
      </HudCard>
    </HudPage>
  );
}
