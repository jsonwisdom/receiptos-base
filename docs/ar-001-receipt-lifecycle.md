# AR-001 Design Contract: Receipt Lifecycle

## 1. State Machine

```text
CREATED -> CANONICALIZED -> HASHED -> SIGNED -> EMITTED
                                                   |
                                                   v
REPLAYED -> { VERIFIED | MISMATCHED }
```

Receipts are append-only by design. Deletion is out of scope for v0 and is detectable through chain breaks.

- **CREATED**: Raw inputs, outputs, and captured context are assembled.
- **CANONICALIZED**: JCS is applied to sub-objects and the full receipt.
- **HASHED**: `content_hash` is computed and becomes `receipt_id`.
- **SIGNED**: Full receipt minus the `signature` field is signed.
- **EMITTED**: Receipt is appended through `parent_hash`.
- **REPLAYED**: Replay recomputes `content_hash`. Replay terminal states only.

## 2. Canonicalization

Use JCS, RFC 8785.

Prefer integers and strings over floats.

Canonicalization uses two passes:

1. Sub-object canonicalization for replay-relevant material.
2. Full receipt canonicalization for signing.

## 3. content_hash Preimage

```json
content_hash = SHA-256(JCS({
  "inputs": inputs,
  "outputs": outputs,
  "captured_context": captured_context,
  "policy_hash": policy_hash,
  "manifest_hash": manifest_hash,
  "parent_hash": parent_hash
}))
```

`policy_hash` is the hash of the serialized ruleset at evaluation time. This creates a dependency on the minimal AR-002 definition.

The `content_hash` preimage excludes:

- `timestamp`
- `signature`
- `receipt_id`
- `policy_result`

Hash format:

- SHA-256
- lowercase hex
- encoded as `sha256:<hex>` when stored in the receipt

## 4. Signature Envelope

```json
"signature": {
  "scheme": "ed25519",
  "public_key": "hex lowercase",
  "value": "base64 signature over JCS(receipt minus signature field)"
}
```

The top-level `timestamp` is recording time and is non-replayable.

## 5. Failure Modes

| Failure | Detection | Terminal |
|---|---|---|
| Missing `captured_context` for nondeterministic material | Replay | `MISMATCHED` |
| `content_hash` mismatch | Replay | `MISMATCHED` |
| Invalid signature | Verification | `REJECTED` |
| `policy_hash` mismatch | Verification | `STALE` |
| Malformed JSON | Parse | `REJECTED` |

`REJECTED` and `MISMATCHED` are distinguished for consumer rendering.

Manifest completeness is self-attested and remains an explicit limitation.

## Out of Scope

- Live re-execution
- External honesty
- Policy quality
