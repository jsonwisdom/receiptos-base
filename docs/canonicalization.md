# ReceiptOS Canonicalization Bedrock v0.2

Status: implementation rail  
Issue: #119  
Invariant: `authority=false`

## Purpose

Define the canonicalization rail for ReceiptOS receipt packets before full validator integration.

## Required Standard

ReceiptOS v0.2 uses a restricted canonical JSON profile:

- JSON object keys sorted lexicographically.
- Compact JSON separators.
- Unicode NFC normalization before canonical serialization.
- Deterministic hashing over immutable `receipt_core` only.
- No floats in receipt core unless a later spec explicitly defines numeric canonicalization.

## Hash Rule

```text
receipt_id = sha256(canonical_json(receipt_core))
core_hash  = receipt_id
```

Hash fields use the prefix:

```text
sha256:<64 lowercase hex characters>
```

## Fields Excluded From `receipt_core`

The following are mutable or publication metadata and must not affect `receipt_id`:

- `receipt_id`
- `core_hash`
- `hashes`
- `variants`
- `approval_status`
- `publish_targets`
- `replay_status`
- `created_at`
- `updated_at`
- `previous_receipt`
- `cid`
- publication URLs
- replay counters

Circular commitment fields excluded from core before hashing:

- `birth_witness.witness_hash`
- `custody.chain_head`

## Required Fixture

Card 001 seed:

```text
title: RECURSIVE CLOUD
ticker: $LOOP
identity_anchor: jaywisdom.base.eth
eas_uid: 0x4dcdb352bfff0c852a556c59567869bd16365cb45e26035b2f94f40abd850654
ipfs_cid: bafkreihkplguzcftebvs5qjgf6trw7h73frpmm7bdwjgrd7j6ahswrnzqu
authority: false
receipt_id: sha256:2e37f5dffe884c2223381fa1cddbbd01d42c9f3cf91c5492931e14c5b33474af
```

## Bedrock Rule

No fake green. The hash rail is not Phase 1 locked until executable tests pass.
