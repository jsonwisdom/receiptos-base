'use strict';

const crypto = require('crypto');
const registry = require('./ext-104-authorized-signer-registry');

function sha256(input) {
  return crypto.createHash('sha256').update(String(input), 'utf8').digest('hex');
}

function baseResponse(reason) {
  return {
    endpoint: 'verify_signature',
    reason,
    frame_mode: 'EYES_NO_HANDS',
    authority: false,
    truth_claim: false,
    mutation: null,
    mutations: []
  };
}

function verifySignatureSurface({ payload_jcs = null, signature_bytes = null, signer_address = null, scheme = null } = {}) {
  const registryState = registry.authorizedSigners();
  const signerSet = new Set((registryState.authorized_signers || []).map((item) => String(item).toLowerCase()));
  const normalizedSigner = signer_address ? String(signer_address).toLowerCase() : null;

  if (!payload_jcs) {
    return {
      ...baseResponse('missing_payload'),
      signature_valid: false,
      cryptogreen: false,
      payload_hash: null,
      signer_authorized: false
    };
  }

  if (!signature_bytes) {
    return {
      ...baseResponse('missing_signature'),
      signature_valid: false,
      cryptogreen: false,
      payload_hash: sha256(payload_jcs),
      signer_authorized: signerSet.has(normalizedSigner)
    };
  }

  if (scheme !== 'secp256k1') {
    return {
      ...baseResponse('unsupported_scheme'),
      signature_valid: false,
      cryptogreen: false,
      payload_hash: sha256(payload_jcs),
      signer_authorized: signerSet.has(normalizedSigner)
    };
  }

  if (!signerSet.has(normalizedSigner)) {
    return {
      ...baseResponse('signer_not_authorized'),
      signature_valid: false,
      cryptogreen: false,
      payload_hash: sha256(payload_jcs),
      signer_authorized: false
    };
  }

  return {
    ...baseResponse('verifier_not_connected'),
    signature_valid: false,
    cryptogreen: false,
    payload_hash: sha256(payload_jcs),
    signer_authorized: true,
    scheme: 'secp256k1',
    verification_performed: false
  };
}

function assertSignatureBoundary(response) {
  if (response.authority !== false) throw new Error('authority breach');
  if (response.truth_claim !== false) throw new Error('truth_claim breach');
  if (response.mutation !== null) throw new Error('mutation breach');
  if (!Array.isArray(response.mutations) || response.mutations.length !== 0) throw new Error('mutations breach');
  if (response.signature_valid === true && response.cryptogreen !== true) throw new Error('valid signature without cryptogreen consistency');
  if (response.cryptogreen === true && response.reason !== 'signature_verified') throw new Error('cryptogreen without signature_verified');
  return true;
}

module.exports = {
  verifySignatureSurface,
  assertSignatureBoundary,
  sha256
};
