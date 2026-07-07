import { canonicalize } from 'json-canonicalize';
import { createHash } from 'node:crypto';
import type { ReplayContext, ReplayResult } from './types';

function sha256Hex(value: string): string {
  return createHash('sha256').update(value, 'utf8').digest('hex');
}

function canonicalHash(value: unknown): string {
  const canonical = canonicalize(value);
  if (typeof canonical !== 'string') {
    throw new Error('canonicalization_failed');
  }
  return sha256Hex(canonical);
}

function assertAuthorityFalse(ctx: ReplayContext): void {
  if (ctx.initialState.authority !== false) {
    throw new Error('initial_state_authority_not_false');
  }

  if (ctx.initialState.noFakeGreen !== true) {
    throw new Error('initial_state_no_fake_green_not_true');
  }

  for (const event of ctx.events) {
    if (event.authority !== false) {
      throw new Error(`event_authority_not_false:${event.uid}`);
    }
  }
}

export async function replay(ctx: ReplayContext): Promise<ReplayResult> {
  assertAuthorityFalse(ctx);

  const stateRoot = canonicalHash({
    initialState: ctx.initialState,
    events: ctx.events.map((event) => ({
      uid: event.uid,
      schemaUid: event.schemaUid,
      txHash: event.txHash ?? null,
      eventHash: event.eventHash,
      payload: event.payload,
      authority: event.authority,
    })),
    strategy: ctx.strategy,
    invariants: ctx.invariants,
  });

  return {
    stateRoot,
    eventCount: ctx.events.length,
    strategy: ctx.strategy,
    authority: false,
    noFakeGreen: true,
    verifiedReplay: false,
    invariantCount: ctx.invariants.length,
  };
}
