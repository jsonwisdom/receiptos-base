"use server";

type ReplayResult = {
  epochId: string;
  replay_hash: string | null;
  state: "REPLAY_RECORDED" | "REPLAY_UNAVAILABLE";
};

const supabaseUrl = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

async function supabaseRest(path: string, init?: RequestInit) {
  if (!supabaseUrl || !supabaseKey) return null;

  const response = await fetch(`${supabaseUrl}/rest/v1/${path}`, {
    ...init,
    headers: {
      apikey: supabaseKey,
      Authorization: `Bearer ${supabaseKey}`,
      "Content-Type": "application/json",
      Prefer: "return=representation",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) return null;
  return response.json();
}

export async function replayEpoch(epochId: string): Promise<ReplayResult> {
  const epochRows = await supabaseRest(`epochs?id=eq.${encodeURIComponent(epochId)}&select=*`);
  const epoch = Array.isArray(epochRows) ? epochRows[0] : null;

  if (!epoch) {
    return { epochId, replay_hash: null, state: "REPLAY_UNAVAILABLE" };
  }

  const replayHash = typeof epoch.replay_hash === "string" ? epoch.replay_hash : null;

  await supabaseRest("transparency_log", {
    method: "POST",
    body: JSON.stringify({
      epoch_id: epochId,
      action: "REPLAY_EXECUTED",
      replay_hash: replayHash,
      authority: false,
      truth_claim: false,
    }),
  });

  return { epochId, replay_hash: replayHash, state: "REPLAY_RECORDED" };
}
