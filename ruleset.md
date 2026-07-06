# Garbage Pail Kidding Ruleset

Status: `GPK_RULESET_V1`  
Authority: `false`  
Schema: `cards/schema.json`  
Replay engine: `engine/replay.py`

## 1. No Receipt = No Authority

A card may be funny, dramatic, cursed, crowned, or loud. None of that grants authority.

Only replayable state transitions count.

## 2. Cards are satirical; effects are deterministic

Each card has two layers:

1. `satirical_text` — flavor text. It may contain jokes, exaggeration, and even `TODO`.
2. `input_effect` and `output_effect` — operational state transition. These must not contain placeholders.

The court ignores flavor when validating state.

## 3. Replay order

Every valid card replay follows this order:

```text
game_state.json + cards/GPK-XXX.json
→ apply input_effect
→ compute next_state
→ compare actual delta with output_effect.state_delta
→ hash canonical next_state
→ compare hash with output_effect.expected_next_hash
→ exit 0 on match, exit 1 on mismatch
```

## 3.1 External evidence intake

External artifacts, including Zora/Base media or token metadata, are sidecar attestations only.

They do not mutate `game_state.json`, do not enter `cards/`, and do not affect canonical replay hashes.

External evidence may be appended to `evidence-ledger.json` only when all checks pass:

1. content hash verified
2. schema compliant under `evidence-ledger.schema.json`
3. `related_receipt` points to an existing sealed receipt
4. `authority` is `false`
5. metadata is excluded from canonical hash calculation

If any check fails, the entry remains `PENDING_REVIEW` or is marked `REJECTED`. No verified commit may be claimed.

## 4. Hashing rule

All hashes use canonical JSON:

```text
sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")))
```

Genesis input hash for `game_state.json`:

```text
sha256:20fcd4f3220b26a88e4c005422c7c3f3dbe34df34d02502a46571c3a5a2e6448
```

Expected next hash after `GPK-001`:

```text
sha256:630dfcf1cacd8e0b0c90175f2d3b9868bb2e5b1b9d7bff1864be41fce7ce8ace
```

## 4.1 Deterministic invariant clause

Canonical replay hashes SHALL be computed only from protocol-defined game state.

Execution metadata is excluded from canonical hash calculation, including:

- timestamps
- run IDs
- host IDs
- system logs
- trace IDs
- execution duration
- debug output

If a hash changes because metadata changed, the hash is measuring execution context, not replay state.

## 5. Placeholder scan

`PLACEHOLDER_SCAN` applies to operational fields only:

- `input_effect`
- `output_effect`

Allowed in `satirical_text`:

- `TODO`
- unfinished jokes
- trash goblin theater

Forbidden in operational fields:

- `TODO`
- `TBD`
- `PLACEHOLDER`
- `REPLACE_ME`
- unresolved fake hashes

## 6. Exit semantics

| Replay result | Exit code |
|---|---:|
| Match | `0` |
| Mismatch | `1` |

## 7. Bridge rule

Cards can lie.  
Receipts decide.  
Authority remains `false`.
