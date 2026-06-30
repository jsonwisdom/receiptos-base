# ACTIVE_LANES v2 Constitutional Boundary

GREEN means: receipt verified, hash matches, replay succeeds, authority=false.
GREEN does not mean: the underlying claim is true.

Timestamp, not tribunal.

This boundary is load-bearing. ACTIVE_LANES records provenance and replay status, not truth authority. Downstream lanes inherit this invariant by default.

LANE: AL
STATUS: GREEN
STATUS_SOURCE: VERIFIED_RECEIPT
RECEIPT_PTR: sha256:22b00da22b00da22b00da22b00da22b00da22b00da22b00da22b00da22b00da
authority: false

LANE: CWaaS
STATUS: YELLOW
STATUS_SOURCE: REPORTED
RECEIPT_PTR: NULL
authority: false

LANE: PRC-JRN-EXT-001
STATUS: YELLOW
STATUS_SOURCE: REPORTED
RECEIPT_PTR: NULL
authority: false

---

## EXT-007 — HUB_REPLAY_AUTOMATION

### Artifact States

- DISCOVERED — Reference located
- FETCHABLE — Canonical identifiers available to at least one verifier
- FROZEN — Canonical bytes captured by at least one verifier
- RAW_PASS — One or more verifier completed independent replay
- QUERYABLE — Two or more distinct verifiers reached RAW_PASS
- QUARANTINE — Failed integrity check
- UNREPLAYABLE — Source requires JS/execution or returns 404

### Evidence Bundle, Per Verifier

- URL_ONLY — Link present, no protocol IDs
- CANONICAL_METADATA — fid plus full 32-byte castHash plus timestamp obtained
- CANONICAL_BYTES — raw_text retrieved from Hub by this verifier
- HASH_MATCH — SHA-256(raw_text) equals frozen_hash
- INDEPENDENT_REPLAY — This verifier executed full Hub fetch plus compute
- HUB_ENDPOINT_USED — Specific Hub node queried
- REPLAY_TIMESTAMP — When this verifier ran replay

### HubReplayEngine

Input:

```text
{ fid: uint64, hash: 0x[64_hex] }
```

Output:

```text
Evidence Bundle | ERROR
```

Steps:

1. GET `{hub}/v1/castById?fid={fid}&hash={hash}`
2. Extract `text`, `timestamp`, `author_fid`, and `hash` from response
3. Compute `sha256 = SHA-256(UTF-8 bytes of text)`
4. Emit `CANONICAL_METADATA`, `CANONICAL_BYTES`, `HASH_MATCH` if matched, and `INDEPENDENT_REPLAY`

### Anti-Tribunal Invariants

1. No Inherited Evidence: Verifier A cannot use Verifier B's `CANONICAL_BYTES`
2. No Truth Judgment: `RAW_PASS` attests existence, not veracity
3. Stop is Valid: `BLOCKED_INSUFFICIENT_EVIDENCE` is a terminal state for that verifier
4. Audit Everything: Every transition cites the evidence element that enabled it

### Derivation Rule

```text
URL → DISCOVERED + URL_ONLY → need CANONICAL_METADATA → need INDEPENDENT_REPLAY → RAW_PASS
```

Required canonical input:

```text
fid: {numeric}
hash: 0x{64_hex_chars}
```

authority: false
