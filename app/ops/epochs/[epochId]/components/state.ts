import type { EpochRecord, EpochState, Invariants, VerifierReport, WitnessManifest } from "./types";

export function determineEpochState(
  epoch: EpochRecord | null,
  manifests: WitnessManifest[] | null,
  _reports: VerifierReport[] | null,
): EpochState {
  if (!epoch) return "NOT_FOUND";

  if (!epoch.epoch_root || !epoch.transparency_root) return "ERROR_NO_GREEN";

  if (!manifests || manifests.length === 0) return "WITNESS_PENDING";

  if (epoch.replay_hash && epoch.replay_hash !== epoch.epoch_root) return "DIVERGENCE_DETECTED";

  return "PASS";
}

export function deriveInvariants(
  epoch: EpochRecord,
  manifests: WitnessManifest[],
  state: EpochState,
): Invariants {
  return {
    epoch_root_verifiable: Boolean(epoch.epoch_root && epoch.transparency_root),
    witness_set_complete: manifests.length > 0,
    replay_consistent: state !== "DIVERGENCE_DETECTED",
    no_truth_declared: true,
  };
}

export function truncateHash(value?: string | null): string {
  if (!value) return "missing";
  if (value.length <= 18) return value;
  return `${value.slice(0, 10)}...${value.slice(-8)}`;
}

export function normalizeStatus(status?: string | null): "FINALIZED" | "PENDING" | "FAILED" {
  if (status === "FINALIZED" || status === "PENDING" || status === "FAILED") return status;
  return "PENDING";
}
