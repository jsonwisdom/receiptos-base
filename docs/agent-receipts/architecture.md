# Agent Receipts Architecture v0.1

> Receipt Backbone inside ReceiptOS Base

Receipt Backbone is an adoption-first layer for agent workflows. It instruments existing agents instead of replacing them.

## MVP Flow

```text
Agent Action
    ↓
Receipt Hook
    ↓
Policy Check
    ↓
Signed Receipt
    ↓
Replay Bundle
    ↓
Independent Verifier
```

## Why receiptos-base

`receiptos-base` is the correct canonical substrate because it already centers:

- replay-safe verification,
- canonical bytes,
- manifest locks,
- CI receipts,
- Base/onchain compatibility,
- `authority=false` doctrine.

`receipts-engine-v1` can remain the public verifier surface. `receiptos-base` should hold the agentic receipt core.

## Four Verifiable Properties

| Property | Success Criterion |
|---|---|
| Receipt generation | Every agent action emits a signed record. |
| Policy evaluation | Every receipt records pass/fail with rule version. |
| Replay | Same inputs reproduce the same receipt hash. |
| Independent verification | Third party validates without trusting the runtime. |

## Trust Boundary

The verifier is the trust root.

The runtime is only a receipt producer.

The receipt proves recorded execution structure, not objective correctness.
