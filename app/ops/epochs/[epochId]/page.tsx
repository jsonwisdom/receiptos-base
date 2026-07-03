import { EpochReplayLayout } from "./components/EpochReplayLayout";
import { DivergenceDetected, EpochNotFound, ErrorNoGreen, WitnessPending } from "./components/EmptyState";
import { determineEpochState } from "./components/state";
import type { EpochRecord, TransparencyLog, VerifierReport, WitnessManifest } from "./components/types";

type PageProps = {
  params: Promise<{ epochId: string }>;
};

const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

async function supabaseSelect<T>(path: string): Promise<{ data: T[]; error: string | null }> {
  if (!supabaseUrl || !supabaseKey) {
    return { data: [], error: "Supabase environment is not configured." };
  }

  const response = await fetch(`${supabaseUrl}/rest/v1/${path}`, {
    headers: {
      apikey: supabaseKey,
      Authorization: `Bearer ${supabaseKey}`,
    },
    cache: "no-store",
  });

  if (!response.ok) {
    return { data: [], error: `${response.status} ${response.statusText}` };
  }

  return { data: await response.json(), error: null };
}

export default async function EpochReplayViewer({ params }: PageProps) {
  const { epochId } = await params;
  const encodedEpochId = encodeURIComponent(epochId);

  const [epochResult, logsResult, manifestsResult, reportsResult] = await Promise.all([
    supabaseSelect<EpochRecord>(`epochs?id=eq.${encodedEpochId}&select=*`),
    supabaseSelect<TransparencyLog>(`transparency_log?epoch_id=eq.${encodedEpochId}&select=*&order=created_at.desc`),
    supabaseSelect<WitnessManifest>(`witness_manifests?epoch_id=eq.${encodedEpochId}&select=*`),
    supabaseSelect<VerifierReport>(`verifier_reports?epoch_id=eq.${encodedEpochId}&select=*`),
  ]);

  if (epochResult.error && epochResult.data.length === 0) {
    return <ErrorNoGreen error={epochResult.error} />;
  }

  const epoch = epochResult.data[0] || null;
  const manifests = manifestsResult.data || [];
  const reports = reportsResult.data || [];
  const logs = logsResult.data || [];
  const state = determineEpochState(epoch, manifests, reports);

  if (state === "NOT_FOUND") return <EpochNotFound epochId={epochId} />;
  if (!epoch) return <EpochNotFound epochId={epochId} />;

  if (state === "WITNESS_PENDING") return <WitnessPending epochId={epochId} />;

  if (state === "DIVERGENCE_DETECTED") {
    return (
      <DivergenceDetected
        epochId={epochId}
        expectedHash={epoch.epoch_root || "missing"}
        actualHash={epoch.replay_hash || "missing"}
        diff={{ summary: "replay_hash differs from epoch_root" }}
      />
    );
  }

  if (state === "ERROR_NO_GREEN") return <ErrorNoGreen error="Required epoch roots are missing." />;

  return <EpochReplayLayout state={state} data={{ epoch, logs, manifests, reports }} />;
}
