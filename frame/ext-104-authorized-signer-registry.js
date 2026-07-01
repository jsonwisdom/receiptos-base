'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

function sha256(input) {
  return crypto.createHash('sha256').update(String(input), 'utf8').digest('hex');
}

const SEED_PATH = path.join(__dirname, '..', 'receipts', 'ext-104-authorized-signer-registry.seed.json');
const THRESHOLD = null;

function loadSeedRegistry() {
  const raw = fs.readFileSync(SEED_PATH, 'utf8');
  const seed = JSON.parse(raw);
  return {
    registry_status: 'CANONICAL_FROM_EXT_104_SEED',
    authorized_signers: Array.isArray(seed.authorized_signers) ? seed.authorized_signers : [],
    signer_scheme: seed.signer_scheme || null,
    seed_hash: sha256(raw),
    source_of_truth: 'receipts/ext-104-authorized-signer-registry.seed.json'
  };
}

function currentRegistry() {
  return loadSeedRegistry();
}

function baseRegistry(endpoint, status) {
  const registry = currentRegistry();
  return {
    endpoint,
    status,
    frame_mode: 'EYES_NO_HANDS',
    registry_status: registry.registry_status,
    registry_source: registry.source_of_truth,
    registry_hash: registry.seed_hash,
    authority: false,
    truth_claim: false,
    mutation: null,
    mutations: []
  };
}

function authorizedSigners() {
  const registry = currentRegistry();
  return {
    ...baseRegistry('authorized_signers', 'CANONICAL_REGISTRY_LOADED'),
    authorized_signers: registry.authorized_signers,
    signer_scheme: registry.signer_scheme,
    source_of_truth: registry.source_of_truth,
    master_key: null,
    threshold: THRESHOLD
  };
}

function verifySignature({ signer_id = null, payload_hash = null, signature_bytes = null } = {}) {
  const registry = currentRegistry();
  const normalizedSigner = typeof signer_id === 'string' ? signer_id.toLowerCase() : signer_id;
  const authorized = registry.authorized_signers.map((id) => String(id).toLowerCase()).includes(normalizedSigner);
  return {
    ...baseRegistry('verify_signature', authorized ? 'SIGNER_PRESENT_SIGNATURE_UNVERIFIED' : 'UNAUTHORIZED_SIGNER'),
    signer_id,
    payload_hash,
    signature_bytes_present: Boolean(signature_bytes),
    signer_authorized: authorized,
    signature_valid: false,
    verification_performed: false,
    reason: authorized ? 'real_signature_verifier_not_connected' : 'signer_not_in_authorized_registry'
  };
}

function verifyMultisig({ signer_ids = [], payload_hash = null, signatures = [] } = {}) {
  const registry = currentRegistry();
  const authorizedSet = new Set(registry.authorized_signers.map((id) => String(id).toLowerCase()));
  const authorizedSubmitted = signer_ids.filter((id) => authorizedSet.has(String(id).toLowerCase()));
  const thresholdSatisfied = THRESHOLD !== null && authorizedSubmitted.length >= THRESHOLD;
  return {
    ...baseRegistry('verify_multisig', 'PENDING_THRESHOLD_REGISTRY'),
    signer_ids,
    payload_hash,
    signatures_count: Array.isArray(signatures) ? signatures.length : 0,
    authorized_submitted_count: authorizedSubmitted.length,
    threshold: THRESHOLD,
    threshold_satisfied: thresholdSatisfied,
    multisig_valid: false,
    verification_performed: false
  };
}

function assertSignerRegistryBoundary(response) {
  if (response.authority !== false) throw new Error('authority breach');
  if (response.truth_claim !== false) throw new Error('truth_claim breach');
  if (response.mutation !== null) throw new Error('mutation breach');
  if (!Array.isArray(response.mutations) || response.mutations.length !== 0) throw new Error('mutations breach');
  if (response.master_key !== undefined && response.master_key !== null) throw new Error('master key breach');
  return true;
}

module.exports = {
  SEED_PATH,
  THRESHOLD,
  loadSeedRegistry,
  currentRegistry,
  authorizedSigners,
  verifySignature,
  verifyMultisig,
  assertSignerRegistryBoundary
};
