const { canonicalJSON, hashCanonical, receiptIdFromCore, sha256Hex } = require("./canonical.js");

async function runL1Verification(request = {}) {
  const input = typeof request.input === "string" ? request.input.trim() : canonicalJSON(request.payload || "");
  const mode = request.live ? "EXTERNAL_PENDING" : "LOCAL_DETERMINISTIC";
  const core = { integrity_standard: "ROS-L1-001", input_hash: sha256Hex(input), mode, observed: true, verified: false, authority: false, truth_claim: false };
  return { schema: "ReceiptOS/L1VerificationReceipt/v1", version: "1.0.0", receipt_id: receiptIdFromCore(core), event_hash: hashCanonical(core), algorithm: "sha256:rfc8785", mode, status: request.live ? "EXTERNAL_PENDING" : "WITNESS_ONLY", authority: false, truth_claim: false, observed: true, verified: false, input_hash: core.input_hash, canonical_core: canonicalJSON(core), stages: [{ id: "normalize-input", status: "complete", authority: false, truth_claim: false }, { id: "canonicalize-core", status: "complete", authority: false, truth_claim: false }, { id: request.live ? "external-rpc" : "local-deterministic", status: request.live ? "pending" : "complete", authority: false, truth_claim: false }], metadata: { observed_not_verified: true, replayable: true } };
}

module.exports = { runL1Verification };
