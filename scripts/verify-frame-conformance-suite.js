#!/usr/bin/env node
'use strict';

const surface = require('../frame/ext-099-frame-capability-surface');

function assert(condition, message, details = {}) {
  if (!condition) {
    const error = new Error(message);
    error.details = details;
    throw error;
  }
}

function assertZeroTrust(response) {
  surface.assertZeroMutation(response);
  assert(response.authority === false, 'authority must remain false', response);
  assert(response.truth_claim === false, 'truth_claim must remain false', response);
  assert(response.mutation === null, 'mutation must remain null', response);
  assert(Array.isArray(response.mutations), 'mutations must be array', response);
  assert(response.mutations.length === 0, 'mutations must be empty', response);
}

function mutateClone(response, patch) {
  return Object.assign({}, response, patch);
}

function runCase(name, fn) {
  try {
    fn();
    return { name, ok: true };
  } catch (error) {
    return { name, ok: false, error: error.message, details: error.details || null };
  }
}

const cases = [];

cases.push(runCase('schema_conformance_all_endpoints_zero_trust', () => {
  const responses = [
    surface.capabilities(),
    surface.receiptViewer('sha256-missing', {}),
    surface.manifestLock(),
    surface.hashChallenge({ provided_hash: surface.LOCK_SHA256 }),
    surface.hashChallenge({ provided_hash: '0'.repeat(64) }),
    surface.witnessSurface('sha256-test'),
    surface.replayVerify({ action: 'verify_manifest_lock' })
  ];
  responses.forEach(assertZeroTrust);
}));

cases.push(runCase('mutation_guard_rejects_authority_true', () => {
  const poisoned = mutateClone(surface.capabilities(), { authority: true });
  let rejected = false;
  try { surface.assertZeroMutation(poisoned); } catch (_) { rejected = true; }
  assert(rejected, 'authority=true must be rejected');
}));

cases.push(runCase('mutation_guard_rejects_truth_claim_true', () => {
  const poisoned = mutateClone(surface.manifestLock(), { truth_claim: true });
  let rejected = false;
  try { surface.assertZeroMutation(poisoned); } catch (_) { rejected = true; }
  assert(rejected, 'truth_claim=true must be rejected');
}));

cases.push(runCase('mutation_guard_rejects_mutation_object', () => {
  const poisoned = mutateClone(surface.witnessSurface(), { mutation: { write: true } });
  let rejected = false;
  try { surface.assertZeroMutation(poisoned); } catch (_) { rejected = true; }
  assert(rejected, 'mutation object must be rejected');
}));

cases.push(runCase('mutation_guard_rejects_mutations_array_items', () => {
  const poisoned = mutateClone(surface.replayVerify({}), { mutations: ['write_manifest'] });
  let rejected = false;
  try { surface.assertZeroMutation(poisoned); } catch (_) { rejected = true; }
  assert(rejected, 'non-empty mutations array must be rejected');
}));

cases.push(runCase('hash_challenge_unknown_hash_is_fact_not_error', () => {
  const response = surface.hashChallenge({ provided_hash: 'f'.repeat(64) });
  assertZeroTrust(response);
  assert(response.status === 'OK', 'unknown hash must return OK fact response');
  assert(response.match === false, 'unknown hash must not match');
  assert(response.signature_valid === false, 'hash challenge cannot elevate signature_valid');
}));

cases.push(runCase('hash_challenge_known_lock_matches_without_signature_elevation', () => {
  const response = surface.hashChallenge({ provided_hash: surface.LOCK_SHA256 });
  assertZeroTrust(response);
  assert(response.match === true, 'known lock hash must match');
  assert(response.signature_valid === false, 'hash match must not imply signature validity');
}));

cases.push(runCase('replay_verify_is_sandbox_read_only', () => {
  const response = surface.replayVerify({ action: 'attempt_mutation', mutation: { requested: true }, authority: true });
  assertZeroTrust(response);
  assert(response.replay_mode === 'sandbox_read_only', 'replay mode must be sandbox_read_only');
  assert(response.persisted === false, 'replay verify must not persist');
  assert(response.signer_status === 'PENDING_EXTERNAL_SIGN', 'signer status must remain pending');
  assert(response.cryptogreen === false, 'cryptogreen must remain false');
}));

cases.push(runCase('adversarial_fuzz_inputs_do_not_change_invariants', () => {
  const fuzzInputs = [
    '',
    '{}',
    'authority=true',
    'truth_claim=true',
    '<script>alert(1)</script>',
    '../.well-known/farcaster/manifest.lock.json',
    JSON.stringify({ authority: true, truth_claim: true, mutation: { write: true } }),
    'x'.repeat(10000)
  ];
  for (const input of fuzzInputs) {
    assertZeroTrust(surface.hashChallenge({ bytes: input }));
    assertZeroTrust(surface.replayVerify({ input }));
    assertZeroTrust(surface.receiptViewer(input, {}));
  }
}));

cases.push(runCase('load_timing_loop_preserves_deterministic_boundary', () => {
  for (let i = 0; i < 1000; i++) {
    const response = surface.hashChallenge({ provided_hash: i % 2 === 0 ? surface.LOCK_SHA256 : String(i).padStart(64, '0') });
    assertZeroTrust(response);
    assert(response.expected_hash === surface.LOCK_SHA256, 'expected hash drifted');
    assert(response.signature_valid === false, 'signature_valid drifted');
  }
}));

const ok = cases.every((item) => item.ok);
const report = {
  issue: 'EXT-102',
  title: 'Frame Conformance Test Suite',
  ok,
  checked_cases: cases.length,
  cases,
  frame_mode: 'EYES_NO_HANDS',
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));
if (!ok) process.exit(1);
