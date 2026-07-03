# AR-006 Verifier Consumption Contract

> Status: verifier-surface scaffold

AR-006 defines how a verifier surface consumes Agent Receipts v0.2 outputs from ReceiptOS.

This is not a new protocol layer. It is a rendering and audit contract for the already-tagged MVP vertical slice.

## Scope

The verifier consumes a receipt bundle and returns a minimal lifecycle summary.

```text
Receipt Bundle
    ↓
Signature Check
    ↓
Policy Hash Freshness Check
    ↓
content_hash Replay
    ↓
Lifecycle State Render
```

## Minimal Result Shape

```json
{
  "state": "VERIFIED | STALE | REJECTED | MISMATCHED | BOOTSTRAP",
  "receipt_id": "sha256:<content_hash>",
  "content_hash": "sha256:<hex>",
  "signature_valid": true,
  "policy_hash_current": true,
  "replay_match": true,
  "authority": false,
  "evidence": "hash reference or audit trail id"
}
```

## Terminal States

| State | Meaning | Consumer Rendering |
|---|---|---|
| `VERIFIED` | Signature, policy hash, and replay all match. | Valid receipt. |
| `STALE` | Signature is valid, but policy hash differs from current policy material. | Governance halt. |
| `REJECTED` | Malformed receipt, invalid signature, or authority boundary violation. | Hard reject. |
| `MISMATCHED` | Signature valid and policy current, but replayed `content_hash` diverges. | Replay mismatch. |
| `BOOTSTRAP` | Genesis or bootstrap bundle accepted under explicit bootstrap rules. | Bootstrap-only render. |

## Verification Order

```text
parse / authority
    ↓
signature
    ↓
policy_hash freshness
    ↓
content_hash replay
    ↓
render terminal state
```

## Required Discipline

- Do not collapse `STALE`, `REJECTED`, or `MISMATCHED` into green/pass.
- Do not claim semantic correctness.
- Do not claim external dependency honesty.
- Do not claim manifest completeness.
- Preserve `authority=false` in consumer rendering.

## Source of Truth

Protocol behavior is anchored by the tagged vertical slice:

```text
mvp-vertical-slice-complete
```

The executable trace lives at:

```text
examples/agent-receipts/run-demo.js
```
