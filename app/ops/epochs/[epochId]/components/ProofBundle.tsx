import { truncateHash } from "./state";
import type { VerifierReport } from "./types";

export function ProofBundle({ bundles }: { bundles: VerifierReport[] }) {
  return (
    <section style={{ border: "1px solid #e5e7eb", borderRadius: "0.75rem", padding: "1rem" }}>
      <h2>Proof Bundles</h2>
      {bundles.length === 0 ? (
        <p>No proof bundles or verifier reports found.</p>
      ) : (
        <div style={{ display: "grid", gap: "0.75rem" }}>
          {bundles.map((bundle) => (
            <article key={bundle.id} style={{ border: "1px solid #f3f4f6", borderRadius: "0.5rem", padding: "0.75rem" }}>
              <p><strong>Filename:</strong> {bundle.filename || `verifier-report-${bundle.id}`}</p>
              <p><strong>Type:</strong> {bundle.type || "FULL"}</p>
              <p><strong>Size:</strong> {bundle.size ?? "missing"}</p>
              <p><strong>Timestamp:</strong> {bundle.timestamp || bundle.created_at || "missing"}</p>
              <p><strong>Integrity:</strong> <code title={bundle.integrity_hash || "missing"}>{truncateHash(bundle.integrity_hash)}</code></p>
              {bundle.url ? <a href={bundle.url}>Download proof bundle</a> : <strong>Download URL missing</strong>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
