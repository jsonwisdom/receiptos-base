# Agent Receipts Threat Model v0.1

> Narrow MVP threat model for ReceiptOS Base

Agent Receipts v0.1 aims to prove what happened inside an instrumented workflow.

It does not prove that the agent was correct, that the external world was honest, or that the runtime was uncompromised before instrumentation.

## Assets

| Asset | Why It Matters |
|---|---|
| Receipt core bytes | Primary evidence packet for agent action. |
| Receipt hash | Stable identity for the receipt. |
| Signing key | Binds receipt bytes to a producer identity. |
| Policy version | Prevents silent policy drift. |
| Replay bundle | Allows independent reproduction of receipt hash. |

## Threats and Mitigations

| Threat | Description | MVP Mitigation |
|---|---|---|
| Receipt modification | A receipt is edited after generation. | Digital signatures over canonical receipt bytes. |
| Receipt deletion | A receipt is removed from the local log. | Future hash chain / append-only log. v0 records risk explicitly. |
| Policy drift | A policy changes without visible receipt metadata. | Every receipt includes policy ID and policy version. |
| Replay mismatch | Replay produces a different hash. | Deterministic serialization and replay metadata. |
| Runtime compromise | Runtime lies before receipt creation. | Out of scope for v0. |
| External dependency dishonesty | Tool/API returns false information. | Out of scope unless dependency output is independently verified. |
| Clock manipulation | Timestamp is misleading. | Timestamp is metadata, not proof of truth. |
| Key compromise | Signing key is stolen or misused. | Future key rotation / revocation. v0 records public key ID. |

## Allowed Security Claims

Agent Receipts v0.1 may claim:

- receipt bytes match the recorded receipt hash,
- receipt signature verifies against the declared public key,
- receipt records action, input hash, output hash, policy version, and policy decision,
- replay can reproduce the same receipt hash when inputs and replay bundle are unchanged.

## Prohibited Security Claims

Agent Receipts v0.1 must not claim:

- the agent made the correct decision,
- the policy was the correct policy,
- the runtime was fully trustworthy,
- external dependencies behaved honestly,
- the receipt proves legal or factual truth beyond the recorded execution.

## MVP Boundary

```text
one tool call -> one policy evaluation -> one signed receipt -> one replay verification
```

Everything else belongs in v0.2 or later.
