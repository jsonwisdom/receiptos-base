#!/usr/bin/env node
'use strict';

const registry = require('../frame/ext-104-authorized-signer-registry');

const SEED_SIGNER = '0xa380552a27b0a5a2874ea7aa52cac09f542002e8';

function assert(condition, message, details = {}) {
  if (!condition) {
    const error = new Error(message);
    error.details = details;
    throw error;
  }
}

const cases = [
  ['authorizedSigners', registry.authorizedSigners()],
  ['verifySignature-seed-present', registry.verifySignature({ signer_id: SEED_SIGNER, payload_hash: 'd3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce', signature_bytes: '0x00' })],
  ['verifySignature-unauthorized', registry.verifySignature({ signer_id: 'FID_123', payload_hash: '0'.repeat(64), signature_bytes: '0xabc' })],
  ['verifySignature-missing', registry.verifySignature({})],
  ['verifyMultisig-pending', registry.verifyMultisig({ signer_ids: [SEED_SIGNER, 'FID_2'], payload_hash: '0'.repeat(64), signatures: ['0x1', '0x2'] })]
];

let ok = true;
const results = [];

for (const [name, response] of cases) {
  try {
    registry.assertSignerRegistryBoundary(response);
    assert(response.frame_mode === 'EYES_NO_HANDS', 'frame mode drift', response);
    assert(response.registry_status === 'CANONICAL_FROM_EXT_104_SEED', 'registry status drift', response);
    if (response.endpoint === 'authorized_signers') {
      assert(Array.isArray(response.authorized_signers), 'authorized_signers must be array', response);
      assert(response.authorized_signers.includes(SEED_SIGNER), 'canonical registry must include seed signer', response);
      assert(response.master_key === null, 'master_key must be null', response);
      assert(response.signer_scheme === 'secp256k1', 'signer scheme must be secp256k1', response);
    }
    if (response.endpoint === 'verify_signature' && name === 'verifySignature-seed-present') {
      assert(response.signer_authorized === true, 'seed signer must be recognized as present', response);
      assert(response.signature_valid === false, 'membership alone must not validate signature', response);
      assert(response.verification_performed === false, 'stub must not claim cryptographic verification', response);
      assert(response.reason === 'real_signature_verifier_not_connected', 'seed signer must await real verifier', response);
    }
    if (response.endpoint === 'verify_signature' && name !== 'verifySignature-seed-present') {
      assert(response.signer_authorized === false, 'non-seed signer must be unauthorized', response);
      assert(response.signature_valid === false, 'unauthorized signer must never validate signature', response);
      assert(response.verification_performed === false, 'verification must not claim execution', response);
    }
    if (response.endpoint === 'verify_multisig') {
      assert(response.threshold === null, 'pending threshold must be null', response);
      assert(response.threshold_satisfied === false, 'threshold cannot be satisfied while pending', response);
      assert(response.multisig_valid === false, 'multisig cannot validate while pending', response);
    }
    results.push({ name, endpoint: response.endpoint, ok: true });
  } catch (error) {
    ok = false;
    results.push({ name, endpoint: response && response.endpoint, ok: false, error: error.message, details: error.details || null });
  }
}

const report = {
  issue: 'EXT-105',
  title: 'Canonical Authorized Signer Registry Verification',
  ok,
  checked_cases: results.length,
  results,
  frame_mode: 'EYES_NO_HANDS',
  registry_status: 'CANONICAL_FROM_EXT_104_SEED',
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));
if (!ok) process.exit(1);
