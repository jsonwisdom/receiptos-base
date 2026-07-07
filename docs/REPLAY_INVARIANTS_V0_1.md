# Replay Invariants v0.1

ReceiptOS replay exists to verify Git-tracked evidence surfaces and deterministic replay outputs. It does not assert external truth, legal status, institutional authority, or mutable repository metadata.

## Invariants

### 1. Local-first replay

Replay MUST be executable using only Git-tracked content and standard Git operations.

External services may assist as witnesses, but they MUST NOT be required for correctness.

### 2. Git-state verification

Replay verifies repository state.

Replay checks whether the repository state matches the manifest, schema, and expected deterministic outputs.

Replay does NOT assert external truth, factual correctness, legal truth, market truth, or institutional authority.

### 3. Mutable metadata exclusion

Repository metadata is NOT evidence unless committed.

Examples of mutable metadata include:

- GitHub repository description
- GitHub topics
- GitHub stars, forks, watchers, and issue counts
- GitHub issues and pull requests
- GitHub branch protection settings
- social preview images
- external summaries from third-party systems

Mutable metadata MAY be cited as context only if labeled as mutable context.

Mutable metadata MUST NOT be promoted into SHA-bound evidence unless it is captured, hashed, committed, and replayable.

### 4. Mandatory authority=false

Replay MUST preserve `authority=false`.

Replay asserts reproducibility, not authority.

A replay result MUST NOT claim legal force, institutional endorsement, official status, or truth authority.

### 5. Manifest commit_sha resolution

The `commit_sha` declared in a manifest MUST resolve to an actual commit in the target repository.

Failure to resolve the commit is a replay failure.

### 6. Deterministic tree_sha256 matching

The `tree_sha256` declared in a manifest MUST match the SHA-256 of deterministic `git ls-tree -r <commit_sha>` output.

The replay engine MUST define and use one stable serialization method for tree output.

Any mismatch between the computed tree hash and declared tree hash is a replay failure.

### 7. Schema validation required

Receipts MUST validate against the canonical schema before promotion.

A receipt that fails schema validation MUST NOT be promoted as a passing receipt.

Schema failure MUST produce a failure receipt.

### 8. Failure receipt emission

Replay MUST emit a structured failure receipt on invariant violation.

A failure receipt MUST include:

- failed invariant identifier
- expected value
- actual value
- artifact path or commit reference
- reproducible replay command or step
- `authority=false`

Replay MUST NOT fail silently.

### 9. External attestations as witnesses

External attestations MAY serve as witnesses.

Examples include:

- EAS attestations
- IPFS CIDs
- external model verification
- user-provided transcript receipts
- third-party API observations

External attestations MUST NOT be required for local replay correctness.

Local replay remains the first verification surface.

## Canonical Summary

```json
{
  "invariants_id": "REPLAY_INVARIANTS_V0_1",
  "authority": false,
  "local_first": true,
  "mutable_context_excluded": true,
  "external_attestations_are_witnesses_only": true,
  "failure_receipts_required": true
}
```

## Build Order Constraint

Replay engine logic MUST NOT expand beyond these invariants without a new invariant version.

Engine behavior must be traceable back to this document.
