import { useState } from "react";
import { HudPage } from "../components/HudPage";
import { HudCard } from "../components/HudPrimitives";
import { apiAskAssistant, type AssistantResponse } from "../services/api";

export function AssistantPage() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState<AssistantResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await apiAskAssistant(question);
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
      subtitle="Local dataset analyst — evidence-grounded answers only"
      rightMeta={<>{<div>DATASET-GROUNDED</div>}</>}
    >
      <div className="hud-assistant-layout" style={{ maxWidth: 860, display: "grid", gap: 16 }}>
        <HudCard label="Query console" title="Ask the local dataset">
          <input
            className="control hud-search"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
            placeholder='e.g. "Show connections of P-0421"'
          />
          <div className="hud-search-hints">
            <span className="glass-strip">Try: connections of P-0421</span>
            <span className="glass-strip">Try: entity profile</span>
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

        {result ? (
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
