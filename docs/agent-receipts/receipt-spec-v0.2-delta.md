# Agent Receipt Specification v0.2 Delta

> Status: Contract hardening delta for Agent Receipt v0.1

## Purpose

This document upgrades the v0.1 agent receipt contract by tightening replay scope, hashing scope, policy evidence, and chaining semantics.

The v0.2 rule is simple:

```text
recorded transformation -> content_hash -> receipt_id -> full receipt signature
```

## Required Changes

### 1. Separate content hash from signature scope

Add `content_hash` as the replayable hash of the recorded transformation core.

`receipt_id` must equal `content_hash`.

The signature covers the full canonicalized receipt minus the signature field.

### 2. Narrow replay scope

Replay verifies the recorded transformation only.

Replay does not mean live re-execution of the agent.

Given the receipt minus signature, captured inputs, outputs, and context, the verifier must reproduce the identical `content_hash`.

### 3. Add captured context

Add `captured_context` for nondeterministic material.

Examples:

- raw model output
- raw API response
- random seed
- wall-clock value used by the action
- model identifier and sampling settings
- environment metadata needed for replay explanation

### 4. Make chaining content-addressed

Replace parent receipt references with `parent_hash`.

`parent_hash` must be the `content_hash` of the prior receipt, or `null` for the first receipt.

### 5. Require policy evidence

Add `policy.policy_hash`.

A version string alone is insufficient for independent verification.

`policy_hash` should identify the actual rule set, policy file, or evaluator code used to produce the policy result.

### 6. Scope manifest hash

Add explicit limitation language:

`manifest_hash` is self-attested by the producer. A verifier can confirm consistency with a supplied manifest, but cannot independently prove the manifest is complete.

## v0.2 Receipt Shape

```json
{
  "receipt_version": "agent-receipt/v0.2",
  "receipt_id": "sha256:<content_hash>",
  "timestamp": "ISO8601",
  "agent_id": "string",
  "action_type": "tool_call | policy_eval | state_transition | ...",
  "inputs": {},
  "outputs": {},
  "captured_context": [
    {
      "type": "llm_sample | api_response | wall_clock | seed | environment | recorded_transformation",
      "value": "string or object"
    }
  ],
  "policy": {
    "version": "string",
    "policy_hash": "sha256:<hash-of-policy-material>",
    "policy_id": "string"
  },
  "policy_result": {
    "pass": true,
    "details": {}
  },
  "parent_hash": "sha256:<prior-content-hash> | null",
  "manifest_hash": "sha256:<hash-of-referenced-artifacts>",
  "content_hash": "sha256:<jcs-hash-of-recorded-transformation-core>",
  "signature": {
    "scheme": "ed25519",
    "public_key": "string",
    "value": "base64:<signature>"
  },
  "authority": false
}
```

## Content Hash Rule

`content_hash` is computed from:

```text
inputs + outputs + captured_context + policy.policy_hash + manifest_hash + parent_hash
```

Use deterministic JSON canonicalization and SHA-256.

## Allowed Claims

Agent Receipt v0.2 may support evidence that:

- a recorded action occurred inside an instrumented workflow,
- inputs, outputs, and captured context were recorded,
- a hashed policy evaluated the receipt,
- replay reproduced the same `content_hash`,
- the receipt chain is content-addressed through `parent_hash`,
- the full receipt has not changed since signing.

## Out of Scope

Agent Receipt v0.2 does not prove:

- semantic correctness of agent reasoning or policy,
- honesty of external dependencies or captured context,
- completeness of `manifest_hash`,
- live re-execution of nondeterministic steps,
- runtime integrity before instrumentation.

## Implementation Checklist

- Add `captured_context` field and examples.
- Separate `content_hash` from full receipt signature.
- Set `receipt_id = content_hash`.
- Replace parent receipt reference with `parent_hash`.
- Add `policy_hash` to policy object.
- Document replay as recorded transformation only.
- Add manifest completeness limitation.
- Update demo fixtures to match v0.2.
- Update verifier tests to enforce v0.2 fields.
