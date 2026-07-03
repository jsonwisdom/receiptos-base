import { NextRequest, NextResponse } from "next/server";
import { computeInterpretation } from "../../../lib/interpretation/policies";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BASE_URL = process.env.NEXT_PUBLIC_URL || "https://receiptos-base.vercel.app";
const VERIFY_URL = `${BASE_URL}/api/verify`;

type InterpretResponse = {
  valid: boolean;
  reason: string;
  receipt_id?: string;
  wire_reference?: string;
  interpretation?: unknown;
  authority: false;
  truth_claim: false;
  verdict: "WITNESS_ONLY";
};

function fail(reason: string, receiptId?: string): InterpretResponse {
  return {
    valid: false,
    reason,
    receipt_id: receiptId,
    authority: false,
    truth_claim: false,
    verdict: "WITNESS_ONLY",
  };
}

export async function POST(request: NextRequest): Promise<NextResponse<InterpretResponse>> {
  try {
    const body = await request.json().catch(() => ({}));
    const receiptId = String(body?.receipt_id || body?.receiptId || "").trim();
    const policy = String(body?.policy || "").trim();

    if (!receiptId) return NextResponse.json(fail("missing_receipt_id"), { status: 400 });
    if (!policy) return NextResponse.json(fail("missing_policy", receiptId), { status: 400 });
    if (body?.authority === true || body?.truth_claim === true) {
      return NextResponse.json(fail("promotion_attempt_rejected", receiptId), { status: 400 });
    }

    const verifyResponse = await fetch(VERIFY_URL, {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ receiptId }),
    });

    if (!verifyResponse.ok) return NextResponse.json(fail("verify_api_unreachable", receiptId), { status: 502 });

    const verified = await verifyResponse.json();
    if (verified?.valid !== true || verified?.receipt?.authority !== false || verified?.receipt?.truth_claim !== false) {
      return NextResponse.json(fail("receipt_not_verified", receiptId), { status: 404 });
    }

    const interpretation = computeInterpretation(verified.receipt, policy);
    if (!interpretation) return NextResponse.json(fail("unknown_policy", receiptId), { status: 400 });

    return NextResponse.json({
      valid: true,
      reason: "interpretation_computed",
      receipt_id: receiptId,
      wire_reference: verified?.replay?.source || `${BASE_URL}/stream`,
      interpretation,
      authority: false,
      truth_claim: false,
      verdict: "WITNESS_ONLY",
    });
  } catch {
    return NextResponse.json(fail("internal_error"), { status: 500 });
  }
}

export async function GET(): Promise<NextResponse<InterpretResponse>> {
  return NextResponse.json(fail("post_required"), { status: 405 });
}
