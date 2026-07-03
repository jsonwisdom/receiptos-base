export async function POST(request: Request) {
  let body: Record<string, unknown> = {};

  try {
    body = await request.json();
  } catch {
    body = {};
  }

  return Response.json({
    status: "PENDING_VERIFIER_IMPLEMENTATION",
    verdict: "WITNESS_ONLY",
    accepted_fields: ["uid", "signature", "signer"],
    received: {
      uid_present: typeof body.uid === "string" && body.uid.length > 0,
      signature_present:
        typeof body.signature === "string" && body.signature.length > 0,
      signer_present: typeof body.signer === "string" && body.signer.length > 0,
    },
    authority: false,
    truth_claim: false,
  });
}

export async function GET() {
  return Response.json({
    status: "BIND_STUB_READY",
    verdict: "WITNESS_ONLY",
    authority: false,
    truth_claim: false,
  });
}
