export type EpochState = "PASS" | "WITNESS_PENDING" | "DIVERGENCE_DETECTED" | "ERROR_NO_GREEN" | "NOT_FOUND";

export type InvariantState = Exclude<EpochState, "NOT_FOUND">;

export type EpochRecord = {
  id: string;
  created_at?: string | null;
  timestamp?: string | null;
  block_number?: number | string | null;
  chain_id?: string | null;
  status?: "FINALIZED" | "PENDING" | "FAILED" | string | null;
  epoch_root?: string | null;
  transparency_root?: string | null;
  witness_root?: string | null;
  manifest_hash?: string | null;
  replay_hash?: string | null;
  merkle_depth?: number | null;
  leaf_count?: number | null;
};

export type TransparencyLog = {
  id?: string;
  action?: string | null;
  created_at?: string | null;
  replay_hash?: string | null;
  details?: unknown;
};

export type WitnessManifest = {
  id: string;
  address?: string | null;
  signature?: string | null;
  created_at?: string | null;
  timestamp?: string | null;
  manifest_url?: string | null;
  verification_status?: "COMPLETE" | "PARTIAL" | "MISSING" | string | null;
};

export type VerifierReport = {
  id: string;
  filename?: string | null;
  size?: string | number | null;
  created_at?: string | null;
  timestamp?: string | null;
  type?: "FULL" | "INCREMENTAL" | "WITNESS_ONLY" | string | null;
  url?: string | null;
  integrity_hash?: string | null;
};

export type EpochReplayData = {
  epoch: EpochRecord;
  logs: TransparencyLog[];
  manifests: WitnessManifest[];
  reports: VerifierReport[];
};

export type Invariants = {
  epoch_root_verifiable: boolean;
  witness_set_complete: boolean;
  replay_consistent: boolean;
  no_truth_declared: boolean;
};
