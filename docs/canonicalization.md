# ReceiptOS Canonicalization Bedrock v0.2

Status: scaffold / implementation pending  
Issue: #119  
Invariant: `authority=false`

## Purpose

Define the canonicalization rail for ReceiptOS receipt packets before validator implementation.

## Required Standard

ReceiptOS v0.2 will use:

- JSON Canonicalization Scheme (JCS / RFC 8785)
- Unicode NFC normalization before canonical serialization
- Deterministic hashing over immutable `receipt_core` only

## Hash Rule

```text
receipt_id = keccak256(jcs(receipt_core))
core_hash  = receipt_id
```

## Fields Excluded From `receipt_core`

The following are mutable/publication metadata and must not affect `receipt_id`:

- `created_at`
- `updated_at`
- `variants`
- `approval_status`
- `publish_targets`
- `replay_status`
- publication URLs
- replay counters

## Required Fixture

Card 001 seed:

```text
title: RECURSIVE CLOUD
ticker: $LOOP
identity_anchor: jaywisdom.base.eth
eas_uid: 0x4dcdb352bfff0c852a556c59567869bd16365cb45e26035b2f94f40abd850654
ipfs_cid: bafkreihkplguzcftebvs5qjgf6trw7h73frpmm7bdwjgrd7j6ahswrnzqu
authority: false
```

## Bedrock Rule

No fake green. This document is a scaffold until paired with deterministic tests.
