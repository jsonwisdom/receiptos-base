import { truncateHash } from "./state";
import type { WitnessManifest } from "./types";

function deriveVerificationStatus(witnesses: WitnessManifest[]): "COMPLETE" | "PARTIAL" | "MISSING" {
  if (witnesses.length === 0) return "MISSING";
  const complete = witnesses.every((witness) => Boolean(witness.address && witness.signature && witness.manifest_url));
  return complete ? "COMPLETE" : "PARTIAL";
}

export function WitnessSet({ witnesses }: { witnesses: WitnessManifest[] }) {
  const verificationStatus = deriveVerificationStatus(witnesses);

  return (
    <section style={{ border: "1px solid #e5e7eb", borderRadius: "0.75rem", padding: "1rem" }}>
      <h2>Witness Set</h2>
      <p>Verification status: <strong>{verificationStatus}</strong></p>
      {witnesses.length === 0 ? (
        <p><strong>Missing witnesses:</strong> no witness manifests found for this epoch.</p>
      ) : (
        <div style={{ display: "grid", gap: "0.75rem" }}>
          {witnesses.map((witness) => (
            <article key={witness.id} style={{ border: "1px solid #f3f4f6", borderRadius: "0.5rem", padding: "0.75rem" }}>
              <p><strong>Address:</strong> <code title={witness.address || "missing"}>{truncateHash(witness.address)}</code></p>
              <p><strong>Signature:</strong> <code title={witness.signature || "missing"}>{truncateHash(witness.signature)}</code></p>
              <p><strong>Timestamp:</strong> {witness.timestamp || witness.created_at || "missing"}</p>
              <p><strong>Status:</strong> {witness.verification_status || (witness.address && witness.signature ? "COMPLETE" : "MISSING")}</p>
              {witness.manifest_url ? <a href={witness.manifest_url}>Download manifest</a> : <strong>Manifest missing</strong>}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
