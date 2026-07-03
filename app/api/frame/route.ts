import { NextRequest, NextResponse } from "next/server";

type FrameAction = "post" | "post_redirect";

interface FrameButton {
  label: string;
  action: FrameAction;
  target?: string;
}

interface WireReceipt {
  status?: string;
  integrity_standard?: string;
  verification_method?: string;
  magic?: string;
  authority?: boolean;
  truth_claim?: boolean;
  verdict?: string;
  reason?: string;
  etag?: string;
}

interface FrameResponse {
  status: string;
  verification_gate: "passed" | "pending";
  integrity_standard: "ROS-0006" | "UNKNOWN";
  verification_method?: string;
  verdict: "WITNESS_ONLY";
  authority: false;
  truth_claim: false;
  message: string;
  uid?: string;
  invalid_input?: boolean;
  wire_reason?: string;
  image: string;
  buttons: FrameButton[];
  input?: { text: string };
  post_url: string;
}

const KNOWN_EAS_UID =
  "0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6";
const BASE_URL = process.env.NEXT_PUBLIC_URL || "https://receiptos-base.vercel.app";
const REQUIRED_MAGIC = "0x1626ba7e";

function wireVerified(receipt: WireReceipt | null): boolean {
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

function buildResponse(
  receipt: WireReceipt | null,
  overrides: Partial<FrameResponse> = {},
): FrameResponse {
  const verified = wireVerified(receipt);

  return {
    status: verified ? "VERIFIED" : "PENDING",
    verification_gate: verified ? "passed" : "pending",
    integrity_standard:
      receipt?.integrity_standard === "ROS-0006" ? "ROS-0006" : "UNKNOWN",
    verification_method: receipt?.verification_method,
    verdict: "WITNESS_ONLY",
    authority: false,
    truth_claim: false,
    message: verified
      ? "VERIFIED: ROS-0006 Authorized Identity receipt accepted by Wire."
      : "PENDING: Wire has not satisfied the ROS-0006 verification gate.",
    wire_reason: receipt?.reason || "wire_unreachable_or_invalid",
    image: `${BASE_URL}/og/witness-only.svg`,
    buttons: [
      { label: verified ? "VERIFIED" : "PENDING", action: "post" },
      {
        label: "View Wire",
        action: "post_redirect",
        target: `${BASE_URL}/stream`,
      },
      {
        label: "View Docket #57",
        action: "post_redirect",
        target: "https://github.com/jsonwisdom/receiptos-base/issues/57",
      },
    ],
    input: { text: "Paste EAS UID or witness hash" },
    post_url: `${BASE_URL}/api/frame`,
    ...overrides,
  };
}

async function readInputText(request: NextRequest): Promise<string> {
  const contentType = request.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    const body = await request.json().catch(() => ({}));
    const farcasterInput = body?.untrustedData?.inputText;
    const directInput = body?.input;
    return String(farcasterInput || directInput || "").trim();
  }

  if (
    contentType.includes("multipart/form-data") ||
    contentType.includes("application/x-www-form-urlencoded")
  ) {
    const formData = await request.formData().catch(() => null);
    return String(formData?.get("input") || "").trim();
  }

  return "";
}

export async function GET(): Promise<NextResponse<FrameResponse>> {
  const receipt = await fetchWireReceipt();
  return NextResponse.json(buildResponse(receipt), {
    headers: { "Cache-Control": "no-cache, no-store, must-revalidate" },
  });
}

export async function POST(
  request: NextRequest,
): Promise<NextResponse<FrameResponse>> {
  try {
    const receipt = await fetchWireReceipt();
    const verified = wireVerified(receipt);
    const inputText = await readInputText(request);
    const inputMatches = inputText === KNOWN_EAS_UID;
    const invalidInput = inputText.length > 0 && !inputMatches;

    return NextResponse.json(
      buildResponse(receipt, {
        status: verified && inputMatches ? "VERIFIED" : verified ? "VERIFIED" : "PENDING",
        message: verified
          ? inputMatches
            ? "VERIFIED: Wire accepted ROS-0006 and witness UID matched."
            : "VERIFIED: Wire accepted ROS-0006 Authorized Identity receipt."
          : "PENDING: Wire has not satisfied the ROS-0006 verification gate.",
        uid: inputMatches ? inputText : undefined,
        invalid_input: invalidInput,
        buttons: [
          { label: verified ? "VERIFIED" : "PENDING", action: "post" },
          { label: inputMatches ? "UID MATCHED" : "Submit UID", action: "post" },
          {
            label: "View Wire",
            action: "post_redirect",
            target: `${BASE_URL}/stream`,
          },
        ],
      }),
      {
        status: 200,
        headers: { "Cache-Control": "no-cache, no-store, must-revalidate" },
      },
    );
  } catch {
    return NextResponse.json(
      buildResponse(null, {
        message: "PENDING: Frame failed closed while reading Wire.",
        invalid_input: true,
        buttons: [{ label: "Retry", action: "post" }],
      }),
      {
        status: 400,
        headers: { "Cache-Control": "no-cache, no-store, must-revalidate" },
      },
    );
  }
}
