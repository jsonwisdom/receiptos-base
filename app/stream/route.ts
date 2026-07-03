import { existsSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";
import { NextRequest, NextResponse } from "next/server";
import { Contract, JsonRpcProvider, hashMessage, verifyMessage } from "ethers";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const EXPECTED_SIGNER = "0xa380552a27b0a5a2874ea7aa52cac09f542002e8";
const REQUIRED_BINDING = "provenance/identity-binding/jaywisdom-identity-binding.txt";
const REQUIRED_SIG = "provenance/identity-binding/jaywisdom-identity-binding.sig";
const REQUIRED_SUMS = "SHA256SUMS";
const ERC1271_MAGIC_VALUE = "0x1626ba7e";
const ERC1271_ABI = ["function isValidSignature(bytes32 hash, bytes signature) view returns (bytes4)"];

type Receipt = {
  schema: "RE-01/receipt-stream/v1";
  status: string;
  verdict: "WITNESS_ONLY";
  authority: false;
  truth_claim: false;
  signer: string;
  reason: string;
  verification_path?: string;
  binding_sha256?: string;
  signature_sha256?: string;
  digest?: string;
  magic?: string;
};

function sha256(data: string | Buffer) {
  return createHash("sha256").update(data).digest("hex");
}

function parseSums(content: string) {
  const entries = new Map<string, string>();
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    const match = trimmed.match(/^([a-fA-F0-9]{64})\s+\*?(.+)$/);
    if (match) entries.set(match[2].trim(), match[1].toLowerCase());
  }
  return entries;
}

function base(status: string, reason: string, extra: Partial<Receipt> = {}): Receipt {
  return {
    schema: "RE-01/receipt-stream/v1",
    status,
    reason,
    verdict: "WITNESS_ONLY",
    authority: false,
    truth_claim: false,
    signer: EXPECTED_SIGNER,
    ...extra,
  };
}

function isLikelyEoaSignature(signature: string) {
  return /^0x[0-9a-fA-F]{130}$/.test(signature);
}

async function buildReceipt(): Promise<Receipt> {
  const root = process.cwd();
  const bindingPath = join(root, REQUIRED_BINDING);
  const sigPath = join(root, REQUIRED_SIG);
  const sumsPath = join(root, REQUIRED_SUMS);

  if (!existsSync(bindingPath)) return base("PENDING_SIGNATURE", "missing_identity_binding_text");
  if (!existsSync(sigPath)) return base("PENDING_SIGNATURE", "missing_signature_file");
  if (!existsSync(sumsPath)) return base("PENDING_SIGNATURE", "missing_sha256sums");

  const bindingText = readFileSync(bindingPath, "utf8");
  const sigText = readFileSync(sigPath, "utf8");
  const sums = parseSums(readFileSync(sumsPath, "utf8"));
  const bindingHash = sha256(bindingText);
  const sigHash = sha256(sigText);

  if (sums.get(REQUIRED_BINDING) !== bindingHash) return base("PENDING_SIGNATURE", "binding_checksum_mismatch");
  if (sums.get(REQUIRED_SIG) !== sigHash) return base("PENDING_SIGNATURE", "signature_checksum_mismatch");

  let sig: any;
  try {
    sig = JSON.parse(sigText);
  } catch {
    return base("PENDING_SIGNATURE", "signature_json_invalid", { binding_sha256: bindingHash, signature_sha256: sigHash });
  }

  if (String(sig.signer || sig.address || "").toLowerCase() !== EXPECTED_SIGNER) {
    return base("PENDING_SIGNATURE", "wrong_signer", { binding_sha256: bindingHash, signature_sha256: sigHash });
  }
  if (sig.msg && sig.msg !== bindingText) {
    return base("PENDING_SIGNATURE", "signed_message_bytes_mismatch", { binding_sha256: bindingHash, signature_sha256: sigHash });
  }

  const signature = sig.signature || sig.sig;
  if (!signature || typeof signature !== "string" || !signature.startsWith("0x")) {
    return base("PENDING_SIGNATURE", "signature_hex_missing", { binding_sha256: bindingHash, signature_sha256: sigHash });
  }

  if (isLikelyEoaSignature(signature)) {
    const recovered = verifyMessage(bindingText, signature).toLowerCase();
    if (recovered === EXPECTED_SIGNER) {
      return base("SIGNATURE_VERIFIED", "eip191_recovered_expected_signer", {
        verification_path: "eip191",
        binding_sha256: bindingHash,
        signature_sha256: sigHash,
      });
    }
    return base("PENDING_SIGNATURE", "eip191_recovery_wrong_signer", {
      verification_path: "eip191",
      binding_sha256: bindingHash,
      signature_sha256: sigHash,
    });
  }

  const rpcUrl = process.env.BASE_RPC_URL || process.env.ETH_RPC_URL || process.env.RPC_URL;
  if (!rpcUrl) {
    return base("PENDING_SIGNATURE", "erc1271_rpc_missing", {
      verification_path: "erc1271",
      binding_sha256: bindingHash,
      signature_sha256: sigHash,
    });
  }

  const digest = hashMessage(bindingText);
  const provider = new JsonRpcProvider(rpcUrl);
  const contract = new Contract(EXPECTED_SIGNER, ERC1271_ABI, provider);
  const magic = String(await contract.isValidSignature(digest, signature)).toLowerCase();

  if (magic === ERC1271_MAGIC_VALUE) {
    return base("SIGNATURE_VERIFIED", "erc1271_magic_value_accepted", {
      verification_path: "erc1271",
      binding_sha256: bindingHash,
      signature_sha256: sigHash,
      digest,
      magic,
    });
  }

  return base("PENDING_SIGNATURE", "erc1271_magic_value_rejected", {
    verification_path: "erc1271",
    binding_sha256: bindingHash,
    signature_sha256: sigHash,
    digest,
    magic,
  });
}

export async function GET(request: NextRequest) {
  const receipt = await buildReceipt();
  const body = JSON.stringify(receipt, Object.keys(receipt).sort(), 2) + "\n";
  const etag = `"sha256:${sha256(body)}"`;

  if (request.headers.get("if-none-match") === etag) {
    return new NextResponse(null, {
      status: 304,
      headers: {
        ETag: etag,
        "Cache-Control": "public, max-age=60, must-revalidate",
      },
    });
  }

  return new NextResponse(body, {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ETag: etag,
      "Cache-Control": "public, max-age=60, must-revalidate",
    },
  });
}
