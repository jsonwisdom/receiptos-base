# EXT-105 — Registry Canonization

## Purpose

EXT-105 canonizes the EXT-104 signer seed into a canonical registry layer without mutating `.well-known/farcaster/manifest.lock.json`.

## Canonical Registry Content

```text
version: EXT-105
registry_status: CANONICAL
manifest_id: jaywisdom
manifest_lock_path: .well-known/farcaster/manifest.lock.json
canonical_manifest_hash: d3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce
authorized_signer_address: 0xa380552a27b0a5a2874ea7aa52cac09f542002e8
signer_scheme: secp256k1
added_in: EXT-104
revocations: empty
frame_policy: read_registry_and_verify_math_only
manifest_lock_mutation: false
authority: false
truth_claim: false
```

## Boundary

The registry becomes a machine-verifiable fact layer. The manifest lock remains immutable. The Frame reads the registry and verifies math only.

## Valid Transition

```text
EXT-104 SEEDED_MANUAL_TRUST_ROOT
  -> EXT-105 CANONICAL_REGISTRY_LAYER
```

## Forbidden Transition

```text
canonical_registry -> authority=true
canonical_registry -> truth_claim=true
canonical_registry -> manifest.lock.json mutation
canonical_registry -> CRYPTOGREEN without real signature verification
```

## Invariant

Registry canonization makes the signer set observable and replayable. It does not make the signer authoritative over truth, and it does not give the Frame write power.

Timestamp, not tribunal.
