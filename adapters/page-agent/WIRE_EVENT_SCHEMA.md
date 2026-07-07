# PageAgent WireEvent Schema v0.1

Status: schema-first contract.

PageAgent acts. ReceiptOS proves. Replay decides.

## Boundary

The PageAgent adapter may emit a canonical `WireEvent`. It must not mutate core bus state directly.

```text
PageAgent action
  -> receipt capture
  -> schema-aligned WireEvent emission
  -> EAS attestation candidate
  -> replay witness verifies
```

## EAS Schema #1655

```text
0x645dbf9ec783f597d1b1747cc24063e8b566a2ff9f5eda3b6f5034fa0d92a20d
```

## Event

```ts
interface PageAgentWireEventV0_1 {
  event_type: "receiptos.wire.page_agent.ui_action.v0_1";
  version: "0.1.0";
  timestamp: number; // Unix ms from emission
  recipient: "jaywisdom.base.eth" | `0x${string}`;
  replay_required: true;
  authority: false;
  hash_algorithm: "sha256";
  payload_hash: `0x${string}`; // bytes32 over canonical JSON payload
  command_hash: `0x${string}`; // bytes32
  dom_before_hash: `0x${string}`; // bytes32
  dom_after_hash: `0x${string}`; // bytes32
  receipt_type: "PAGE_AGENT_UI_ACTION_V0_1";
  eas_schema_uid?: string;
  replay_engine_version?: string;
  prev_receipt_hash?: `0x${string}`;
}
```

## Mapping

| PageAgent receipt field | WireEvent field |
| --- | --- |
| `type` | `receipt_type` |
| `command_hash` | `command_hash` |
| `dom_before_hash` | `dom_before_hash` |
| `dom_after_hash` | `dom_after_hash` |
| `action_result` | `payload_hash` via canonical JSON |
| `timestamp_ms` | `timestamp` |
| `authority` | `authority` |

## Hashing

- `hash_algorithm` is fixed to `sha256` for v0.1.
- `payload_hash` hashes canonical JSON, with sorted object keys and stable array order.
- DOM and command hashes are UTF-8 SHA-256.
- all hashes are emitted as `0x`-prefixed bytes32 hex.

## Invariants

- `authority` remains `false`.
- `replay_required` remains `true`.
- `hash_algorithm` remains `sha256`.
- all hash fields are `0x`-prefixed bytes32 hex.
- timestamp is a positive Unix millisecond integer.
- DOM-before mismatch fails closed.
- replay is required before any downstream state transition.
- this contract emits an event candidate only; no bus mutation happens here.
