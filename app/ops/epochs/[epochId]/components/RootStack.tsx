"use client";

import { truncateHash } from "./state";
import type { EpochRecord } from "./types";

const rootKeys = ["epoch_root", "transparency_root", "witness_root", "manifest_hash", "replay_hash"] as const;

type RootKey = (typeof rootKeys)[number];

export function RootStack({ epoch }: { epoch: EpochRecord }) {
  async function copy(value?: string | null) {
    if (!value || !navigator?.clipboard) return;
    await navigator.clipboard.writeText(value);
  }

  return (
    <section style={{ border: "1px solid #e5e7eb", borderRadius: "0.75rem", padding: "1rem" }}>
      <h2>Root Stack</h2>
      <div style={{ display: "grid", gap: "0.75rem" }}>
        {rootKeys.map((key: RootKey) => {
          const value = epoch[key];
          return (
            <div key={key} style={{ border: "1px solid #f3f4f6", borderRadius: "0.5rem", padding: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "center" }}>
                <strong>{key}</strong>
                <button type="button" onClick={() => copy(value)} disabled={!value}>Copy</button>
              </div>
              <code title={value || "missing"}>{truncateHash(value)}</code>
            </div>
          );
        })}
      </div>
      <p style={{ marginBottom: 0 }}>
        Merkle path: depth <strong>{epoch.merkle_depth ?? "missing"}</strong>, leaves <strong>{epoch.leaf_count ?? "missing"}</strong>
      </p>
    </section>
  );
}
