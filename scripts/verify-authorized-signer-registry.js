#!/usr/bin/env node
'use strict';

const registry = require('../frame/ext-104-authorized-signer-registry');

function assert(condition, message, details = {}) {
  if (!condition) {
    const error = new Error(message);
    error.details = details;
    throw error;
  }
}

const cases = [
  ['authorizedSigners', registry.authorizedSigners()],
  ['verifySignature-unauthorized', registry.verifySignature({ signer_id: 'FID_123', payload_hash: '0'.repeat(64), signature_bytes: '0xabc' })],
  ['verifySignature-missing', registry.verifySignature({})],
  ['verifyMultisig-pending', registry.verifyMultisig({ signer_ids: ['FID_1', 'FID_2'], payload_hash: '0'.repeat(64), signatures: ['0x1', '0x2'] })]
];

let ok = true;
const results = [];

for (const [name, response] of cases) {
  try {
    registry.assertSignerRegistryBoundary(response);
    assert(response.frame_mode === 'EYES_NO_HANDS', 'frame mode drift', response);
    assert(response.registry_status === 'PENDING_REAL_SIGNER_REGISTRY', 'registry status drift', response);
    if (response.endpoint === 'authorized_signers') {
      assert(Array.isArray(response.authorized_signers), 'authorized_signers must be array', response);
      assert(response.authorized_signers.length === 0, 'pending registry must remain empty', response);
      assert(response.master_key === null, 'master_key must be null', response);
    }
    if (response.endpoint === 'verify_signature') {
      assert(response.signer_authorized === false, 'pending registry must authorize no signer', response);
      assert(response.signature_valid === false, 'signature must not validate without real registry/verifier', response);
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
  issue: 'EXT-104',
  title: 'Authorized Signer Registry Verification',
  ok,
  checked_cases: results.length,
  results,
  frame_mode: 'EYES_NO_HANDS',
  registry_status: 'PENDING_REAL_SIGNER_REGISTRY',
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));
if (!ok) process.exit(1);
