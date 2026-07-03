# Agent Receipts Demo

> Status: committed fixture verifier for Agent Receipt v0.2 terminal states

This demo verifies committed Agent Receipt fixtures against the current policy material.

```text
receipt fixture -> signature verification -> policy hash freshness -> content_hash replay -> terminal state
```

It intentionally uses plain Node.js and built-in `crypto` only. No `npm install` is required for the receipt verifier.

## Run

From the repository root:

```bash
npm run verify:receipt
```

Equivalent direct command:

```bash
node examples/agent-receipts/run-demo.js
```

## Fixture Files

```text
examples/agent-receipts/fixtures/valid.receipt.json
examples/agent-receipts/fixtures/policy-denied.receipt.json
examples/agent-receipts/fixtures/stale.receipt.json
examples/agent-receipts/fixtures/rejected.receipt.json
examples/agent-receipts/fixtures/mismatched.receipt.json
```

Policy fixtures:

```text
policy/agent-receipts/v0.1.json
policy/agent-receipts/v0.2.json
policy/agent-receipts/default-policy.json
```

`default-policy.json` is the current policy material used by the verifier.

## What the Runner Does

1. Loads committed receipt fixtures.
2. Loads `policy/agent-receipts/default-policy.json`.
3. Verifies Ed25519 signature before replay.
4. Verifies `policy.policy_hash` freshness before replay.
5. Replays `content_hash` from the AR-001 preimage:

```text
inputs + outputs + captured_context + policy_hash + manifest_hash + parent_hash
```

6. Asserts expected terminal states.
7. Prints trace lines with `content_hash`, `policy_hash`, and reason.

## Policy Hash Rule

The policy file does not contain its own `policy_hash`.

That avoids a circular self-reference. The runner computes `policy_hash` at load time over:

```json
{
  "version": "<policy_version>",
  "rules": ["<serialized rules>"]
}
```

## Expected Output

```text
valid receipt: terminal=VERIFIED policy_pass=true content_hash=sha256:3f37c016aef922b693bd3dbc6f18ae502fea6dbadad22cbd9bbad0a2f0ea7602 policy_hash=sha256:01a3c1000c070ce6150be81abc594e8cc7646bed9064d596799ee4e12adeceb8 reason=ok
policy denied receipt: terminal=VERIFIED policy_pass=false content_hash=sha256:117ba9471271c4cfb624e4841a02517246b055dacb31d7ac529b557f8cc7d53e policy_hash=sha256:01a3c1000c070ce6150be81abc594e8cc7646bed9064d596799ee4e12adeceb8 reason=ok
stale receipt: terminal=STALE policy_pass=true content_hash=sha256:481df8d9304be7cc9dbad8c7d72f3be0d9723a907157da2727f1495a7098ac98 policy_hash=sha256:fdf97650672d146d731e88aa204309052ff76b9db234012d8b4fec415388e012 reason=policy_hash mismatch
rejected receipt: terminal=REJECTED policy_pass=true content_hash=sha256:3f37c016aef922b693bd3dbc6f18ae502fea6dbadad22cbd9bbad0a2f0ea7602 policy_hash=sha256:01a3c1000c070ce6150be81abc594e8cc7646bed9064d596799ee4e12adeceb8 reason=invalid signature
mismatched receipt: terminal=MISMATCHED policy_pass=true content_hash=sha256:ecb0794ab4964a01e7f5128f5fcc0855788fc468b576ca73419782fe8ec67301 policy_hash=sha256:01a3c1000c070ce6150be81abc594e8cc7646bed9064d596799ee4e12adeceb8 reason=content_hash replay mismatch
fixture_trace: pass
authority: false
```

## Terminal States

| Terminal | Meaning | Fixture |
|---|---|---|
| `VERIFIED` | Signature, policy hash, and replay all match. | `valid.receipt.json` |
| `VERIFIED` with `policy_pass=false` | Policy-denied receipt is still signed audit evidence. | `policy-denied.receipt.json` |
| `STALE` | Signature is valid, but current policy hash differs from recorded policy hash. | `stale.receipt.json` |
| `REJECTED` | Receipt is malformed, authority boundary is violated, or signature is invalid. | `rejected.receipt.json` |
| `MISMATCHED` | Signature is valid, policy hash is current, but replayed `content_hash` diverges. | `mismatched.receipt.json` |

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

## Boundary

This demo verifies recorded transformation only.

It does not prove:

- semantic correctness,
- external dependency honesty,
- policy quality,
- manifest completeness,
- live re-execution of nondeterministic agent behavior.
