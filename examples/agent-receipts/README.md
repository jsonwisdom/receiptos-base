# Agent Receipts Demo

> Status: MVP vertical slice terminal states proven

This demo proves one narrow flow:

```text
one tool call -> receipt hook -> structured policy evaluation -> signed receipt -> replay verification
```

It intentionally uses plain Node.js and built-in `crypto` only. No `npm install` is required.

## Run

From the repository root:

```bash
node examples/agent-receipts/run-demo.js
```

## Tool Call

```text
echo("hello receiptos agent receipts") -> "hello receiptos agent receipts"
```

The tool input and output fixtures live beside this README:

```text
examples/agent-receipts/tool-call.input.json
examples/agent-receipts/tool-call.output.json
```

## What the Runner Does

1. Loads the input, output, and policy fixtures.
2. Computes `policy.policy_hash` over `{ version, rules }` from `policy/agent-receipts/default-policy.json`.
3. Builds an Agent Receipt v0.2 object.
4. Evaluates policy with structured matchers, not `eval()`.
5. Computes `content_hash` from the AR-001 preimage:

```text
inputs + outputs + captured_context + policy_hash + manifest_hash + parent_hash
```

6. Sets `receipt_id = content_hash`.
7. Signs the full canonical receipt minus the `signature` field.
8. Writes `receipts/agent-demo.receipt.json`.
9. Writes `receipts/agent-demo-policy-denied.receipt.json`.
10. Verifies signature before policy-hash freshness.
11. Verifies policy hash before replay.
12. Replays `content_hash`.
13. Runs terminal-state checks.

## Policy Hash Rule

The policy file does not contain its own `policy_hash`.

That avoids a circular self-reference. The runner computes `policy_hash` at load time over:

```json
{
  "version": "<policy_version>",
  "rules": ["<serialized rules>"]
}
```

## Policy Evaluation Rule

The demo does not evaluate policy-authored condition strings.

Policy rules use structured matchers. A future general condition language needs a real parser or sandboxed evaluator before it should be accepted from policy files.

## Expected Output

```text
valid receipt: policy pass=true
valid receipt: VERIFIED
policy denied receipt: policy pass=false
policy denied receipt: VERIFIED
policy hash drift: STALE
tampered receipt: REJECTED
valid signature with replay divergence: MISMATCHED
receipt_written: receipts/agent-demo.receipt.json
policy_denied_receipt_written: receipts/agent-demo-policy-denied.receipt.json
authority: false
```

## Terminal States

| Terminal | Meaning | Demo Case |
|---|---|---|
| `VERIFIED` | Signature, policy hash, and replay all match. | Valid receipt. |
| `STALE` | Signature is valid, but current policy hash differs from recorded policy hash. | Synthetic policy drift. |
| `REJECTED` | Receipt is malformed, authority boundary is violated, or signature is invalid. | Tampered signed receipt. |
| `MISMATCHED` | Signature is valid, but replayed `content_hash` diverges. | Resigned replay-divergent receipt. |

## Failure-Mode Precedence

Verification order is:

```text
parse/authority -> signature -> policy_hash freshness -> content_hash replay
```

Direct tampering of a signed receipt returns:

```text
REJECTED
```

It does not return `MISMATCHED`, because replay should not run against an invalid signature.

`STALE` is reserved for validly signed receipts whose recorded policy hash no longer matches the supplied current policy material.

`MISMATCHED` is reserved for a well-formed, validly signed, policy-current receipt whose replayed `content_hash` diverges from the recorded value.

## Policy Failure as Evidence

A policy-denied receipt is still emitted and signed.

That means policy violations are audit evidence, not silent drops.

The demo proves this with an `llm_call` that omits `captured_context`. The structured policy denies it, but the receipt still verifies cryptographically.

## Success Criteria

| Property | Demo Check |
|---|---|
| Receipt generation | `receipts/agent-demo.receipt.json` is written. |
| Policy denial evidence | `receipts/agent-demo-policy-denied.receipt.json` is written. |
| Policy hashing | Receipt includes `policy.policy_hash`. |
| Policy freshness | Synthetic policy drift returns `STALE`. |
| Policy evaluation | Receipt includes `policy_result.pass` and rule details. |
| Replay | Replay recomputes `content_hash`. |
| Independent verification | Verifier does not need the original runtime. |
| Authority boundary | Receipt keeps `authority: false`. |

## Boundary

This demo verifies recorded transformation only.

It does not prove:

- semantic correctness,
- external dependency honesty,
- policy quality,
- manifest completeness,
- live re-execution of nondeterministic agent behavior.
