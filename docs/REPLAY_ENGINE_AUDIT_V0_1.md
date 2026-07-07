# Replay Engine Audit v0.1.1

## 1. Baseline

**Release tag:** `v0.1.1-executable-replay`

**Tag SHA:** `e0907d0667f6c177c37305ed1601cd8058681779`

**Commit SHA:** `a7317adc11f81a33f2421d0e301b7060ff8c896b`

**Tree SHA-256:** `f9521099221a4118e9cfaa1f8bfefa6978d35f74fa6c02a332baff05aaee4e28`

**CLI blob:** `ab8bcd6902ad65d55f7a226011a8d04e99c29853`

**Test status:** `15 passed`

This audit records the executable replay baseline for ReceiptOS v0.1.1.

## 2. Scope

This audit covers:

- `receiptos manifest verify <path>`
- `receiptos replay run <path>`
- `schemas/receipt.schema.json`
- `schemas/manifest.schema.json`
- replay PASS and FAIL receipts
- manifest pre-flight failure gates
- canonical tree hash computation
- non-authority enforcement

It does not cover signatures, external anchors, remote attestations, or legal/institutional truth claims.

## 3. Canonical Tree Hash

The canonical tree hash is computed from deterministic Git tree surface output:

```text
git ls-tree -r --full-tree <commit>
sort lines
join with "\n"
encode UTF-8
sha256
```

No trailing newline is appended to the canonical form.

Reference implementation: `receiptos/cli.py::canonical_tree_sha256()`.

This exists to enforce `INV_DETERMINISTIC_OUTPUT` and prevent drift between Git raw tree objects and ReceiptOS replay surfaces.

## 4. Execution Chain

```text
manifest JSON
  -> receiptos manifest verify
  -> canonical_tree_sha256
  -> canonical surface checks
  -> receiptos replay run
  -> replay_run receipt JSON
```

Authority remains false throughout. ReceiptOS verifies replay surfaces and emits receipts; it does not declare legal truth, institutional authority, or factual finality.

## 5. Invariants

The executable replay baseline enforces these replay invariants:

- `INV_READ_ONLY_WORKSPACE`
- `INV_COMMIT_RESOLVABLE`
- `INV_TREE_HASH_MATCH`
- `INV_CANONICAL_SURFACES_PRESENT`
- `INV_DETERMINISTIC_OUTPUT`

Receipt-layer validation also enforces:

- `INV_SCHEMA_VALID`
- `INV_NON_AUTHORITY`
- `INV_FAILURE_EXPLICIT`

## 6. Gate Matrix

`pytest -q tests` reports `15 passed` at the sealed baseline.

### Receipt gates

| Gate | Expected exit | Meaning |
|---|---:|---|
| `schema_validate.valid.json` | 0 | Valid receipt schema |
| `valid/replay_run.valid.json` | 0 | Valid replay receipt |
| `version_mismatch.json` | 3 | Schema const failure |
| `authority_true.json` | 3 | Authority const failure |
| `hash_mismatch.json` | 4 | Tree hash failure |
| `bad_invariant.json` | 6 | Invariant registry failure |

### Manifest gates

| Gate | Expected exit | Meaning |
|---|---:|---|
| `manifest.valid.json` | 0 | Manifest pre-flight pass |
| `tree_hash_mismatch.json` | 4 | `INV_TREE_HASH_MATCH` failure |
| `commit_unresolvable.json` | 5 | `INV_COMMIT_RESOLVABLE` failure |
| `missing_surface.json` | 5 | `INV_CANONICAL_SURFACES_PRESENT` failure |

### Replay-run manifest gates

| Gate | Expected exit | Meaning |
|---|---:|---|
| valid manifest replay | 0 | Emits PASS `replay_run` receipt |
| tree hash mismatch replay | 4 | Emits FAIL receipt with `INV_TREE_HASH_MATCH` |
| commit unresolvable replay | 5 | Emits FAIL receipt with `INV_COMMIT_RESOLVABLE` |
| missing surface replay | 5 | Emits FAIL receipt with `INV_CANONICAL_SURFACES_PRESENT` |

## 7. Receipt Schema Compliance

All `replay_run` receipts conform to `schemas/receipt.schema.json` v0.1.

Required fields:

- `receipt_version`: `0.1`
- `receipt_type`: `replay_run`
- `authority`: `false`
- `engine_id`: `receiptos-replay-engine`
- `engine_version`: `0.1`
- `replay_invariants`: non-empty invariant list
- `timestamp`: ISO-8601 UTC execution time
- `input_hash`: SHA-256 of manifest bytes
- `output_hash`: canonical `tree_sha256`
- `status`: `PASS` or `FAIL`
- `exit_code`: canonical CLI exit code
- `errors`: empty on PASS, explicit invariant signal on FAIL

## 8. CLI Contract

### `receiptos manifest verify <path>`

- Input: manifest JSON
- Output on PASS: JSON to stdout
- Output on FAIL: JSON to stderr
- Exits: `0`, `3`, `4`, `5`
- Does not emit a receipt

### `receiptos replay run <path>`

- Input: manifest JSON
- Output: `replay_run` receipt JSON to stdout
- Exits: `0`, `3`, `4`, `5`
- Emits PASS or FAIL receipt

## 9. Known Issues

1. `manifest_verify` stderr can leak before `replay_run` emits its FAIL receipt. Tests pass because replay receipts are asserted from stdout. v0.2 should add `quiet=True` or internal structured return values.
2. Manifests are unsigned. Trust currently derives from repository access control and Git history. v0.2 should add `manifest sign` and signature verification.
3. `INV_READ_ONLY_WORKSPACE` is represented in replay receipts, but deeper mutation detection should be expanded in v0.2.

## 10. Provenance

- **Tag:** `v0.1.1-executable-replay`
- **Tag SHA:** `e0907d0667f6c177c37305ed1601cd8058681779`
- **Commit SHA:** `a7317adc11f81a33f2421d0e301b7060ff8c896b`
- **Tree SHA-256:** `f9521099221a4118e9cfaa1f8bfefa6978d35f74fa6c02a332baff05aaee4e28`
- **CLI blob:** `ab8bcd6902ad65d55f7a226011a8d04e99c29853`
- **Tests:** `15 passed`

All future v0.1.1 replay claims should cite this baseline or a later explicitly versioned successor.

## 11. Conclusion

`v0.1.1-executable-replay` satisfies the ReceiptOS provenance boundary at this layer:

1. Deterministic canonical tree hashing
2. Non-authoritative receipts with `authority:false`
3. Explicit PASS and FAIL receipt emission
4. Manifest pre-flight verification
5. Fifteen executable gates covering schema, manifest, replay, and invariant failures

This baseline is immutable. Any change to canonical tree hashing, receipt schema, manifest schema, or replay receipt semantics requires a version bump.

---

End of Audit v0.1.1
