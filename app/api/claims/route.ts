import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

type ClaimResponse = {
  status: "CLAIM_UNPROMOTED" | "PROTOCOL_VIOLATION";
  valid: boolean;
  reason: string;
  claim?: {
    claim_hash: string;
    claim_status: "UNPROMOTED";
    truth_claim: false;
    verified_wire_reference: string;
  };
  replay: {
    authority: false;
    truth_claim: false;
    verdict: "WITNESS_ONLY";
  };
};

const replay: ClaimResponse["replay"] = {
  authority: false,
  truth_claim: false,
  verdict: "WITNESS_ONLY",
};

function violation(reason: string): ClaimResponse {
  return {
    status: "PROTOCOL_VIOLATION",
    valid: false,
    reason,
    replay,
  };
}

function isSafeClaimHash(value: unknown): value is string {
  return typeof value === "string" && /^[A-Za-z0-9:_\-.]{1,256}$/.test(value);
}

function isSafeWireRef(value: unknown): value is string {
  return typeof value === "string" && value.length > 0 && value.length <= 512;
}

function isPromotionString(value: string): boolean {
  const normalized = value.trim().toUpperCase();
  if (normalized === "UNPROMOTED") return false;
  return /(^|[^A-Z])PROMOTED([^A-Z]|$)/.test(normalized);
}

function containsPromotion(value: unknown): boolean {
  if (value === true) return true;
  if (typeof value === "string") return isPromotionString(value);
  if (Array.isArray(value)) return value.some(containsPromotion);
  if (value && typeof value === "object") return Object.values(value as Record<string, unknown>).some(containsPromotion);
  return false;
}

export async function POST(request: NextRequest): Promise<NextResponse<ClaimResponse>> {
  try {
    const body = await request.json().catch(() => null);
    if (!body || typeof body !== "object" || Array.isArray(body)) {
      return NextResponse.json(violation("invalid_json_object"), { status: 400 });
    }

    if (containsPromotion(body)) {
      return NextResponse.json(violation("promotion_attempt_rejected"), { status: 400 });
    }

    if ((body as any).truth_claim !== false) {
      return NextResponse.json(violation("truth_claim_must_be_false"), { status: 400 });
    }

    if ((body as any).claim_status !== "UNPROMOTED") {
      return NextResponse.json(violation("claim_status_must_be_unpromoted"), { status: 400 });
    }

    if (!isSafeClaimHash((body as any).claim_hash)) {
      return NextResponse.json(violation("invalid_claim_hash"), { status: 400 });
    }

    if (!isSafeWireRef((body as any).verified_wire_reference)) {
      return NextResponse.json(violation("invalid_wire_reference"), { status: 400 });
    }

    return NextResponse.json(
      {
        status: "CLAIM_UNPROMOTED",
        valid: true,
        reason: "claim_accepted_unpromoted_only",
        claim: {
          claim_hash: (body as any).claim_hash,
          claim_status: "UNPROMOTED",
          truth_claim: false,
          verified_wire_reference: (body as any).verified_wire_reference,
        },
        replay,
      },
      { status: 200 },
    );
  } catch {
    return NextResponse.json(violation("internal_error"), { status: 400 });
  }
}

export async function GET(): Promise<NextResponse<ClaimResponse>> {
  return NextResponse.json(violation("post_required"), { status: 405 });
}
