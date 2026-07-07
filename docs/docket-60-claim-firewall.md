# Docket #60 — Claim Firewall

## Status

IMPLEMENTED_PENDING_DEPLOY

## Purpose

Prevent any replayed evidence from being promoted into a truth claim by protocol output.

ReceiptOS remains a proof-processor, not a truth-arbiter.

## Architecture

```text
Wire (Evidence) -> Schema (Constraint) -> Frame (Presentation)
```

## Locked constraints

```text
claim_status = UNPROMOTED
truth_claim = false
authority = false
verdict = WITNESS_ONLY
```

## Files

```text
schemas/claim-v1.json
app/api/claims/route.ts
components/ClaimBadge.tsx
tests/claim-firewall.sh
```

## Endpoint

```text
POST /api/claims
```

## Valid input

```json
{
  "claim_hash": "abc123",
  "claim_status": "UNPROMOTED",
  "truth_claim": false,
  "verified_wire_reference": "wire-xyz-789"
}
```

## Fail-closed cases

- `truth_claim=true`
- `claim_status=PROMOTED`
- `_promote=true`
- nested promotion fields
- SQL-style status injection
- invalid or missing claim hash
- invalid or missing Wire reference

## Test

```bash
BASE_URL=http://localhost:3000 ./tests/claim-firewall.sh
```

## Target production test

```bash
BASE_URL=https://receiptos-base.vercel.app ./tests/claim-firewall.sh
```

## Boundary

All responses preserve:

```json
{
  "authority": false,
  "truth_claim": false,
  "verdict": "WITNESS_ONLY"
}
```

No fake green.
