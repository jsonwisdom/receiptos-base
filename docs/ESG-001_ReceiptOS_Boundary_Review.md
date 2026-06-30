# ESG-001 ReceiptOS Boundary Review

Issue: #34

## Status

ReceiptOS is treated as a pure representation protocol.

The conformance floor is limited to:

- canonical encoding
- payload hash binding
- signature metadata and verification hook
- bounded timestamp checks
- nonce structure
- transport-neutral framing
- explicit `authority: false`
- explicit `truth_claim: false`

## Firewall

ReceiptOS core does not define:

- truth adjudication
- causation
- legal meaning
- evidence admissibility
- confidence promotion
- graph-derived state mutation
- shared-state replay registries
- agentic decision loops

## ArtifactHash canonicalization

ArtifactHash canonicalization is deferred to the application profile (e.g., raw payload bytes per content-type, decompressed, pre-transport encoding). The conformance validator treats the provided `artifact_hash` as an opaque cryptographic claim: it MUST verify only structural well-formedness (valid hex) and inclusion under the frame's signature envelope. The validator MUST NOT compute or re-derive the hash itself.

## Added scaffold

- `schemas/receiptos-frame.schema.json`
- `tools/validate_receiptos_frame.py`
- `fixtures/rp-001-receiptos-frame.example.json`

## RP-001 fixture note

The RP-001 frame is witness-only. Its artifact hash is a placeholder until a real `provide_computed_sha256` command binds the artifact.

The fixture intentionally preserves:

```json
{
  "authority": false,
  "truth_claim": false
}
```

## Validator posture

The reference validator skeleton returns protocol conformance only. A conformant result means the frame encoding and binding checks passed. It does not mean the underlying proposition is true.

Example result shape:

```json
{
  "valid_encoding": true,
  "hash_match": true,
  "signature_valid": true,
  "timestamp_within_bounds": true,
  "nonce_well_formed": true,
  "conformant": true,
  "authority": false,
  "truth_claim": false,
  "errors": []
}
```

## Standardization line

Conformance is proven from canonical encoding, cryptographic binding, signature verification, bounded timestamp checks, and nonce structure alone. Everything above that line is application policy.
