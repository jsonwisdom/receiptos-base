'use strict';

const crypto = require('crypto');

function sha256(input) {
  return crypto.createHash('sha256').update(String(input), 'utf8').digest('hex');
}

const REGISTRY_STATUS = 'PENDING_REAL_SIGNER_REGISTRY';
const AUTHORIZED_SIGNERS = [];
const THRESHOLD = null;

function baseRegistry(endpoint, status) {
  return {
    endpoint,
    status,
    frame_mode: 'EYES_NO_HANDS',
    registry_status: REGISTRY_STATUS,
    authority: false,
    truth_claim: false,
    mutation: null,
    mutations: []
  };
}

function authorizedSigners() {
  return {
    ...baseRegistry('authorized_signers', 'PENDING_EMPTY_REGISTRY'),
    authorized_signers: AUTHORIZED_SIGNERS,
    registry_hash: sha256(JSON.stringify(AUTHORIZED_SIGNERS)),
    source_of_truth: 'canonical_registry_artifact_pending',
    master_key: null,
    threshold: THRESHOLD
  };
}

function verifySignature({ signer_id = null, payload_hash = null, signature_bytes = null } = {}) {
  const authorized = AUTHORIZED_SIGNERS.includes(signer_id);
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
  const authorizedSubmitted = signer_ids.filter((id) => AUTHORIZED_SIGNERS.includes(id));
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
  REGISTRY_STATUS,
  AUTHORIZED_SIGNERS,
  authorizedSigners,
  verifySignature,
  verifyMultisig,
  assertSignerRegistryBoundary
};
