# EXT-001 Mutation Rules

Status: manual-review-required
Authority: false
Target: ACTIVE_LANES.md
Lane: PRC-JRN-EXT-001

## Purpose

Define the only admissible mutation from a verified EXT-001 receipt into ACTIVE_LANES.md.

## Required Payload

```text
lane: PRC-JRN-EXT-001
receipt_sha256: <64 lowercase hex chars>
```

## Preconditions

- ACTIVE_LANES validator passes before mutation.
- Payload is authentic EXT-001 output.
- Receipt hash is reproducible.
- Receipt pointer is content-addressed.
- No symbolic receipt labels are used.
- authority remains false.

## Deterministic Mutation

Before verified receipt:

```text
LANE: PRC-JRN-EXT-001
STATUS: YELLOW
STATUS_SOURCE: REPORTED
RECEIPT_PTR: NULL
authority: false
```

After verified receipt:

```text
LANE: PRC-JRN-EXT-001
STATUS: GREEN
STATUS_SOURCE: VERIFIED_RECEIPT
RECEIPT_PTR: sha256:<receipt_sha256>
authority: false
```

## Rejection Conditions

Reject mutation if:

- `receipt_sha256` is missing.
- `receipt_sha256` is not 64 lowercase hex chars.
- lane does not equal `PRC-JRN-EXT-001`.
- validator fails before mutation.
- validator fails after mutation.
- `authority` is anything other than `false`.
- `AUDITOR_VIEW` is manually supplied.
- `RECEIPT_PTR` is symbolic.

## Required Review Sequence

1. Capture raw EXT-001 payload.
2. Compute SHA-256.
3. Freeze append-only.
4. Update ACTIVE_LANES.md using the deterministic mutation above.
5. Run `python ztvs/active_lanes_validator.py`.
6. Commit ACTIVE_LANES.md and the receipt file together.

## Commit Message

```text
EXT-001: apply verified active lane mutation
```

Authority remains false.
