import { NextResponse } from "next/server";

interface WireReceipt {
  status?: string;
  integrity_standard?: string;
  verification_method?: string;
  magic?: string;
  authority?: boolean;
  truth_claim?: boolean;
  verdict?: string;
  reason?: string;
}

interface HealthResponse {
  status: "ok" | "degraded";
  service: string;
  wire: "reachable" | "unreachable";
  stream: "healthy" | "unhealthy";
  verification_gate: "passed" | "pending";
  integrity_standard: "ROS-0006" | "UNKNOWN";
  verification_method?: string;
  authority: false;
  truth_claim: false;
  wire_reason?: string;
  timestamp: string;
}

const BASE_URL = process.env.NEXT_PUBLIC_URL || "https://receiptos-base.vercel.app";
const REQUIRED_MAGIC = "0x1626ba7e";

function gatePassed(receipt: WireReceipt | null): boolean {
  return Boolean(
    receipt &&
      receipt.status === "SIGNATURE_VERIFIED" &&
      receipt.integrity_standard === "ROS-0006" &&
      receipt.verification_method === "erc1271" &&
      String(receipt.magic || "").toLowerCase() === REQUIRED_MAGIC &&
      receipt.authority === false &&
      receipt.truth_claim === false &&
      receipt.verdict === "WITNESS_ONLY",
  );
}

async function fetchWireReceipt(): Promise<WireReceipt | null> {
  try {
    const response = await fetch(`${BASE_URL}/stream`, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (!response.ok) return null;
    return (await response.json()) as WireReceipt;
  } catch {
    return null;
  }
}

export async function GET(): Promise<NextResponse<HealthResponse>> {
  const receipt = await fetchWireReceipt();
  const passed = gatePassed(receipt);

  return NextResponse.json(
    {
      status: receipt ? "ok" : "degraded",
      service: "receiptos-frame",
      wire: receipt ? "reachable" : "unreachable",
      stream: receipt ? "healthy" : "unhealthy",
      verification_gate: passed ? "passed" : "pending",
      integrity_standard:
        receipt?.integrity_standard === "ROS-0006" ? "ROS-0006" : "UNKNOWN",
      verification_method: receipt?.verification_method,
      authority: false,
      truth_claim: false,
      wire_reason: receipt?.reason || "wire_unreachable_or_invalid",
      timestamp: new Date().toISOString(),
    },
    {
      headers: { "Cache-Control": "no-cache, no-store, must-revalidate" },
    },
  );
}
