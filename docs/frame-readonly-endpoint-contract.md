# EXT-098 — Frame Read-Only Endpoint Contract

## Purpose

EXT-098 defines the first live Frame implementation surface for ReceiptOS / JAYWISDOM Farcaster verification.

This is a read-only contract. It enables inspection, replay, and challenge flows without mutating the canonical manifest, elevating authority, or resolving truth claims.

## Dependency Chain

```text
EXT-092 Public Witness Surface
  -> EXT-097 Frame Extension Layer
  -> EXT-098 Frame Read-Only Endpoint Contract
```

Signer lane remains separate:

```text
EXT-096: PENDING_EXTERNAL_SIGN
CRYPTOGREEN: BLOCKED_UNTIL_VERIFIED_SIGNATURE
```

## Endpoint Surface

### 1. Receipt Viewer

```text
GET /api/receipts/:id
```

Returns a receipt or safe failure object.

```json
{
  "endpoint": "receipt_viewer",
  "receipt_id": "string",
  "status": "FOUND_OR_NOT_FOUND",
  "receipt_hash": "sha256_or_null",
  "authority": false,
  "truth_claim": false
}
```

### 2. Manifest Lock Inspector

```text
GET /api/manifest-lock
```

Returns the locked manifest metadata.

```json
{
  "endpoint": "manifest_lock_inspector",
  "manifest_id": "jaywisdom",
  "manifest_path": ".well-known/farcaster/manifest.jcs",
  "lock_path": ".well-known/farcaster/manifest.lock.json",
  "lock_sha256": "d3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce",
  "canonicalization": "RFC8785",
  "authority": false,
  "truth_claim": false
}
```

### 3. Hash Challenger

```text
POST /api/hash-challenge
```

Accepts user-supplied bytes or a declared SHA-256 and reports whether it matches the locked manifest hash.

```json
{
  "endpoint": "hash_challenger",
  "challenge_type": "provided_hash_or_uploaded_bytes",
  "computed_hash": "sha256",
  "expected_hash": "d3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce",
  "match": true,
  "authority": false,
  "truth_claim": false
}
```

### 4. Witness Surface Linkout

```text
GET /api/witness-surface
```

Returns the public Farcaster witness surface without treating it as canonical truth.

```json
{
  "endpoint": "witness_surface",
  "public_witness_url": "https://farcaster.xyz/cmptrwsdm",
  "role": "public_identity_projection",
  "canonical_manifest": false,
  "source_of_truth": false,
  "authority": false,
  "truth_claim": false
}
```

## Frame Actions

```text
VIEW_RECEIPT
INSPECT_LOCK
CHALLENGE_HASH
OPEN_WITNESS_SURFACE
SUBMIT_EVIDENCE_CANDIDATE
```

## Forbidden Behavior

```text
No writes to .well-known/farcaster/*
No mutation of manifest.lock.json
No signer-status upgrade
No CRYPTOGREEN emission
No authority=true
No truth_claim=true
No profile-as-ledger substitution
No private key or recovery phrase collection
```

## Interaction Receipt Rule

Every endpoint response SHOULD be reducible to:

```json
{
  "request_hash": "sha256_of_canonical_request",
  "response_hash": "sha256_of_canonical_response",
  "endpoint": "endpoint_name",
  "status": "safe_status",
  "authority": false,
  "truth_claim": false
}
```

## Invariant

A Frame endpoint may expose verification surfaces. It may not become the court.

Timestamp, not tribunal.
