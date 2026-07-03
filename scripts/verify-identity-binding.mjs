#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";

const EXPECTED_SIGNER = "0xa380552a27b0a5a2874ea7aa52cac09f542002e8";
const REQUIRED_BINDING = "provenance/identity-binding/jaywisdom-identity-binding.txt";
const REQUIRED_SIG = "provenance/identity-binding/jaywisdom-identity-binding.sig";
const REQUIRED_SUMS = "SHA256SUMS";

function result(status, reason, extra = {}) {
  return {
    status,
    reason,
    verdict: "WITNESS_ONLY",
    authority: false,
    truth_claim: false,
    ...extra,
  };
}

function sha256File(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function parseSums(content) {
  const entries = new Map();
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const match = trimmed.match(/^([a-fA-F0-9]{64})\s+\*?(.+)$/);
    if (!match) continue;
    entries.set(match[2].trim(), match[1].toLowerCase());
  }
  return entries;
}

function verify(rootDir) {
  const bindingPath = join(rootDir, REQUIRED_BINDING);
  const sigPath = join(rootDir, REQUIRED_SIG);
  const sumsPath = join(rootDir, REQUIRED_SUMS);

  if (!existsSync(bindingPath)) return result("PENDING_SIGNATURE", "missing_identity_binding_text");
  if (!existsSync(sigPath)) return result("PENDING_SIGNATURE", "missing_signature_file");
  if (!existsSync(sumsPath)) return result("PENDING_SIGNATURE", "missing_sha256sums");

  const sums = parseSums(readFileSync(sumsPath, "utf8"));
  if (!sums.has(REQUIRED_BINDING)) return result("PENDING_SIGNATURE", "sha256sums_missing_binding_entry");
  if (!sums.has(REQUIRED_SIG)) return result("PENDING_SIGNATURE", "sha256sums_missing_signature_entry");

  const bindingHash = sha256File(bindingPath);
  const sigHash = sha256File(sigPath);
  if (sums.get(REQUIRED_BINDING) !== bindingHash) return result("PENDING_SIGNATURE", "binding_checksum_mismatch");
  if (sums.get(REQUIRED_SIG) !== sigHash) return result("PENDING_SIGNATURE", "signature_checksum_mismatch");

  let sig;
  try {
    sig = JSON.parse(readFileSync(sigPath, "utf8"));
  } catch {
    return result("PENDING_SIGNATURE", "signature_json_invalid");
  }

  if (sig.schema !== "RECEIPTOS_IDENTITY_BINDING_SIG_V1") return result("PENDING_SIGNATURE", "unsupported_signature_schema");
  if (String(sig.signer || "").toLowerCase() !== EXPECTED_SIGNER) return result("PENDING_SIGNATURE", "wrong_signer");
  if (sig.method !== "personal_sign") return result("PENDING_SIGNATURE", "unsupported_signing_method");
  if (sig.signed_file !== REQUIRED_BINDING) return result("PENDING_SIGNATURE", "signed_file_mismatch");
  if (sig.authority !== false) return result("PENDING_SIGNATURE", "signature_authority_not_false");
  if (sig.truth_claim !== false) return result("PENDING_SIGNATURE", "signature_truth_claim_not_false");

  if (!sig.signature || typeof sig.signature !== "string" || !sig.signature.startsWith("0x")) {
    return result("PENDING_SIGNATURE", "signature_hex_missing");
  }

  return result("SIGNATURE_BUNDLE_PRESENT", "bundle_structure_valid", {
    signer: EXPECTED_SIGNER,
    binding_sha256: bindingHash,
    signature_sha256: sigHash,
  });
}

const rootDir = process.argv[2] || process.cwd();
const out = verify(rootDir);
console.log(JSON.stringify(out, null, 2));
process.exit(out.status === "SIGNATURE_BUNDLE_PRESENT" ? 0 : 1);
