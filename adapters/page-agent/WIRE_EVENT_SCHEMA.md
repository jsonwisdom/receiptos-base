# PageAgent WireEvent Schema v0.1

Status: schema-first contract.

PageAgent acts. ReceiptOS proves. Replay decides.

## Boundary

The PageAgent adapter may emit a canonical `WireEvent`. It must not mutate core bus state directly.

```text
PageAgent receipt
  -> toWireEvent(...)
  -> core bus ingestion candidate
  -> replay witness verifies
```

## Event

```ts
interface PageAgentWireEventV0_1 {
  type: "receiptos.wire.page_agent.ui_action.v0_1";
  version: "0.1.0";
  source: string;
  sequence: number;
  timestamp: string;
  payload: {
    receipt_type: "PAGE_AGENT_UI_ACTION_V0_1";
    command_hash: string;
    dom_before_hash: string;
    dom_after_hash: string;
    action_result_hash: string;
    replay_required: true;
    authority: false;
  };
  payload_hash: string;
  authority: false;
  witness_only: true;
  side_effect: false;
}
```

## Mapping

| PageAgent receipt field | WireEvent field |
| --- | --- |
| `type` | `payload.receipt_type` |
| `command_hash` | `payload.command_hash` |
| `dom_before_hash` | `payload.dom_before_hash` |
| `dom_after_hash` | `payload.dom_after_hash` |
| `action_result` | `payload.action_result_hash` |
| `timestamp` | `timestamp` |
| `authority` | `authority` + `payload.authority` |

## Invariants

- `authority` remains `false` at event and payload layer.
- `witness_only` remains `true`.
- `side_effect` remains `false`.
- `payload_hash` is recomputed from the payload.
- replay is required before any downstream state transition.
