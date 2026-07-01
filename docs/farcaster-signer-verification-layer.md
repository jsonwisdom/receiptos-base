# EXT-095 — Farcaster Signer Verification Layer

## Purpose

EXT-095 defines the verification gate that turns a pending signer evidence bundle into a cryptographically verified identity association only when real signer evidence is present and replay-verifiable.

This layer does not create signer evidence. It validates signer evidence.

## Dependency Chain

```text
EXT-092 Public Witness Surface
  -> EXT-093 Signature Association Layer
  -> EXT-094 Pending Signer Evidence Bundle Intake
  -> EXT-095 Signer Verification Layer
```

## Input Artifacts

```text
receipts/ext-094-signer-evidence-bundle.pending.json
signer_payload.jcs
signature_receipt.json
```

`signer_payload.jcs` and `signature_receipt.json` must contain real externally signed material. Placeholders are not admissible.

## Signature Receipt Shape

```json
{
  "payload_hash": "sha256_of_signer_payload_jcs",
  "signer_fid": "real_farcaster_fid_or_signer_identifier",
  "signature": "0xREAL_SIGNATURE_BYTES",
  "verification_method": "farcaster_account_association",
  "status": "SIGNED"
}
```

## Verification Rules

```text
1. Read signer_payload.jcs as exact UTF-8 bytes.
2. Compute SHA-256 over signer_payload.jcs.
3. Confirm computed hash equals signature_receipt.payload_hash.
4. Confirm signature_receipt.status == SIGNED.
5. Reject placeholder values, null signer fields, or fake signature markers.
6. Verify signature against the declared Farcaster signer material.
7. Confirm payload manifest_id == jaywisdom.
8. Confirm payload canonical_hash == locked manifest hash.
9. Confirm domain binding targets cmptrwsdm.com/.well-known/farcaster/manifest.json.
10. Confirm authority=false and truth_claim=false.
11. Confirm locked manifest was not mutated.
```

## Valid Transition

```text
AWAITING_REAL_SIGNER_EVIDENCE
  -> SIGNER_EVIDENCE_RECORDED
  -> SIGNATURE_VERIFIED
  -> CRYPTOGREEN
```

`CRYPTOGREEN` is valid only after byte-level hash reconciliation and signature verification both pass.

## Rejection States

```text
payload_hash_mismatch -> ASSOCIATION_REJECTED
signature_missing -> ASSOCIATION_REJECTED
signature_placeholder -> ASSOCIATION_REJECTED
signature_invalid -> ASSOCIATION_REJECTED
signer_mismatch -> ASSOCIATION_REJECTED
domain_mismatch -> ASSOCIATION_REJECTED
manifest_lock_mismatch -> ASSOCIATION_REJECTED
authority_escalation_attempt -> ASSOCIATION_REJECTED
truth_claim_injection -> ASSOCIATION_REJECTED
manifest_mutation_detected -> ASSOCIATION_REJECTED
```

## Cryptogreen Boundary

```json
{
  "cryptogreen_means": [
    "real signer evidence present",
    "payload hash reconciled",
    "signature verifies",
    "domain binding matches",
    "locked manifest unchanged",
    "authority=false",
    "truth_claim=false"
  ],
  "cryptogreen_does_not_mean": [
    "underlying claim is true",
    "signer has sovereign authority",
    "manifest may be silently mutated",
    "public profile is source of truth"
  ]
}
```

## Invariant

Cryptographic control is admissible only as replayable provenance evidence.

It does not become truth authority.

Timestamp, not tribunal.
