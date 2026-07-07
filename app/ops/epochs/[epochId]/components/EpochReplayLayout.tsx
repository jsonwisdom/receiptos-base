import { EpochHeader } from "./EpochHeader";
import { InvariantBanner } from "./InvariantBanner";
import { ProofBundle } from "./ProofBundle";
import { ReplayActions } from "./ReplayActions";
import { RootStack } from "./RootStack";
import { WitnessSet } from "./WitnessSet";
import { deriveInvariants } from "./state";
import type { EpochReplayData, EpochState, InvariantState } from "./types";

export function EpochReplayLayout({ state, data }: { state: EpochState; data: EpochReplayData }) {
  const invariantState: InvariantState = state === "NOT_FOUND" ? "ERROR_NO_GREEN" : state;
  const invariants = deriveInvariants(data.epoch, data.manifests, state);

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "2rem", display: "grid", gap: "1rem" }}>
      <InvariantBanner state={invariantState} invariants={invariants} />
      <EpochHeader epoch={data.epoch} />
      <RootStack epoch={data.epoch} />
      <WitnessSet witnesses={data.manifests} />
      <ReplayActions epochId={data.epoch.id} replayHash={data.epoch.replay_hash} />
      <ProofBundle bundles={data.reports} />
      <section style={{ border: "1px solid #e5e7eb", borderRadius: "0.75rem", padding: "1rem" }}>
        <h2>Hard Rules</h2>
        <pre>{JSON.stringify({ authority: false, truth_claim: false, interpretation: false, confidence_score: false }, null, 2)}</pre>
      </section>
    </main>
  );
}
