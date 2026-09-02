import { useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard, HoloList } from "../components/HudPrimitives";
import { apiAskAssistant, type AssistantResponse, type IntelligenceResponse } from "../services/api";
import { useCaseSelection } from "../services/useCaseSelection";

function PotentialLine({ rel }: { rel: { source: string; target: string; kind: string; confidence: number } }) {
  return (
    <div className="entity entity-tight">
      <div>
        <div><b>{rel.source}</b> ↔ <b>{rel.target}</b></div>
        <div className="meta">
          <span className={`tag ${rel.kind === "POTENTIAL" ? "" : ""}`}>{rel.kind}</span>
          {" "}{Math.round((rel.confidence || 0) * 100)}%
        </div>
      </div>
    </div>
  );
}

function StructuredPanels({ s }: { s: IntelligenceResponse }) {
  return (
    <div className="hud-assistant-results" style={{ display: "grid", gap: 14 }}>
      {/* Summary / key findings */}
      <HudCard label="Assistant" title={s.summary || s.query}>
        {s.key_findings.length > 0 && (
          <HoloList items={s.key_findings.map((k) => ({ label: k.label, value: k.detail }))} />
        )}
        {s.anomalies.length > 0 && (
          <div className="stack" style={{ marginTop: 10 }}>
            <div className="meta"><b>Anomalies detected</b></div>
            {s.anomalies.slice(0, 5).map((a, i) => (
              <div key={i} className="alert high">
                <div><div className="tag">ANOMALY</div><div>{a}</div></div>
              </div>
            ))}
          </div>
        )}
      </HudCard>

      {/* Relationships + potential */}
      {s.relationships.length > 0 && (
        <HudCard label="Relationships" title={`Observed & potential links (${s.relationships.length})`}>
          <div className="stack">
            {s.relationships.map((r, i) => <PotentialLine key={i} rel={r} />)}
          </div>
        </HudCard>
      )}

      {/* Evidence gaps */}
      {s.evidence_gaps.length > 0 && (
        <HudCard label="Evidence gaps" title="What is missing">
          <div className="stack">
            {s.evidence_gaps.slice(0, 5).map((g, i) => <div key={i} className="meta">• {g}</div>)}
          </div>
        </HudCard>
      )}

      {/* Next best action */}
      {s.next_best_action && (
        <HudCard label="Next best action" title="What to examine next">
          <div className="stack">
            <div><b>{s.next_best_action.subject}</b> — {s.next_best_action.kind}</div>
            <HoloList items={[
              { label: "Priority", value: Math.round(s.next_best_action.priority).toString() },
              { label: "Information gain", value: Math.round(s.next_best_action.info_gain).toString() },
            ]} />
            {s.next_best_action.reasoning.length > 0 && (
              <div className="stack">
                <div className="meta"><b>Why?</b></div>
                {s.next_best_action.reasoning.map((r, i) => <div key={i} className="meta">• {r}</div>)}
              </div>
            )}
            {s.next_best_action.recommended_data && (
              <div className="meta">Recommended data: {s.next_best_action.recommended_data}</div>
            )}
          </div>
        </HudCard>
      )}
    </div>
  );
}

export function AssistantPage() {
  const { backend, caseKey } = useCaseSelection();
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AssistantResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiAskAssistant(question, caseKey);
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Assistant unavailable");
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <HudPage
      title="INTELLIGENCE ASSISTANT"
      subtitle={backend === "backend" ? "Evidence-grounded, structured case intelligence" : "Structured demo intelligence"}
      rightMeta={<><div>STRUCTURED</div>{backend === "backend" ? <div>LIVE</div> : <div>DEMO</div>}</>}
    >
      <div className="hud-assistant-layout" style={{ maxWidth: 860, display: "grid", gap: 16 }}>
        <HudCard label="Query console" title="Ask an investigative question">
          <input
            className="control hud-search"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
            placeholder='e.g. "Show connections of P-0421", "potential links", "anomalies", "case overview"'
          />
          <div className="hud-search-hints">
            <span className="glass-strip">Try: connections of P-0421</span>
            <span className="glass-strip">Try: potential links</span>
            <span className="glass-strip">Try: anomalies</span>
            <span className="glass-strip">Try: case overview</span>
          </div>
          <button className="cta" onClick={ask} disabled={loading} style={{ marginTop: 14 }}>
            {loading ? "ANALYZING..." : "ASK ASSISTANT"}
          </button>
        </HudCard>

        {error ? (
          <HudCard label="System" title="Unavailable">
            <div className="meta">{error}</div>
          </HudCard>
        ) : null}

        {result?.structured ? (
          <StructuredPanels s={result.structured} />
        ) : result ? (
          <HudCard label="Assistant" title={result.question}>
            <p>{result.answer}</p>
            <div className="hud-search-hints" style={{ marginTop: 12 }}>
              {result.source_ids.length ? (
                result.source_ids.map((id) => <span key={id} className="glass-strip">{id}</span>)
              ) : (
                <span className="glass-strip">No supporting source</span>
              )}
            </div>
          </HudCard>
        ) : null}
      </div>
    </HudPage>
  );
}