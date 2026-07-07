#!/usr/bin/env node
'use strict';

const registry = require('../frame/ext-104-authorized-signer-registry');

const attempts = [
  { signer_id: '0xa380552a27b0a5a2874ea7aa52cac09f542002e8', payload_hash: 'd3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce', signature_bytes: '0x00' },
  { signer_id: 'FID_123', payload_hash: '0'.repeat(64), signature_bytes: '0xabc' },
  { signer_id: null, payload_hash: null, signature_bytes: null }
];

const results = [];
let ok = true;

for (const input of attempts) {
  const response = registry.verifySignature(input);
  try {
    registry.assertSignerRegistryBoundary(response);
    if (response.status !== 'UNAUTHORIZED_SIGNER') throw new Error('empty registry must return UNAUTHORIZED_SIGNER');
    if (response.signer_authorized !== false) throw new Error('empty registry must authorize no signer');
    if (response.signature_valid !== false) throw new Error('empty registry must never validate signatures');
    if (response.verification_performed !== false) throw new Error('empty registry must not claim verification');
    if (response.reason !== 'signer_not_in_authorized_registry') throw new Error('wrong empty-state reason');
    results.push({ signer_id: input.signer_id, ok: true, status: response.status, reason: response.reason });
  } catch (error) {
    ok = false;
    results.push({ signer_id: input.signer_id, ok: false, error: error.message, response });
  }
}

const report = {
  issue: 'EXT-104-tests',
  title: 'Authorized Signer Empty-State Regression Test',
  ok,
  expected_status: 'UNAUTHORIZED_SIGNER',
  expected_reason: 'signer_not_in_authorized_registry',
  results,
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));
if (!ok) process.exit(1);
