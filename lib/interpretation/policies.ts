export type WireReceipt = {
  status?: string;
  integrity_standard?: string;
  verification_method?: string;
  verification_path?: string;
  magic?: string;
  chain_id?: number;
  verdict?: string;
  authority?: boolean;
  truth_claim?: boolean;
  reason?: string;
};

export type Interpretation = {
  policy: "trust-score-v1" | "risk-v1";
  score: number;
  inputs: string[];
  computed_at: string;
  authority: false;
  truth_claim: false;
  verdict: "WITNESS_ONLY";
};

function base(policy: Interpretation["policy"], score: number, inputs: string[]): Interpretation {
  return {
    policy,
    score: Math.max(0, Math.min(1, score)),
    inputs: Array.from(new Set(inputs)).sort(),
    computed_at: "1970-01-01T00:00:00.000Z",
    authority: false,
    truth_claim: false,
    verdict: "WITNESS_ONLY",
  };
}

export function computeInterpretation(receipt: WireReceipt, policy: string): Interpretation | null {
  const inputs: string[] = [];

  if (receipt.status === "SIGNATURE_VERIFIED") inputs.push("signature_verified");
  if (receipt.integrity_standard === "ROS-0006") inputs.push("ros_0006");
  if (receipt.verification_method === "erc1271") inputs.push("erc1271");
  if (String(receipt.magic || "").toLowerCase() === "0x1626ba7e") inputs.push("erc1271_magic");
  if (receipt.chain_id === 8453) inputs.push("chain_8453");
  if (receipt.authority === false) inputs.push("authority_false");
  if (receipt.truth_claim === false) inputs.push("truth_claim_false");
  if (receipt.verdict === "WITNESS_ONLY") inputs.push("witness_only");

  if (policy === "trust-score-v1") {
    return base("trust-score-v1", inputs.length / 8, inputs);
  }

  if (policy === "risk-v1") {
    const missing = 8 - inputs.length;
    return base("risk-v1", missing / 8, inputs);
  }

  return null;
}
