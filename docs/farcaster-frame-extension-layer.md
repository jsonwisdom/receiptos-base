# EXT-097 — Farcaster Frame Extension Layer

## Purpose

EXT-097 defines the replay-safe Frame Extension Layer for the JAYWISDOM Farcaster identity stack.

This layer expands the Mini App / Frame surface without mutating the locked manifest, elevating authority, or converting interactions into truth claims.

## Dependency Chain

```text
EXT-092 Public Witness Surface
  -> EXT-093 Signature Association Layer
  -> EXT-094 Signer Evidence Intake
  -> EXT-095 Signer Verification Gate
  -> EXT-096 Pending Signer Payload Airlock
  -> EXT-097 Frame Extension Layer
```

Signer verification remains pending. Frame extension may be specified as a capability surface, but no signed capability elevation may be claimed until real signer evidence verifies.

## Frame Surface

```json
{
  "layer": "frame_extension",
  "manifest_id": "jaywisdom",
  "public_witness_surface": "https://farcaster.xyz/cmptrwsdm",
  "domain": "cmptrwsdm.com",
  "app_url": "https://cmptrwsdm.com/app",
  "canonical_manifest": ".well-known/farcaster/manifest.jcs",
  "lock_sha256": "d3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce",
  "signer_status": "PENDING_EXTERNAL_SIGN",
  "authority": false,
  "truth_claim": false
}
```

## Allowed Capabilities

The Frame layer may expose only replay-safe interaction surfaces:

- view receipt
- verify manifest lock
- replay hash check
- inspect witness surface
- open public profile
- submit external evidence candidate
- challenge receipt boundary

## Forbidden Capabilities

```text
authority=true
truth_claim=true
silent manifest mutation
unsigned signer elevation
profile_as_source_of_truth
automatic CRYPTOGREEN claim
private key capture
custodial signer assumption
unverified external evidence promotion
```

## Interaction Receipt Shape

Every Frame interaction should emit a receipt-like event with no truth elevation:

```json
{
  "event_type": "frame_interaction",
  "frame_id": "jaywisdom-replay-frame",
  "action": "verify_manifest_lock",
  "input_hash": "sha256_of_request_payload",
  "output_hash": "sha256_of_response_payload",
  "manifest_lock_hash": "d3e01a4dcb4d64e1617151b211389481c00054f2121a323662546d2e4e2f2cce",
  "authority": false,
  "truth_claim": false
}
```

## Verification Procedure

```text
1. Receive Frame request.
2. Canonicalize request payload.
3. Hash request payload.
4. Execute declared read-only action.
5. Canonicalize response payload.
6. Hash response payload.
7. Emit interaction receipt.
8. Reject any authority or truth escalation.
9. Reject any manifest mutation attempt.
10. Preserve signer_status unless real signer verification has passed.
```

## Valid Statuses

```text
FRAME_SPECIFIED
FRAME_READ_ONLY_READY
FRAME_RECEIPT_EMITTED
FRAME_REJECTED_BOUNDARY_VIOLATION
```

## Invariant

Frames are capability surfaces, not courts.

A Frame can help users inspect, replay, and challenge provenance. It cannot decide truth, grant authority, or mutate canonical identity state.

Timestamp, not tribunal.
