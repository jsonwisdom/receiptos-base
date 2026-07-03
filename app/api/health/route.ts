import { NextResponse } from "next/server";
import { existsSync } from "fs";
import { join } from "path";

interface HealthResponse {
  status: "ok";
  service: string;
  court_state: string;
  authority: false;
  truth_claim: false;
  signature_files_checked: boolean;
  signature_files_exist: boolean;
  timestamp: string;
}

export async function GET(): Promise<NextResponse<HealthResponse>> {
  const projectRoot = process.cwd();
  const identityBindingPath = join(
    projectRoot,
    "provenance",
    "identity-binding",
    "jaywisdom-identity-binding.txt",
  );
  const signaturePath = join(
    projectRoot,
    "provenance",
    "identity-binding",
    "jaywisdom-identity-binding.sig",
  );

  const signatureFilesExist =
    existsSync(identityBindingPath) && existsSync(signaturePath);

  return NextResponse.json(
    {
      status: "ok",
      service: "receiptos-frame",
      court_state: "FRAME_MVP_AWAITING_DEPLOYMENT_RECEIPT",
      authority: false,
      truth_claim: false,
      signature_files_checked: true,
      signature_files_exist: signatureFilesExist,
      timestamp: new Date().toISOString(),
    },
    {
      headers: { "Cache-Control": "no-cache, no-store, must-revalidate" },
    },
  );
}
