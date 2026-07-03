# Agent Receipt Specification v0.1

> Status: Draft MVP contract

This document defines the minimal agent receipt format for ReceiptOS Base.

The goal is narrow: produce deterministic, signed records for agent actions so a third party can verify what happened without trusting the original runtime.

## Minimal Receipt Shape

```json
{
  "receipt_version": "agent-receipt/v0.1",
  "receipt_id": "sha256:<hex>",
  "run_id": "agent-demo-001",
  "sequence": 1,
  "timestamp_utc": "2026-07-02T00:00:00Z",
  "actor": {
    "type": "agent",
    "id": "example-agent"
  },
  "action": {
    "type": "tool_call",
    "tool_name": "echo",
    "input_sha256": "sha256:<hex>",
    "output_sha256": "sha256:<hex>"
  },
  "policy": {
    "policy_id": "default-agent-policy",
    "policy_version": "0.1.0",
    "decision": "pass",
    "rule_results": [
      {
        "rule_id": "AR-001",
        "result": "pass"
      }
    ]
  },
  "replay": {
    "bundle_id": "sha256:<hex>",
    "canonicalization": "JCS",
    "hash_algorithm": "SHA-256"
  },
  "signature": {
    "scheme": "ed25519",
    "public_key_id": "example-dev-key",
    "signature": "base64:<signature>"
  },
  "authority": false
}
```

## Hashing Rule

`receipt_id` is computed over canonical receipt core bytes:

1. Remove `signature.signature`.
2. Set `receipt_id` to `null` or omit it during preimage construction.
3. Serialize with deterministic JSON canonicalization.
4. Compute SHA-256 over UTF-8 bytes.
5. Encode as `sha256:<hex>`.

## Signature Rule

The MVP signature scheme is Ed25519.

The signature binds canonical receipt bytes to a producer key. The verifier must not need access to the original runtime.

## Required Discipline

- `authority` remains `false`.
- Policy version must be visible.
- Replay metadata must be visible.
- Receipts must not claim correctness beyond recorded execution.

## Allowed Claims

This receipt can support evidence that:

- a recorded action occurred within the instrumented workflow,
- specific input and output hashes were attached,
- a named policy version evaluated the receipt,
- canonical bytes have not changed since signing.

## Disallowed Claims

This receipt does not prove:

- the agent reasoned correctly,
- the external world was honest,
- the policy was the right policy,
- the runtime was uncompromised before instrumentation.
