# Court Clerk Case Console

## Status

ACTIVE

## Purpose

The Court Clerk Case Console is the operator index for ReceiptOS dockets. It tracks cases, crux decisions, live endpoints, receipts, and next actions without letting narrative become authority.

## Constitutional Boundary

Every case entry must preserve:

```json
{
  "authority": false,
  "truth_claim": false,
  "verdict": "WITNESS_ONLY"
}
```

The Court Clerk records state. The Court Clerk does not create truth.

## Console Index

| Case | Docket | Crux | Live Artifact | State |
|---|---:|---|---|---|
| Authorized Identity Gate | #57 | Identity binds to Authorized Identity, not wallet mythology | `/stream`, `/api/frame`, `/api/health`, ROS-0006 | CANONICAL |
| Receipt Verification API | #58 / Issue #60 | External clients need neutral replay verification | `/api/verify` | IMPLEMENTED_PENDING_DEPLOY |

## Case: Docket #57 — Authorized Identity Gate

### Crux

ReceiptOS verifies the actual Authorized Identity. EOAs use EIP-191. Contract accounts use ERC-1271. No EOA emulation for contract accounts.

### Locked Artifacts

```text
ROS-0006: Authorized Identity Invariant
/stream
/api/frame
/api/health
provenance/identity-binding/jaywisdom-identity-binding.txt
provenance/identity-binding/jaywisdom-identity-binding.sig
SHA256SUMS
```

### Live State

```text
SIGNATURE_VERIFIED
verification_method=erc1271
magic=0x1626ba7e
authority=false
truth_claim=false
verdict=WITNESS_ONLY
```

## Case: Docket #58 — Receipt Verification API

### Crux

Receipt verification must be externally consumable without promoting the verifier into a truth authority.

### Endpoint

```text
POST /api/verify
```

### Input

```json
{
  "receiptId": "docket-57-ros-0006",
  "receiptHash": "optional sha256 hex"
}
```

### Output Boundary

```json
{
  "valid": true,
  "reason": "receipt_replayed",
  "replay": {
    "authority": false,
    "truth_claim": false,
    "verdict": "WITNESS_ONLY"
  }
}
```

## Live Console Links

```text
Wire:   https://receiptos-base.vercel.app/stream
Frame:  https://receiptos-base.vercel.app/api/frame
Health: https://receiptos-base.vercel.app/api/health
Verify: https://receiptos-base.vercel.app/api/verify
Docket #57: https://github.com/jsonwisdom/receiptos-base/issues/57
Docket #58: https://github.com/jsonwisdom/receiptos-base/issues/60
```

## Meta Ultra Prompt

```text
You are GitFix / MetaFix operating inside ReceiptOS as the Court Clerk.

Mission:
Advance the next docket while preserving the constitutional membrane.

Canonical state:
- ROS-0006_ACTIVE
- DOCKET_57_BOUND
- WIRE_CANONICAL
- FRAME_DOWNSTREAM_OF_WIRE
- HEALTH_GATE_PASSED
- LIVE_STREAM_RECEIPT_VERIFIED
- NO_FAKE_GREEN_ENFORCED

Rules:
1. Wire owns verification.
2. Frame owns presentation.
3. Health reports subsystem state.
4. Verify API replays receipts but never becomes truth authority.
5. Unknown inputs fail closed.
6. All outputs preserve authority=false and truth_claim=false.
7. Every docket must map to code, spec, endpoint, issue, and receipt evidence.
8. Do not promote narrative into verification.

Current active docket:
Docket #58 — Receipt Verification API.

Required next action:
Pull latest main, build, deploy, and test:
- POST /api/verify with receiptId=docket-57-ros-0006
- hash mismatch fixture
- unknown receipt fixture
- GET /api/verify post_required fixture

Target state:
DOCKET_58_REPLAY_API_VERIFIED
```

## Clerk Commands

```bash
curl -i https://receiptos-base.vercel.app/stream
curl -i https://receiptos-base.vercel.app/api/frame
curl -i https://receiptos-base.vercel.app/api/health
curl -i -X POST https://receiptos-base.vercel.app/api/verify \
  -H "Content-Type: application/json" \
  -d '{"receiptId":"docket-57-ros-0006"}'
```
