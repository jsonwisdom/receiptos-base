# Docket #61 — User-Space Interpretation Layer

## Status

IMPLEMENTED_PENDING_DEPLOY

## Overview

Docket #61 adds an interpretation layer that allows applications to compute derived views from canonical ReceiptOS receipts without mutating the receipt or promoting claims.

ReceiptOS verifies. Applications interpret.

## Separation

```text
Wire -> Schema -> Interpretation (app-owned) -> Presentation
```

## Invariants

- `truth_claim=false`
- `authority=false`
- `verdict=WITNESS_ONLY`
- receipts remain immutable
- interpretations are computed separately from receipts
- interpretation policy is application-owned

## Files

```text
schemas/interpretation-v1.json
lib/interpretation/policies.ts
app/api/interpret/route.ts
examples/trust-score-adapter.ts
tests/interpretation-boundary.sh
```

## API

```text
POST /api/interpret
```

Request:

```json
{
  "receipt_id": "docket-57-ros-0006",
  "policy": "trust-score-v1"
}
```

Response:

```json
{
  "valid": true,
  "reason": "interpretation_computed",
  "receipt_id": "docket-57-ros-0006",
  "wire_reference": "https://receiptos-base.vercel.app/stream",
  "interpretation": {
    "policy": "trust-score-v1",
    "score": 1,
    "inputs": ["authority_false", "chain_8453", "erc1271", "erc1271_magic", "ros_0006", "signature_verified", "truth_claim_false", "witness_only"],
    "computed_at": "1970-01-01T00:00:00.000Z",
    "authority": false,
    "truth_claim": false,
    "verdict": "WITNESS_ONLY"
  },
  "authority": false,
  "truth_claim": false,
  "verdict": "WITNESS_ONLY"
}
```

## Policies

```text
trust-score-v1
risk-v1
```

The policies are deterministic. Same receipt and same policy produce the same score.

## Boundary tests

```bash
BASE_URL=https://receiptos-base.vercel.app bash tests/interpretation-boundary.sh
```

Expected:

```text
ALL 6 PASS — Interpretation boundary hardened.
DOCKET_61_PASSED
```

## Closing

ReceiptOS remains a sovereign verification engine. Applications may derive trust. The protocol never emits truth.
