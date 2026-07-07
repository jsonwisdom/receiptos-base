import { createHash } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { runL1Verification } from "../../../packages/receiptos-core/verifier.js";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BASE_URL = process.env.NEXT_PUBLIC_URL || "https://receiptos-base.vercel.app";
const STREAM_URL = `${BASE_URL}/stream`;
const IDS = new Set(["docket-57-ros-0006", "ros-0006-live-stream", "ROS-0006:D57:A380"]);

function hashText(text: string) {
  return createHash("sha256").update(text).digest("hex");
}

function cleanHash(value?: string) {
  return value?.trim().replace(/^sha256:/i, "").replace(/^0x/i, "").toLowerCase();
}

function replay(receiptId?: string, receiptHash?: string, method?: string) {
  return {
    integrity_standard: "ROS-0006",
    receipt_id: receiptId,
    receipt_hash: receiptHash,
    verification_method: method,
    source: STREAM_URL,
    authority: false,
    truth_claim: false,
    verdict: "WITNESS_ONLY",
  };
}

function fail(reason: string, receiptId?: string, receiptHash?: string, receipt?: unknown) {
  const method = typeof receipt === "object" && receipt ? String((receipt as any).verification_method || "") : undefined;
  return {
    valid: false,
    reason,
    receipt,
    replay: replay(receiptId, receiptHash, method),
  };
}

function wireAccepted(receipt: any) {
  return Boolean(
    receipt &&
      receipt.status === "SIGNATURE_VERIFIED" &&
      receipt.integrity_standard === "ROS-0006" &&
      receipt.verification_method === "erc1271" &&
      String(receipt.magic || "").toLowerCase() === "0x1626ba7e" &&
      receipt.authority === false &&
      receipt.truth_claim === false &&
      receipt.verdict === "WITNESS_ONLY",
  );
}

async function verifyLegacy(body: any) {
  const receiptId = String(body?.receiptId || "").trim();
  const suppliedHash = cleanHash(body?.receiptHash);

  if (!receiptId) return fail("missing_receipt_id");
  if (!IDS.has(receiptId)) return fail("unknown_receipt_id", receiptId, suppliedHash);

  const stream = await fetch(STREAM_URL, { cache: "no-store", headers: { Accept: "application/json" } });
  if (!stream.ok) return fail("stream_unreachable", receiptId, suppliedHash);

  const text = await stream.text();
  const receiptHash = hashText(text);
  const receipt = JSON.parse(text);

  if (suppliedHash && suppliedHash !== receiptHash) {
    return fail("receipt_hash_mismatch", receiptId, receiptHash, receipt);
  }

  if (!wireAccepted(receipt)) {
    return fail("receipt_not_verified_by_wire", receiptId, receiptHash, receipt);
  }

  return {
    valid: true,
    reason: "receipt_replayed",
    receipt,
    replay: replay(receiptId, receiptHash, receipt.verification_method),
  };
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    if (typeof body?.input === "string" || body?.payload !== undefined || body?.live === true) {
      const receipt = await runL1Verification({ input: body.input, payload: body.payload, live: body.live });
      return NextResponse.json({ valid: true, receipt, stages: receipt.stages, audit: { authority: false, truth_claim: false, observed_not_verified: true } });
    }
    return NextResponse.json(await verifyLegacy(body));
  } catch {
    return NextResponse.json(fail("internal_error"));
  }
}

export async function GET() {
  return NextResponse.json(fail("post_required"));
}
