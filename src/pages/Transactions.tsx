import { useEffect, useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard, HoloList, StatRow } from "../components/HudPrimitives";
import { apiCaseTransactions, type TransResponse } from "../services/api";
import { useCaseSelection } from "../services/useCaseSelection";

const EMPTY: TransResponse = { total_transactions: 0, total_amount: 0, flows: [], top_senders: [] };

export function TransactionsPage() {
  const { backend, cases, caseKey, setCaseKey } = useCaseSelection();
  const [data, setData] = useState<TransResponse>(EMPTY);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (backend !== "backend" || !caseKey) return;
    apiCaseTransactions(caseKey)
      .then(setData)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, [backend, caseKey]);

  if (backend !== "backend") {
    return (
      <HudPage title="TRANSACTION ANALYSIS" subtitle="Financial flows and suspicious transfers" rightMeta={<><div>OFFLINE DEMO</div></>}>
        <HudCard label="Source" title="Synthetic mode">
          <div className="meta">Start the backend and ingest transaction records to power live volume charts and transfer graphs.</div>
        </HudCard>
      </HudPage>
    );
  }

  return (
    <HudPage
      title="TRANSACTION ANALYSIS"
      subtitle="Derived from persisted transfer edges"
      rightMeta={<><div>{data.total_transactions} TX</div><div>LIVE</div></>}
    >
      <div className="hud-explorer-layout">
        <HudCard label="Case" title="Investigation selector" className="hud-explorer-search">
          <select className="control hud-search" value={caseKey} onChange={(e) => setCaseKey(e.target.value)}>
            {cases.map((c) => <option key={c.case_number} value={c.case_number}>{c.case_number} · {c.title}</option>)}
          </select>
          {error && <div className="meta" style={{ color: "var(--red, #ff5f56)" }}>{error}</div>}
        </HudCard>
        <HudCard label="Volume" title="Aggregates" className="hud-explorer-grid">
          <HoloList items={[
            { label: "Total transactions", value: data.total_transactions.toLocaleString() },
            { label: "Total amount", value: data.total_amount.toLocaleString(undefined, { maximumFractionDigits: 0 }) },
            { label: "Active flows", value: data.flows.length.toLocaleString() },
          ]} />
        </HudCard>
      </div>
      {data.top_senders.length > 0 && (
        <HudCard label="Concentration" title="Top senders">
          <div className="hud-search-hints">
            {data.top_senders.slice(0, 8).map((s) => (
              <span key={s.account_id} className="glass-strip">
                {s.account_id} · {s.total_amount.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </span>
            ))}
          </div>
        </HudCard>
      )}
      {data.flows.length > 0 && (
        <HudCard label="Transfers" title="Sender → receiver">
          <div className="table" style={{ maxHeight: 320, overflowY: "auto" }}>
            {data.flows.map((f) => (
              <div key={`${f.source}-${f.target}`} className="entity entity-tight">
                <div>
                  <div><b>{f.source}</b> → <b>{f.target}</b></div>
                  <div className="meta">{f.count} transfers · {f.total_amount.toLocaleString(undefined, { maximumFractionDigits: 0 })}</div>
                </div>
              </div>
            ))}
          </div>
        </HudCard>
      )}
    </HudPage>
  );
}