#!/usr/bin/env node
'use strict';

const surface = require('../frame/ext-099-frame-capability-surface');

const cases = [
  ['capabilities', surface.capabilities()],
  ['receiptViewer-not-found', surface.receiptViewer('sha256-missing', {})],
  ['manifestLock', surface.manifestLock()],
  ['hashChallenge-known-lock', surface.hashChallenge({ provided_hash: surface.LOCK_SHA256 })],
  ['hashChallenge-unknown', surface.hashChallenge({ provided_hash: '0'.repeat(64) })],
  ['witnessSurface', surface.witnessSurface('sha256-test')],
  ['replayVerify', surface.replayVerify({ action: 'verify_manifest_lock' })]
];

let ok = true;
const results = [];

for (const [name, response] of cases) {
  try {
    surface.assertZeroMutation(response);
    results.push({ name, ok: true, endpoint: response.endpoint, authority: response.authority, truth_claim: response.truth_claim });
  } catch (error) {
    ok = false;
    results.push({ name, ok: false, error: error.message });
  }
}

const report = {
  issue: 'EXT-099',
  title: 'Frame Capability Surface Verification',
  ok,
  checked_cases: results.length,
  results,
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));

if (!ok) process.exit(1);
