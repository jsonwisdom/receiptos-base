# EXT-106 — Signature Verification Surface

## Purpose

EXT-106 defines a stateless signature verification surface for the JAYWISDOM / ReceiptOS registry path.

The Frame and audit endpoint may evaluate cryptographic evidence. They must not produce signatures, mutate the registry, mutate the manifest lock, or create authority/truth claims.

## Core Function

```text
verify(signature_bytes, payload_jcs, authorized_signers[]) -> boolean
```

## Endpoint

```text
POST /api/audit/verify-signature
```

## Request Shape

```json
{
  "payload_jcs": "RFC8785 canonical JSON string",
  "signature_bytes": "external signature bytes",
  "signer_address": "authorized signer address",
  "scheme": "secp256k1"
}
```

## Response Shape

Valid signature response:

```json
{
  "signature_valid": true,
  "reason": "signature_verified",
  "cryptogreen": true,
  "authority": false,
  "truth_claim": false
}
```

Invalid signature response:

```json
{
  "signature_valid": false,
  "reason": "signature_invalid",
  "cryptogreen": false,
  "authority": false,
  "truth_claim": false
}
```

## Required Boundary Fields

Every response must include:

```json
{
  "authority": false,
  "truth_claim": false,
  "mutation": null,
  "mutations": []
}
```

## Valid Reasons

```text
signature_verified
signature_invalid
signer_not_authorized
unsupported_scheme
missing_payload
missing_signature
verifier_not_connected
```

## CRYPTOGREEN Boundary

`cryptogreen: true` is allowed only when all are true:

```text
signer is present in canonical registry
scheme is supported
payload_jcs is present
signature_bytes are present
signature cryptographically verifies
```

`cryptogreen: true` does not mean:

```text
the payload is true
the signer is trusted as an authority
the system endorses the content
the manifest lock mutated
the registry mutated
```

## Current Implementation Posture

Until a real secp256k1 verifier and known-good signature vector are connected, the implementation must return `signature_valid: false` and `cryptogreen: false` with a safe reason.

## Invariant

The verification surface lets math speak. It does not let the Frame govern.

Timestamp, not tribunal.
