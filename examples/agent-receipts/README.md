# Agent Receipts Demo

> Status: AR-001 executable vertical slice

This demo proves one narrow flow:

```text
one tool call -> receipt hook -> policy evaluation -> signed receipt -> replay verification
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
2. Computes `policy.policy_hash` from `policy/agent-receipts/default-policy.json`.
3. Builds an Agent Receipt v0.2 object.
4. Computes `content_hash` from the AR-001 preimage:

```text
inputs + outputs + captured_context + policy_hash + manifest_hash + parent_hash
```

5. Sets `receipt_id = content_hash`.
6. Signs the full canonical receipt minus the `signature` field.
7. Writes `receipts/agent-demo.receipt.json`.
8. Verifies signature before replay.
9. Replays `content_hash`.
10. Runs failure-mode checks.

## Expected Output

```text
valid receipt: VERIFIED
tampered receipt: REJECTED
valid signature with replay divergence: MISMATCHED
receipt_written: receipts/agent-demo.receipt.json
authority: false
```

## Failure-Mode Precedence

Signature verification is the pre-replay gate.

That means direct tampering of a signed receipt returns:

```text
REJECTED
```

It does not return `MISMATCHED`, because replay should not run against an invalid signature.

`MISMATCHED` is reserved for a well-formed, validly signed receipt whose replayed `content_hash` diverges from the recorded value.

## Success Criteria

| Property | Demo Check |
|---|---|
| Receipt generation | `receipts/agent-demo.receipt.json` is written. |
| Policy evaluation | Receipt includes `policy.policy_hash` and `policy_result`. |
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
