'use strict';

const crypto = require('crypto');

const LOCK_SHA256 = 'd3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce';
const PUBLIC_WITNESS_URL = 'https://farcaster.xyz/cmptrwsdm';
const DOMAIN_BINDING = 'https://cmptrwsdm.com/.well-known/farcaster/manifest.json';

function sha256(input) {
  return crypto.createHash('sha256').update(String(input), 'utf8').digest('hex');
}

function baseAudit(endpoint, status) {
  return {
    endpoint,
    status,
    audit_posture: 'PUBLIC_VERIFIABLE',
    security: [],
    frame_mode: 'EYES_NO_HANDS',
    authority: false,
    truth_claim: false,
    mutation: null,
    mutations: []
  };
}

function auditRoot() {
  return {
    ...baseAudit('audit_root', 'PENDING_ANCHOR'),
    merkle_root: null,
    anchor_status: 'PENDING_ANCHOR',
    anchor_chain: null,
    anchor_reference: null,
    fabricated_anchor: false
  };
}

function auditManifestLock() {
  return {
    ...baseAudit('audit_manifest_lock', 'OK'),
    manifest_id: 'jaywisdom',
    lock_sha256: LOCK_SHA256,
    canonical_manifest: '.well-known/farcaster/manifest.jcs',
    lock_path: '.well-known/farcaster/manifest.lock.json',
    domain_binding: DOMAIN_BINDING,
    public_witness_url: PUBLIC_WITNESS_URL
  };
}

function auditBundle() {
  return {
    ...baseAudit('audit_bundle', 'PENDING_BUNDLE'),
    bundle_path: null,
    bundle_sha256: null,
    bundle_status: 'PENDING_BUNDLE',
    fabricated_bundle: false
  };
}

function challengeReplay(payload = {}) {
  const request_hash = sha256(JSON.stringify(payload));
  const response = {
    ...baseAudit('challenge_replay', 'OK'),
    replay_mode: 'sandbox_read_only',
    persisted: false,
    request_hash,
    lock_sha256: LOCK_SHA256,
    match: payload && payload.expected_hash ? payload.expected_hash === LOCK_SHA256 : false,
    creates_receipt: false,
    cryptogreen: false
  };
  return {
    ...response,
    response_hash: sha256(JSON.stringify(response))
  };
}

function assertPublicAuditBoundary(response) {
  if (response.authority !== false) throw new Error('authority breach');
  if (response.truth_claim !== false) throw new Error('truth_claim breach');
  if (response.mutation !== null) throw new Error('mutation breach');
  if (!Array.isArray(response.mutations) || response.mutations.length !== 0) throw new Error('mutations breach');
  if (!Array.isArray(response.security) || response.security.length !== 0) throw new Error('public security breach');
  return true;
}

module.exports = {
  LOCK_SHA256,
  auditRoot,
  auditManifestLock,
  auditBundle,
  challengeReplay,
  assertPublicAuditBoundary
};
