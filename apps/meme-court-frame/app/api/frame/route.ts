import { NextRequest } from 'next/server';

const UID = '0x7ed8784f88dc16d9720dfd0a6d45a21b02f8d5d128eaf529ffeab0002e9c0af6';
const SCHEMA_UID = '0x45af9479e460c501c71e09679936d9dc20eb3a37f0cc0586d8d6937d9e1ec80d';
const COMMIT = '2c7b4aa384265596a2c55df7b877e6874896573b';
const STATEMENT_SHA256 = '6928aeed37e3d86cf1952a42dfc82b2de214b347284c62a24534baf036e03c5e';

const state = 'PENDING_SIGNATURE' as const;

const payload = {
  name: 'Meme Court Receipt Verifier',
  status: state,
  verdict: 'WITNESS_ONLY',
  message: 'On-chain statement-hash witness exists. Wallet signature bundle still pending.',
  doctrine: 'No receipt = no authority.',
  uid: UID,
  schema_uid: SCHEMA_UID,
  repository: 'jsonwisdom/receiptos-base',
  commit: COMMIT,
  statement_sha256: STATEMENT_SHA256,
  authority: false,
  truth_claim: false,
  next_required_evidence: [
    'provenance/identity-binding/jaywisdom-identity-binding.sig',
    'provenance/identity-binding/SHA256SUMS'
  ]
};

export async function GET() {
  return Response.json(payload, {
    status: 200,
    headers: {
      'Cache-Control': 'no-store'
    }
  });
}

export async function POST(_req: NextRequest) {
  return Response.json(payload, {
    status: 200,
    headers: {
      'Cache-Control': 'no-store'
    }
  });
}
