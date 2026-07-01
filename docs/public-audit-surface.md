# EXT-103 — Public Audit Surface

## Purpose

EXT-103 exposes a public, read-only audit surface for the JAYWISDOM / ReceiptOS Frame stack.

This layer allows external auditors to inspect integrity anchors, manifest locks, replay challenge metadata, and audit bundle pointers without trusting operators or mutating system state.

## Public Posture

```json
{
  "audit_posture": "PUBLIC_VERIFIABLE",
  "security": [],
  "frame_mode": "EYES_NO_HANDS",
  "authority": false,
  "truth_claim": false,
  "mutation": null,
  "mutations": []
}
```

## Public Endpoints

```text
GET  /api/audit/root
GET  /api/audit/manifest-lock
GET  /api/audit/bundle
POST /api/audit/challenge-replay
```

## Endpoint Roles

### GET /api/audit/root

Returns the public integrity anchor metadata.

The Merkle root may be `PENDING_ANCHOR` until a real root is produced and anchored. A pending root must not be represented as anchored.

### GET /api/audit/manifest-lock

Returns the canonical Farcaster manifest lock hash and identity binding.

### GET /api/audit/bundle

Returns audit bundle metadata or a pending bundle pointer. The endpoint must not fabricate an archive, artifact, or historical root.

### POST /api/audit/challenge-replay

Accepts replay challenge input and returns deterministic observation metadata. It may report match or mismatch. It may not mutate state, create receipts, or resolve truth claims.

## Required Response Boundary

Every EXT-103 response must include:

```json
{
  "authority": false,
  "truth_claim": false,
  "mutation": null,
  "mutations": []
}
```

## Forbidden Behavior

```text
authority=true
truth_claim=true
mutation object
non-empty mutations array
operator-only gatekeeping
fabricated merkle root
fabricated audit bundle
silent receipt creation
silent manifest mutation
profile-as-ledger substitution
CRYPTOGREEN emission without signer verification
```

## Invariant

The public audit surface makes the system inspectable. It does not make the system authoritative.

Public verification is not truth adjudication.

Timestamp, not tribunal.
