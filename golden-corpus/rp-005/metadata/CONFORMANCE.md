# RP-005 Conformance Contract

**Status:** FROZEN (v1.0.0)
**Profile:** A (RFC 8785 JCS)
**Standard:** RP-005/v1.0

This document is the immutable conformance contract for the RP-005 golden corpus.
Implementations MUST verify against this contract; they MUST NOT reverse-engineer
expectations solely from vector contents.

---

## 1. Required Manifest Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | yes | Must be `"rp-005"` |
| `profile` | string | yes | Must be `"A"` |
| `version` | string | yes | Corpus version (semver) |
| `standard` | string | yes | Must be `"RP-005/v1.0"` |
| `families` | string[] | yes | Ordered: `valid`, `invalid`, `edge`, `regression` |
| `vectors` | string[] | yes | Relative paths to each `expected.json` |
| `root_hash` | string | yes | 64-char lowercase hex SHA-256 of sealed vector set |

Keys MUST be sorted lexicographically (JCS). Encoding: UTF-8. Newlines: LF only.

---

## 2. Directory Ordering

Families appear in this fixed order:

1. `valid/`
2. `invalid/`
3. `edge/`
4. `regression/`

Within a family, vector directories are ordered lexicographically by directory name.
Each vector directory contains exactly:

- `input.json`
- `expected.json`

No other files are permitted inside a vector directory for the sealed corpus.

---

## 3. Canonical JSON Serialization (Profile A)

- RFC 8785 JSON Canonicalization Scheme (JCS)
- UTF-8 encoding
- LF (`\n`) line endings only; no CR
- Object keys sorted lexicographically
- No insignificant whitespace beyond JCS rules
- Trailing newline permitted on committed files for POSIX compatibility;
  hash inputs use the exact committed byte sequences

---

## 4. Exit Code Registry

| Code | Meaning |
|------|---------|
| `0` | Acceptance (valid / successful regression) |
| `65` | Rejection (invalid or edge diagnostic failure) |

No other exit codes are defined for RP-005 v1.0 harness runs.

---

## 5. Diagnostic Identifier Registry

| `reason` | When |
|----------|------|
| `ok` | Acceptance |
| `missing_required_field` | Required field absent |
| `empty_payload` | Empty object / zero-content payload |

Additional reasons MAY be added only via a new corpus version; existing reasons
are immutable under v1.0.0.

---

## 6. Replay ID Requirements

- Field name: `replay_id`
- Format: UUIDv7 (RFC 9562) string representation
- MUST be deterministic for a given vector (fixed in the sealed corpus)
- MUST NOT be randomly generated at harness runtime for golden vectors

---

## 7. Hash Computation Algorithm

### Per-file digest

```
SHA-256(exact committed file bytes)
```

Output: lowercase hex, 64 characters.

### Root hash

1. Collect every sealed vector file path relative to repository root:
   - `.../input.json` and `.../expected.json` for each vector
2. Sort paths lexicographically (byte order, UTF-8)
3. For each path, form the record:
   ```
   path || 0x00 || sha256_hex || 0x0A
   ```
4. Concatenate all records in sorted order
5. `root_hash = SHA-256(concatenation)` as lowercase hex

Manifest itself is **excluded** from the root hash input so that binding the
hash into `manifest.json` does not create a circular dependency.

---

## 8. Sealing Procedure

1. Canonicalize every JSON file under the four families (Profile A).
2. Compute per-file SHA-256 over exact committed bytes.
3. Build deterministic path ordering (section 7).
4. Compute `root_hash`.
5. Write `root_hash` into `manifest.json` (keys sorted).
6. Recompute `root_hash` independently; confirm identical value.
7. Commit sealed `manifest.json` and this contract.
8. Tag or mark release state as sealed only after step 6 passes.

---

## 9. Expected Object Shape

| Field | Type | Notes |
|-------|------|-------|
| `spec` | string | `"RP-005"` |
| `spec_revision` | string | e.g. `"1.0.0"` |
| `vector` | string | Case id |
| `vector_revision` | string | Case revision |
| `family` | string | One of the four families |
| `valid` | bool | Pass/fail |
| `exit_code` | int | `0` or `65` |
| `reason` | string | From diagnostic registry |
| `failed_field` | string\|null | Set on structural failures |
| `canonical_file` | string\|null | Usually `"input.json"` when accepted |
| `sha256` | string\|null | Optional per-vector digest slot |

Keys sorted lexicographically.

---

## 10. Non-Goals (v1.0.0)

- Cryptographic signatures over the corpus
- Authority claims
- Network or time-dependent vectors
- Non-deterministic replay IDs
