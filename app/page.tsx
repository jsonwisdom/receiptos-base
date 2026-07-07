"use client";

import { useMemo, useState } from "react";

type VerifyResponse = {
  valid: boolean;
  receipt?: any;
  stages?: any[];
  audit?: {
    authority: false;
    truth_claim: false;
    observed_not_verified: true;
  };
  reason?: string;
};

export default function Layer1Portal() {
  const [input, setInput] = useState("docket-57-ros-0006");
  const [result, setResult] = useState<VerifyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const receiptText = useMemo(() => {
    return result?.receipt ? JSON.stringify(result.receipt, null, 2) : "";
  }, [result]);

  async function runVerification() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch("/api/verify", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ input }),
      });
      const body = await response.json();
      if (!response.ok) throw new Error(body?.reason || body?.error || "verification_failed");
      setResult(body);
    } catch (err) {
      setError(err instanceof Error ? err.message : "verification_failed");
    } finally {
      setLoading(false);
    }
  }

  async function copyReceipt() {
    if (receiptText) await navigator.clipboard.writeText(receiptText);
  }

  function downloadReceipt() {
    if (!receiptText) return;
    const blob = new Blob([receiptText], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${result?.receipt?.receipt_id || "receiptos-l1"}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main style={{ minHeight: "100vh", background: "#05070a", color: "#d7f9ff", fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace", padding: "2rem" }}>
      <section style={{ maxWidth: 980, margin: "0 auto" }}>
        <p style={{ color: "#67e8f9", letterSpacing: "0.16em", textTransform: "uppercase" }}>ReceiptOS Layer 1</p>
        <h1 style={{ fontSize: "2.5rem", margin: "0 0 0.5rem" }}>Verification Portal</h1>
        <p style={{ color: "#9ca3af" }}>authority=false · truth_claim=false · observed != verified · replayable or rejected</p>

        <div style={{ display: "grid", gap: "1rem", marginTop: "2rem" }}>
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Paste UID / tx hash / wallet / ENS / receipt ID"
            rows={4}
            style={{ width: "100%", borderRadius: 12, border: "1px solid #164e63", background: "#08111a", color: "#e5faff", padding: "1rem" }}
          />
          <button onClick={runVerification} disabled={loading || !input.trim()} style={{ borderRadius: 12, border: "1px solid #22d3ee", background: "#083344", color: "#ecfeff", padding: "0.9rem 1rem", cursor: "pointer" }}>
            {loading ? "Running pipeline..." : "Run verification"}
          </button>
        </div>

        {error && <p style={{ color: "#fca5a5" }}>Error: {error}</p>}

        {result?.receipt && (
          <section style={{ marginTop: "2rem", display: "grid", gap: "1rem" }}>
            <div style={{ border: "1px solid #155e75", borderRadius: 16, padding: "1rem", background: "#07131c" }}>
              <h2>Pipeline stages</h2>
              <ol>
                {(result.stages || []).map((stage: any) => (
                  <li key={stage.id}>{stage.id}: {stage.status}</li>
                ))}
              </ol>
            </div>

            <div style={{ border: "1px solid #155e75", borderRadius: 16, padding: "1rem", background: "#07131c" }}>
              <h2>Canonical receipt</h2>
              <pre style={{ overflowX: "auto", whiteSpace: "pre-wrap" }}>{receiptText}</pre>
              <div style={{ display: "flex", gap: "0.75rem" }}>
                <button onClick={copyReceipt}>Copy JSON</button>
                <button onClick={downloadReceipt}>Download JSON</button>
              </div>
            </div>
          </section>
        )}
      </section>
    </main>
  );
}
