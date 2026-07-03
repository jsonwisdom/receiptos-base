import { createHash } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";

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

export async function POST(request: NextRequest) {
  try {
    const body = await request.json().catch(() => ({}));
    const receiptId = String(body?.receiptId || "").trim();
    const suppliedHash = cleanHash(body?.receiptHash);

    if (!receiptId) return NextResponse.json(fail("missing_receipt_id"));
    if (!IDS.has(receiptId)) return NextResponse.json(fail("unknown_receipt_id", receiptId, suppliedHash));

    const stream = await fetch(STREAM_URL, { cache: "no-store", headers: { Accept: "application/json" } });
    if (!stream.ok) return NextResponse.json(fail("stream_unreachable", receiptId, suppliedHash));

    const text = await stream.text();
    const receiptHash = hashText(text);
    const receipt = JSON.parse(text);

    if (suppliedHash && suppliedHash !== receiptHash) {
      return NextResponse.json(fail("receipt_hash_mismatch", receiptId, receiptHash, receipt));
    }

    if (!wireAccepted(receipt)) {
      return NextResponse.json(fail("receipt_not_verified_by_wire", receiptId, receiptHash, receipt));
    }

    return NextResponse.json({
      valid: true,
      reason: "receipt_replayed",
      receipt,
      replay: replay(receiptId, receiptHash, receipt.verification_method),
    });
  } catch {
    return NextResponse.json(fail("internal_error"));
  }
}

export async function GET() {
  return NextResponse.json(fail("post_required"));
}
