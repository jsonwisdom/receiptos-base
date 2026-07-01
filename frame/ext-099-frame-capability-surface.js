'use strict';

const crypto = require('crypto');

const LOCK_SHA256 = 'd3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce';
const MANIFEST_ID = 'jaywisdom';
const PUBLIC_WITNESS_URL = 'https://farcaster.xyz/cmptrwsdm';
const DOMAIN_BINDING = 'https://cmptrwsdm.com/.well-known/farcaster/manifest.json';
const FRAME_ID = 'jaywisdom-replay-frame';

function sha256(input) {
  return crypto.createHash('sha256').update(String(input), 'utf8').digest('hex');
}

function baseReceipt(endpoint, status) {
  return {
    endpoint,
    status,
    frame_id: FRAME_ID,
    authority: false,
    truth_claim: false,
    mutation: null,
    mutations: []
  };
}

function capabilities() {
  return {
    ...baseReceipt('frame_capabilities', 'OK'),
    methods: [
      'GET /api/frame/capabilities',
      'GET /api/frame/receipt/:receipt_id',
      'GET /api/frame/manifest-lock',
      'POST /api/frame/hash-challenge',
      'GET /api/frame/witness-surface',
      'POST /api/frame/replay-verify'
    ],
    actions: [
      'VIEW_RECEIPT',
      'INSPECT_LOCK',
      'CHALLENGE_HASH',
      'OPEN_WITNESS_SURFACE',
      'SUBMIT_EVIDENCE_CANDIDATE',
      'REPLAY_VERIFY'
    ]
  };
}

function receiptViewer(receiptId, receiptIndex = {}) {
  const receipt = receiptIndex[receiptId] || null;
  return {
    ...baseReceipt('receipt_viewer', receipt ? 'FOUND' : 'NOT_FOUND'),
    receipt_id: receiptId,
    receipt_hash: receipt ? sha256(JSON.stringify(receipt)) : null,
    receipt
  };
}

function manifestLock() {
  return {
    ...baseReceipt('manifest_lock_inspector', 'OK'),
    manifest_id: MANIFEST_ID,
    manifest_path: '.well-known/farcaster/manifest.jcs',
    lock_path: '.well-known/farcaster/manifest.lock.json',
    lock_sha256: LOCK_SHA256,
    canonicalization: 'RFC8785'
  };
}

function hashChallenge({ provided_hash = null, bytes = null } = {}) {
  const computed_hash = bytes !== null ? sha256(bytes) : provided_hash;
  return {
    ...baseReceipt('hash_challenger', 'OK'),
    challenge_type: bytes !== null ? 'uploaded_bytes' : 'provided_hash',
    computed_hash,
    expected_hash: LOCK_SHA256,
    match: computed_hash === LOCK_SHA256,
    signature_valid: false
  };
}

function witnessSurface(receiptId = null) {
  return {
    ...baseReceipt('witness_surface', 'OK'),
    receipt_id: receiptId,
    public_witness_url: PUBLIC_WITNESS_URL,
    role: 'public_identity_projection',
    canonical_manifest: false,
    source_of_truth: false,
    domain_binding: DOMAIN_BINDING
  };
}

function replayVerify(payload = {}) {
  const request_hash = sha256(JSON.stringify(payload));
  const response = {
    ...baseReceipt('replay_verify', 'OK'),
    replay_mode: 'sandbox_read_only',
    persisted: false,
    request_hash,
    lock_sha256: LOCK_SHA256,
    signer_status: 'PENDING_EXTERNAL_SIGN',
    cryptogreen: false
  };
  return {
    ...response,
    response_hash: sha256(JSON.stringify(response))
  };
}

function assertZeroMutation(response) {
  if (response.authority !== false) throw new Error('authority breach');
  if (response.truth_claim !== false) throw new Error('truth_claim breach');
  if (response.mutation !== null) throw new Error('mutation breach');
  if (!Array.isArray(response.mutations) || response.mutations.length !== 0) {
    throw new Error('mutations breach');
  }
  return true;
}

module.exports = {
  LOCK_SHA256,
  MANIFEST_ID,
  PUBLIC_WITNESS_URL,
  capabilities,
  receiptViewer,
  manifestLock,
  hashChallenge,
  witnessSurface,
  replayVerify,
  assertZeroMutation
};
