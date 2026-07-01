#!/usr/bin/env node
'use strict';

const surface = require('../frame/ext-106-signature-verification-surface');

const AUTHORIZED_SIGNER = '0xa380552a27b0a5a2874ea7aa52cac09f542002e8';

function assert(condition, message, details = {}) {
  if (!condition) {
    const error = new Error(message);
    error.details = details;
    throw error;
  }
}

const cases = [
  ['missing-payload', surface.verifySignatureSurface({ signature_bytes: 'sig_label', signer_address: AUTHORIZED_SIGNER, scheme: 'secp256k1' }), 'missing_payload'],
  ['missing-signature', surface.verifySignatureSurface({ payload_jcs: '{"ok":true}', signer_address: AUTHORIZED_SIGNER, scheme: 'secp256k1' }), 'missing_signature'],
  ['unsupported-scheme', surface.verifySignatureSurface({ payload_jcs: '{"ok":true}', signature_bytes: 'sig_label', signer_address: AUTHORIZED_SIGNER, scheme: 'ed25519' }), 'unsupported_scheme'],
  ['unauthorized-signer', surface.verifySignatureSurface({ payload_jcs: '{"ok":true}', signature_bytes: 'sig_label', signer_address: 'unauthorized_signer_label', scheme: 'secp256k1' }), 'signer_not_authorized'],
  ['authorized-awaiting-verifier', surface.verifySignatureSurface({ payload_jcs: '{"ok":true}', signature_bytes: 'sig_label', signer_address: AUTHORIZED_SIGNER, scheme: 'secp256k1' }), 'verifier_not_connected']
];

let ok = true;
const results = [];

for (const [name, response, expectedReason] of cases) {
  try {
    surface.assertSignatureBoundary(response);
    assert(response.reason === expectedReason, 'unexpected reason', { response, expectedReason });
    assert(response.signature_valid === false, 'negative/stub case must not validate signature', response);
    assert(response.cryptogreen === false, 'negative/stub case must not emit cryptogreen', response);
    results.push({ name, ok: true, reason: response.reason });
  } catch (error) {
    ok = false;
    results.push({ name, ok: false, error: error.message, details: error.details || null });
  }
}

const report = {
  issue: 'EXT-106',
  title: 'Signature Verification Surface Negative/Staged Tests',
  ok,
  checked_cases: results.length,
  results,
  cryptogreen: false,
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));
if (!ok) process.exit(1);
