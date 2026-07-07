# Replay Engine v0.1 Specification

ReceiptOS Replay Engine v0.1 defines the behavior required to replay Git-tracked evidence surfaces against committed manifests, schemas, and invariants.

This document is behavioral, not implementation-specific. It does not prescribe language, runtime, package manager, hosting provider, or external attestation layer.

## Engine Identity

Every replay receipt produced under this specification MUST identify the engine and invariant set used.

```json
{
  "engine_id": "REPLAY_ENGINE_V0_1",
  "engine_version": "0.1.0",
  "replay_invariants": {
    "id": "REPLAY_INVARIANTS_V0_1",
    "version": "0.1.0"
  },
  "authority": false
}
```

## Scope

Replay Engine v0.1 operates only on Git-tracked content in the target repository.

For ReceiptOS Base v0.1, the target repository is:

```text
jsonwisdom/receiptos-base
```

Primary inputs:

- manifest JSON file
- local clone with full Git history
- canonical receipt schema
- replay invariants document
- standard Git object database

External systems are optional witnesses only.

Examples of optional witnesses:

- EAS attestations
- IPFS CIDs
- block explorers
- third-party API observations
- external model verification

External systems MUST NOT be required for replay correctness.

## Read-Only Replay Requirement

Replay Engine v0.1 MUST be read-only with respect to the user's working tree.

The engine SHOULD use read-only Git commands such as:

```text
git rev-parse <commit_sha>
git cat-file -t <commit_sha>
git ls-tree -r <commit_sha>
git show <commit_sha>:<path>
```

The engine MUST NOT require `git checkout <commit_sha>` against the user's active working tree.

If file materialization is required, the engine MAY use an ephemeral worktree or temporary directory, provided the user's current branch and working tree are not mutated.

## Replay Pipeline

### 1. Load manifest

Input: path to manifest JSON.

Required checks:

- JSON parses successfully
- required manifest keys are present
- `authority` is false
- `mutable_context_excluded` is true
- referenced `commit_sha` is present
- referenced `tree_sha256` is present when required by manifest version

Failure emits `replay_failure`.

### 2. Resolve commit

The engine MUST verify that the manifest `commit_sha` resolves to a valid Git commit object.

Recommended commands:

```text
git rev-parse <commit_sha>
git cat-file -t <commit_sha>
```

Expected object type:

```text
commit
```

Failure emits `replay_failure` with failed invariant:

```text
INV_5_COMMIT_SHA_RESOLUTION
```

### 3. Verify deterministic tree hash

The engine MUST compute SHA-256 over a deterministic tree listing.

Canonical tree command for v0.1:

```text
git ls-tree -r <commit_sha>
```

The exact byte output of this command, as emitted by Git in the replay environment, is the v0.1 tree hash input.

The computed SHA-256 MUST match manifest `tree_sha256`.

Failure emits `replay_failure` with failed invariant:

```text
INV_6_TREE_SHA256_MATCH
```

### 4. Verify canonical surfaces

The engine MUST verify the presence of canonical files referenced by the current replay layer.

For ReceiptOS Base v0.1, required surfaces include:

```text
constitution/RECEIPTOS_PROVENANCE_BOUNDARY_V0_1.md
docs/REPLAY_INVARIANTS_V0_1.md
schemas/receipt.schema.json
```

The engine SHOULD verify these files using:

```text
git show <commit_sha>:<path>
```

or equivalent read-only object database access.

Missing required surfaces emit `replay_failure`.

### 5. Validate schema

The engine MUST validate derived receipts against the canonical schema:

```text
schemas/receipt.schema.json
```

A receipt that fails schema validation MUST NOT be promoted as a successful receipt.

Schema failure emits `replay_failure`.

### 6. Promote receipt

If all required checks pass, the engine emits `replay_success`.

If any invariant fails, the engine emits `replay_failure`.

The engine MUST NOT fail silently.

## Success Receipt

A successful replay emits a structured JSON object containing at minimum:

```json
{
  "receipt_type": "replay_success",
  "engine_id": "REPLAY_ENGINE_V0_1",
  "engine_version": "0.1.0",
  "replay_invariants": {
    "id": "REPLAY_INVARIANTS_V0_1",
    "version": "0.1.0"
  },
  "manifest_id": "<manifest_id>",
  "repo": "jsonwisdom/receiptos-base",
  "commit_sha": "<commit_sha>",
  "tree_sha256": "<tree_sha256>",
  "authority": false,
  "mutable_context_excluded": true,
  "checks_passed": [],
  "replay_command": "<canonical command sequence>",
  "observed_at": "<ISO-8601 timestamp>"
}
```

The success receipt asserts only that the replayed Git state matched the manifest and invariants.

It does not assert external truth.

## Failure Receipt

Every invariant violation emits a structured JSON failure receipt.

A failure receipt contains at minimum:

```json
{
  "receipt_type": "replay_failure",
  "engine_id": "REPLAY_ENGINE_V0_1",
  "engine_version": "0.1.0",
  "replay_invariants": {
    "id": "REPLAY_INVARIANTS_V0_1",
    "version": "0.1.0"
  },
  "manifest_id": "<manifest_id_or_null>",
  "repo": "jsonwisdom/receiptos-base",
  "commit_sha": "<commit_sha_or_null>",
  "authority": false,
  "mutable_context_excluded": true,
  "failed_invariant_id": "<invariant_id>",
  "expected": "<expected value or condition>",
  "actual": "<observed value or error>",
  "replay_step": "<pipeline step>",
  "replay_command": "<command or step that failed>",
  "observed_at": "<ISO-8601 timestamp>"
}
```

Failure receipts preserve evidence of failure. They are not passing receipts.

## External Attestations

External attestations MAY be included as witness references in replay receipts.

External witness examples:

- EAS UID
- IPFS CID
- block explorer URL
- external verification transcript
- third-party API response hash

External witness references MUST NOT be required for local replay success.

External witnesses do not override failed local replay.

## Determinism Requirements

All operations that feed tree hashes or receipt fields MUST be representation-stable.

Replay Engine v0.1 MUST document:

- exact Git commands used
- exact manifest path used
- exact schema path used
- exact invariant version used
- exact hash algorithm used

The required hash algorithm for tree binding in v0.1 is:

```text
SHA-256
```

## Non-Goals

Replay Engine v0.1 does not:

- validate legal truth
- validate market truth
- validate institutional endorsement
- require EAS
- require IPFS
- require block explorers
- require mutable GitHub metadata
- mutate the user's active working tree

## Canonical Summary

```json
{
  "engine_id": "REPLAY_ENGINE_V0_1",
  "engine_version": "0.1.0",
  "authority": false,
  "local_first": true,
  "read_only": true,
  "mutable_context_excluded": true,
  "external_attestations_are_witnesses_only": true,
  "failure_receipts_required": true
}
```
