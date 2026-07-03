# Agent Receipts Demo

> Status: MVP vertical slice stub

This demo proves one narrow flow:

```text
one tool call -> receipt hook -> policy evaluation -> signed receipt -> replay bundle
```

## Tool Call

```text
echo("hello receiptos agent receipts") -> "hello receiptos agent receipts"
```

## Success Criteria

| Property | Demo Check |
|---|---|
| Receipt generation | `receipts/agent-demo.receipt.json` exists. |
| Policy evaluation | Receipt includes policy decision and version. |
| Replay | Replay bundle reproduces receipt hash. |
| Independent verification | Verifier can validate without access to runtime. |

## Expected Files

```text
examples/agent-receipts/
├── README.md
├── tool-call.input.json
├── tool-call.output.json
└── replay-bundle.json
```

## Expected Result

```text
receipt_generated: pass
policy_evaluated: pass
signature_verified: pass
replay_hash_match: pass
authority: false
```
