#!/usr/bin/env node
'use strict';

const registry = require('../frame/ext-104-authorized-signer-registry');

const attempts = [
  { signer_id: 'seed_signer_label' },
  { signer_id: 'unknown_signer_label' },
  { signer_id: null }
];

let ok = true;
const results = [];

for (const input of attempts) {
  const response = {
    endpoint: 'empty_registry_denial_fixture',
    status: 'UNAUTHORIZED_SIGNER',
    frame_mode: 'EYES_NO_HANDS',
    registry_status: 'EMPTY_SET_FIXTURE',
    signer_id: input.signer_id,
    signer_authorized: false,
    signature_valid: false,
    verification_performed: false,
    reason: 'no_authorized_signers_loaded',
    authority: false,
    truth_claim: false,
    mutation: null,
    mutations: []
  };

  try {
    registry.assertSignerRegistryBoundary(response);
    if (response.signer_authorized !== false) throw new Error('empty set authorized a signer');
    if (response.signature_valid !== false) throw new Error('empty set validated a signature');
    if (response.reason !== 'no_authorized_signers_loaded') throw new Error('wrong empty-set reason');
    results.push({ signer_id: input.signer_id, ok: true });
  } catch (error) {
    ok = false;
    results.push({ signer_id: input.signer_id, ok: false, error: error.message });
  }
}

const report = {
  issue: 'EXT-104-tests',
  title: 'Empty Registry Denial Fixture',
  ok,
  results,
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));
if (!ok) process.exit(1);
