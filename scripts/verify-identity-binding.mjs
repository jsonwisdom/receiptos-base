#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";
import { Contract, JsonRpcProvider, verifyMessage, hashMessage } from "ethers";

const EXPECTED_SIGNER = "0xa380552a27b0a5a2874ea7aa52cac09f542002e8";
const REQUIRED_BINDING = "provenance/identity-binding/jaywisdom-identity-binding.txt";
const REQUIRED_SIG = "provenance/identity-binding/jaywisdom-identity-binding.sig";
const REQUIRED_SUMS = "SHA256SUMS";
const ERC1271_MAGIC_VALUE = "0x1626ba7e";
const ERC1271_ABI = ["function isValidSignature(bytes32 hash, bytes signature) view returns (bytes4)"];

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

function isLikelyEoaSignature(signature) {
  return typeof signature === "string" && /^0x[0-9a-fA-F]{130}$/.test(signature);
}

async function verifyCrypto(bindingText, sig) {
  const signature = sig.signature || sig.sig;

  if (!signature || typeof signature !== "string" || !signature.startsWith("0x")) {
    return result("PENDING_SIGNATURE", "signature_hex_missing");
  }

  if (process.env.RECEIPTOS_ALLOW_TEST_SIGNATURE === "1" && sig.test_signature === true) {
    return result("SIGNATURE_VERIFIED", "test_signature_fixture_allowed", {
      verification_path: "test_fixture",
      signer: EXPECTED_SIGNER,
    });
  }

  if (isLikelyEoaSignature(signature)) {
    try {
      const recovered = verifyMessage(bindingText, signature).toLowerCase();
      if (recovered === EXPECTED_SIGNER) {
        return result("SIGNATURE_VERIFIED", "eip191_recovered_expected_signer", {
          verification_path: "eip191",
          signer: EXPECTED_SIGNER,
          recovered_signer: recovered,
        });
      }
      return result("PENDING_SIGNATURE", "eip191_recovery_wrong_signer", {
        verification_path: "eip191",
        expected_signer: EXPECTED_SIGNER,
        recovered_signer: recovered,
      });
    } catch (error) {
      return result("PENDING_SIGNATURE", "eip191_recovery_error", {
        verification_path: "eip191",
        error: String(error?.message || error),
      });
    }
  }

  const rpcUrl = process.env.BASE_RPC_URL || process.env.ETH_RPC_URL || process.env.RPC_URL;
  if (!rpcUrl) {
    return result("PENDING_SIGNATURE", "erc1271_rpc_missing", {
      verification_path: "erc1271",
      expected_signer: EXPECTED_SIGNER,
    });
  }

  try {
    const provider = new JsonRpcProvider(rpcUrl);
    const walletCode = await provider.getCode(EXPECTED_SIGNER);
    if (!walletCode || walletCode === "0x") {
      return result("PENDING_SIGNATURE", "erc1271_expected_signer_not_contract", {
        verification_path: "erc1271",
        expected_signer: EXPECTED_SIGNER,
      });
    }

    const digest = hashMessage(bindingText);
    const contract = new Contract(EXPECTED_SIGNER, ERC1271_ABI, provider);
    const magic = String(await contract.isValidSignature(digest, signature)).toLowerCase();

    if (magic === ERC1271_MAGIC_VALUE) {
      return result("SIGNATURE_VERIFIED", "erc1271_magic_value_accepted", {
        verification_path: "erc1271",
        signer: EXPECTED_SIGNER,
        digest,
        magic,
      });
    }

    return result("PENDING_SIGNATURE", "erc1271_magic_value_rejected", {
      verification_path: "erc1271",
      expected_magic: ERC1271_MAGIC_VALUE,
      actual_magic: magic,
      digest,
    });
  } catch (error) {
    return result("PENDING_SIGNATURE", "erc1271_verification_error", {
      verification_path: "erc1271",
      error: String(error?.message || error),
    });
  }
}

async function verify(rootDir) {
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
  if (String(sig.signer || sig.address || "").toLowerCase() !== EXPECTED_SIGNER) return result("PENDING_SIGNATURE", "wrong_signer");
  if (sig.method !== "personal_sign") return result("PENDING_SIGNATURE", "unsupported_signing_method");
  if (sig.signed_file !== REQUIRED_BINDING) return result("PENDING_SIGNATURE", "signed_file_mismatch");
  if (sig.authority !== false) return result("PENDING_SIGNATURE", "signature_authority_not_false");
  if (sig.truth_claim !== false) return result("PENDING_SIGNATURE", "signature_truth_claim_not_false");

  const bindingText = readFileSync(bindingPath, "utf8");
  if (sig.msg && sig.msg !== bindingText) return result("PENDING_SIGNATURE", "signed_message_bytes_mismatch");

  const cryptoResult = await verifyCrypto(bindingText, sig);
  return {
    ...cryptoResult,
    binding_sha256: bindingHash,
    signature_sha256: sigHash,
  };
}

const rootDir = process.argv[2] || process.cwd();
const out = await verify(rootDir);
console.log(JSON.stringify(out, null, 2));
process.exit(out.status === "SIGNATURE_VERIFIED" ? 0 : 1);
