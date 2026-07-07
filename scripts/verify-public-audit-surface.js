#!/usr/bin/env node
'use strict';

const audit = require('../frame/ext-103-public-audit-surface');

function assert(condition, message, details = {}) {
  if (!condition) {
    const error = new Error(message);
    error.details = details;
    throw error;
  }
}

const cases = [
  ['auditRoot', audit.auditRoot()],
  ['auditManifestLock', audit.auditManifestLock()],
  ['auditBundle', audit.auditBundle()],
  ['challengeReplay-match', audit.challengeReplay({ expected_hash: audit.LOCK_SHA256 })],
  ['challengeReplay-mismatch', audit.challengeReplay({ expected_hash: '0'.repeat(64) })]
];

const results = [];
let ok = true;

for (const [name, response] of cases) {
  try {
    audit.assertPublicAuditBoundary(response);
    assert(response.frame_mode === 'EYES_NO_HANDS', 'frame_mode drift', response);
    assert(response.audit_posture === 'PUBLIC_VERIFIABLE', 'audit posture drift', response);
    if (response.endpoint === 'audit_root') {
      assert(response.anchor_status === 'PENDING_ANCHOR', 'pending root must not claim anchor');
      assert(response.merkle_root === null, 'pending root must not fabricate merkle root');
      assert(response.fabricated_anchor === false, 'fabricated anchor flag must be false');
    }
    if (response.endpoint === 'audit_bundle') {
      assert(response.bundle_status === 'PENDING_BUNDLE', 'pending bundle must not claim archive');
      assert(response.bundle_sha256 === null, 'pending bundle must not fabricate bundle hash');
      assert(response.fabricated_bundle === false, 'fabricated bundle flag must be false');
    }
    if (response.endpoint === 'challenge_replay') {
      assert(response.persisted === false, 'challenge replay must not persist');
      assert(response.creates_receipt === false, 'challenge replay must not create receipt');
      assert(response.cryptogreen === false, 'challenge replay must not emit cryptogreen');
    }
    results.push({ name, endpoint: response.endpoint, ok: true });
  } catch (error) {
    ok = false;
    results.push({ name, endpoint: response && response.endpoint, ok: false, error: error.message, details: error.details || null });
  }
}

const report = {
  issue: 'EXT-103',
  title: 'Public Audit Surface Verification',
  ok,
  checked_cases: results.length,
  results,
  audit_posture: 'PUBLIC_VERIFIABLE',
  frame_mode: 'EYES_NO_HANDS',
  authority: false,
  truth_claim: false,
  mutation: null,
  mutations: []
};

console.log(JSON.stringify(report, null, 2));
if (!ok) process.exit(1);
