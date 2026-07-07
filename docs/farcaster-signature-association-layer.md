# EXT-093 — Farcaster Signature Association Layer

## Purpose

EXT-093 defines the replay-safe signature association layer for the locked JAYWISDOM Farcaster identity stack.

This layer binds the canonical manifest identity to signer provenance without granting authority to the signer, the public profile, or any social surface.

```text
manifest_id: jaywisdom
public_witness_url: https://farcaster.xyz/cmptrwsdm
manifest_path: .well-known/farcaster/manifest.json
canonical_manifest_path: .well-known/farcaster/manifest.jcs
lock_path: .well-known/farcaster/manifest.lock.json
lock_sha256: d3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce
previous_doctrine: docs/farcaster-public-witness-surface.md
authority: false
truth_claim: false
```

## Boundary

A signer association is evidence of cryptographic control at a point in time. It is not proof that any underlying claim is true.

Signer control may support identity continuity, replay checks, and domain binding. It must not be interpreted as sovereign authority, truth authority, or protocol finality.

## Signature Association Object

```json
{
  "layer": "signature_association",
  "manifest_id": "jaywisdom",
  "public_witness_surface": "https://farcaster.xyz/cmptrwsdm",
  "canonical_manifest": ".well-known/farcaster/manifest.jcs",
  "lock_sha256": "d3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce",
  "signer_surface": "pending_real_account_association_payload",
  "signer_provenance": "pending",
  "replay_safe_signature_metadata": true,
  "authority": false,
  "truth_claim": false
}
```

## Valid Evidence Inputs

The association layer may accept only replayable signer evidence:

- Farcaster account association payload
- Signature bytes
- Verifiable signer address or key identifier
- Domain binding statement
- Timestamp or signed payload timestamp
- Canonical serialization method
- SHA-256 hash of canonical association payload

## Verification Procedure

```text
1. Capture raw account association payload.
2. Canonicalize payload using the declared serialization rule.
3. Compute SHA-256 over canonical payload bytes.
4. Verify signature against declared signer material.
5. Confirm declared domain or identity binding matches manifest scope.
6. Record signer metadata without mutating the locked manifest.
7. Preserve authority=false and truth_claim=false.
```

## Failure Modes

```text
signature_missing -> association_pending
signature_invalid -> association_rejected
canonicalization_drift -> association_rejected
signer_mismatch -> association_rejected
domain_mismatch -> association_rejected
manifest_lock_mismatch -> association_rejected
authority_escalation_attempt -> association_rejected
truth_claim_injection -> association_rejected
```

## Non-Mutation Rule

The signature association layer does not rewrite the manifest lock.

If the live manifest changes, a new canonical manifest hash and new lock artifact must be produced through the existing replay chain.

## Invariant

```text
Signature proves control of signer material under replayable conditions.
Signature does not prove truth.
Signature does not grant authority.
Signature does not mutate the canonical manifest.
```

Timestamp, not tribunal.
