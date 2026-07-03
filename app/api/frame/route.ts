const DEFAULT_UID =
  "0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6";

function normalizeUid(input: FormDataEntryValue | null): string {
  if (typeof input !== "string") return DEFAULT_UID;
  const trimmed = input.trim();
  return trimmed.length > 0 ? trimmed : DEFAULT_UID;
}

export async function POST(request: Request) {
  let uid = DEFAULT_UID;

  try {
    const contentType = request.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
      const body = await request.json();
      uid = typeof body?.input === "string" ? body.input.trim() : DEFAULT_UID;
    } else {
      const formData = await request.formData();
      uid = normalizeUid(formData.get("input"));
    }
  } catch {
    uid = DEFAULT_UID;
  }

  return Response.json({
    status: "PENDING_SIGNATURE",
    verdict: "WITNESS_ONLY",
    uid,
    authority: false,
    truth_claim: false,
  });
}

export async function GET() {
  return Response.json({
    status: "FRAME_ROUTE_READY",
    verdict: "WITNESS_ONLY",
    authority: false,
    truth_claim: false,
  });
}
