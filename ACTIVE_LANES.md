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
- CANONICAL_METADATA — fid plus full Farcaster castHash plus timestamp obtained
- CANONICAL_BYTES — raw_text retrieved from Hub by this verifier
- HASH_MATCH — SHA-256(raw_text) equals frozen_hash
- INDEPENDENT_REPLAY — This verifier executed full Hub fetch plus compute
- HUB_ENDPOINT_USED — Specific Hub node queried
- REPLAY_TIMESTAMP — When this verifier ran replay
- NETWORK_RESOLUTION_FAILED — Verifier could not resolve or reach the configured Hub endpoint

### HubReplayEngine

Input:

```text
{ fid: uint64, hash: full Farcaster cast hash }
```

For current Farcaster casts observed in TNTR-007, the full cast hash is 20 bytes / 40 hex characters after `0x`, for example:

```text
0x3e909b0a97acb3b65a3b9547802ce5b7940e48ab
```

Do not hard-code a single Hub hostname. The Hub endpoint must be verifier-configurable:

```text
HUB_ENDPOINT={configured_hub_base_url}
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

### Safe-Failure Reasons

- canonical_metadata_unavailable — FID, full cast hash, timestamp, or replay metadata cannot be obtained
- hub_replay_404 — Configured Hub endpoint returns not found for the provided identifiers
- hash_mismatch — Retrieved canonical text does not match the expected frozen hash
- invalid_verifier — Verifier metadata is malformed or unverifiable
- network_resolution_failed — Verifier cannot resolve or reach the configured Hub endpoint

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
hash: full Farcaster cast hash as returned by Hub/client
hub: verifier-configured Hub endpoint
```

authority: false

---

## EXT-008 — MULTI_HUB_FALLBACK

### Purpose

EXT-008 defines how a verifier attempts multiple configured Hub endpoints without turning infrastructure reachability into a truth claim about the artifact.

### Input

```text
fid: {numeric}
hash: full Farcaster cast hash as returned by Hub/client
hub_candidates: ordered list of verifier-configured Hub endpoints
```

### Evidence Bundle Additions

- HUB_CANDIDATE_LIST — Ordered Hub endpoints attempted by this verifier
- HUB_ATTEMPT_RESULT — Per-endpoint result including HTTP status, curl exit code, and error text when available
- MULTI_HUB_UNREACHABLE — All configured Hub endpoints failed due to DNS, connection, TLS, or timeout failure
- FIRST_SUCCESSFUL_HUB — First endpoint returning valid Hub JSON for the requested fid/hash

### Algorithm

1. Iterate over `hub_candidates` in declared order.
2. For each Hub, request `{hub}/v1/castById?fid={fid}&hash={hash}`.
3. Record endpoint, HTTP status, exit code, stderr, and response hash.
4. Stop at the first endpoint returning parseable Hub JSON containing canonical cast data.
5. If no endpoint returns canonical JSON, emit `MULTI_HUB_UNREACHABLE` or the most precise safe-failure reason.
6. Do not emit `RAW_PASS` unless canonical bytes are retrieved and independently hashed by this verifier.

### Safe-Failure Reasons

- multi_hub_unreachable — No configured Hub endpoint was reachable by this verifier
- hub_candidate_dns_failed — One configured Hub endpoint failed DNS resolution
- hub_candidate_http_error — One configured Hub endpoint returned a non-success HTTP status
- hub_candidate_invalid_json — One configured Hub endpoint returned unparsable JSON

### TNTR-007 Multi-Hub Attempt

Observed identifiers:

```text
fid: 1432701
hash: 0x01e26d779d81e689ed1c9afa6150fc8bace19fc2
```

Attempted Hub endpoints:

```text
https://hub.farcaster.xyz
http://hub.farcaster.xyz:2281
http://nemes.farcaster.xyz:2281
```

Observed result from Cloud Shell:

```text
curl: (6) Could not resolve host: hub.farcaster.xyz
HTTP:000
curl: (6) Could not resolve host: hub.farcaster.xyz
HTTP:000
curl: (6) Could not resolve host: nemes.farcaster.xyz
HTTP:000
```

Classification:

```text
network_resolution_failed
multi_hub_unreachable
```

TNTR-007 state:

```text
FETCHABLE_CANDIDATE
Local Evidence: FID_OBTAINED + CAST_HASH_CANDIDATE + MULTI_HUB_UNREACHABLE
RAW_PASS: not emitted
authority: false
```

### EXT-008 Invariant

Endpoint failure is infrastructure evidence, not artifact evidence. A verifier may report that its configured endpoints failed; it may not conclude that the cast does not exist or that other verifiers cannot replay it.
