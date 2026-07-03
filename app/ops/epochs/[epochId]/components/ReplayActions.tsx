"use client";

import { useState, useTransition } from "react";
import { replayEpoch } from "../actions";

export function ReplayActions({ epochId, replayHash }: { epochId: string; replayHash?: string | null }) {
  const [isPending, startTransition] = useTransition();
  const [logs, setLogs] = useState<string[]>([]);

  function appendLog(message: string) {
    setLogs((existing) => [`${new Date().toISOString()} ${message}`, ...existing]);
  }

  function runReplay() {
    const confirmed = window.confirm("Run deterministic replay for this epoch?");
    if (!confirmed) return;

    startTransition(async () => {
      appendLog("REPLAY_REQUESTED");
      const result = await replayEpoch(epochId);
      appendLog(`${result.state} replay_hash=${result.replay_hash || "missing"}`);
    });
  }

  return (
    <section style={{ border: "1px solid #e5e7eb", borderRadius: "0.75rem", padding: "1rem" }}>
      <h2>Replay Actions</h2>
      <p>Replay hash: <code>{replayHash || "missing"}</code></p>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
        <button type="button" onClick={runReplay} disabled={isPending}>{isPending ? "Replaying..." : "Replay Epoch"}</button>
        <button type="button" onClick={() => appendLog("VERIFY_WITNESS_SET_REQUESTED")}>Verify Witness Set</button>
        <button type="button" onClick={() => appendLog("DOWNLOAD_MANIFEST_REQUESTED")}>Download Manifest</button>
        <button type="button" onClick={() => appendLog("DOWNLOAD_PROOF_BUNDLE_REQUESTED")}>Download Proof Bundle</button>
        <button type="button" onClick={() => appendLog("GENERATE_VERIFIER_REPORT_REQUESTED")}>Generate Verifier Report</button>
      </div>
      <h3>Action Log</h3>
      {logs.length === 0 ? <p>No actions executed in this browser session.</p> : <pre>{logs.join("\n")}</pre>}
    </section>
  );
}
