# Docket #58 — Receipt Verification API

## Status

IMPLEMENTED

## Endpoint

```text
POST /api/verify
```

## Purpose

Provide a neutral, read-only replay surface for ReceiptOS receipts.

The endpoint verifies receipt bytes and optional receipt hashes, but it does not become a truth authority.

## Input

```json
{
  "receiptId": "docket-57-ros-0006",
  "receiptHash": "optional sha256 hex"
}
```

Supported receipt IDs:

```text
docket-57-ros-0006
ros-0006-live-stream
ROS-0006:D57:A380
```

## Output

```json
{
  "valid": true,
  "reason": "receipt_replayed",
  "receipt": {},
  "replay": {
    "integrity_standard": "ROS-0006",
    "verification_method": "erc1271",
    "authority": false,
    "truth_claim": false,
    "verdict": "WITNESS_ONLY"
  }
}
```

## Fail-closed behavior

- Missing `receiptId` returns `valid=false`.
- Unknown `receiptId` returns `valid=false`.
- Unreachable Wire returns `valid=false`.
- Hash mismatch returns `valid=false`.
- Wire receipt not satisfying ROS-0006 returns `valid=false`.
- Internal error returns `valid=false`.

## Boundary

The replay object always preserves:

```json
{
  "authority": false,
  "truth_claim": false,
  "verdict": "WITNESS_ONLY"
}
```

## Implementation commit

```text
f71a9b65a724ab052e212653ed4a7cd2ccf42af5
```

No fake green.
