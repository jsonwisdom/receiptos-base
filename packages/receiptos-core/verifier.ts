import { canonicalize } from './canonical.ts';

export interface VerifyInput {
  payload: any;
  // strict determinism rules
}

export async function verifyL1(input: VerifyInput) {
  const canon = canonicalize(input.payload);
  // deterministic hash, no Date.now
  const eventHash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(canon));
  const receiptId = Array.from(new Uint8Array(eventHash)).map(b => b.toString(16).padStart(2,'0')).join('').slice(0,32);
  return {
    receipt_id: receiptId,
    event_hash: Array.from(new Uint8Array(eventHash)).map(b => b.toString(16).padStart(2,'0')).join(''),
    authority: false,
    truth_claim: false,
    observed: 'deterministic-replay',
    verified: 'L1-portal-match'
  };
}