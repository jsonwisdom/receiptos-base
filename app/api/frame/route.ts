import { NextRequest, NextResponse } from "next/server";

type FrameAction = "post" | "post_redirect";

interface FrameButton {
  label: string;
  action: FrameAction;
  target?: string;
}

interface FrameResponse {
  status: string;
  verdict: "WITNESS_ONLY";
  authority: false;
  truth_claim: false;
  message: string;
  uid?: string;
  invalid_input?: boolean;
  image: string;
  buttons: FrameButton[];
  input?: { text: string };
  post_url: string;
}

const KNOWN_EAS_UID =
  "0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6";
const BASE_URL = process.env.NEXT_PUBLIC_URL || "http://localhost:3000";
const WITNESS_MESSAGE =
  "On-chain statement-hash witness exists. Wallet signature bundle still pending.";

function buildResponse(overrides: Partial<FrameResponse> = {}): FrameResponse {
  return {
    status: "PENDING_SIGNATURE",
    verdict: "WITNESS_ONLY",
    authority: false,
    truth_claim: false,
    message: WITNESS_MESSAGE,
    image: `${BASE_URL}/og/witness-only.svg`,
    buttons: [
      { label: "Submit Witness", action: "post" },
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
  return NextResponse.json(buildResponse(), {
    headers: { "Cache-Control": "no-cache, no-store, must-revalidate" },
  });
}

export async function POST(
  request: NextRequest,
): Promise<NextResponse<FrameResponse>> {
  try {
    const inputText = await readInputText(request);
    const inputMatches = inputText === KNOWN_EAS_UID;
    const invalidInput = inputText.length > 0 && !inputMatches;

    return NextResponse.json(
      buildResponse({
        message: inputMatches
          ? "Witness recorded. Signature bundle verification pending."
          : "Invalid witness input. Please provide the known EAS UID.",
        uid: inputMatches ? inputText : undefined,
        invalid_input: invalidInput,
        buttons: [
          { label: inputMatches ? "Recorded" : "Invalid", action: "post" },
          { label: "Try Again", action: "post" },
        ],
      }),
      {
        status: 200,
        headers: { "Cache-Control": "no-cache, no-store, must-revalidate" },
      },
    );
  } catch {
    return NextResponse.json(
      buildResponse({
        message: "Error processing witness input.",
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
