import { normalizeStatus } from "./state";
import type { EpochRecord } from "./types";

export function EpochHeader({ epoch }: { epoch: EpochRecord }) {
  const status = normalizeStatus(epoch.status);
  const timestamp = epoch.timestamp || epoch.created_at || "missing";

  return (
    <header style={{ border: "1px solid #e5e7eb", borderRadius: "0.75rem", padding: "1rem" }}>
      <p style={{ margin: 0, textTransform: "uppercase", letterSpacing: "0.08em", fontSize: "0.75rem" }}>Epoch Replay Viewer</p>
      <h1 style={{ margin: "0.35rem 0" }}>{epoch.id}</h1>
      <dl style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.75rem", margin: 0 }}>
        <div><dt>Timestamp UTC</dt><dd>{timestamp}</dd></div>
        <div><dt>Block Height</dt><dd>{epoch.block_number ?? "missing"}</dd></div>
        <div><dt>Chain ID</dt><dd>{epoch.chain_id ?? "missing"}</dd></div>
        <div><dt>Status</dt><dd><strong>{status}</strong></dd></div>
      </dl>
    </header>
  );
}
