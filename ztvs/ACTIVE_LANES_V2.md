# ACTIVE_LANES.md v2 Replay Schema

Status: draft-operational
Authority: false
Layer: ZTVS / replay plane
Purpose: make lane status admissible by separating claim, provenance, and receipt anchor.

## Governing Invariant

ACTIVE_LANES.md v2 is not a human-interpreted status sheet. It is a replay-consumable object.

The governing triad is:

- `STATUS` — the claim
- `STATUS_SOURCE` — the provenance boundary
- `RECEIPT_PTR` — the immutable anchor

Downstream systems must consume `AUDITOR_VIEW`, not `STATUS`.

## Lane Entry Schema

```text
LANE: <string>
STATUS: <GREEN | YELLOW | RED | NULL>
STATUS_SOURCE: <VERIFIED_RECEIPT | REPORTED | INFERRED | NULL>
RECEIPT_PTR: <sha256:... | tx:... | eas:... | pr:... | NULL>
```

## STATUS Semantics

- `GREEN` — lane claims operational readiness.
- `YELLOW` — lane claims partial, degraded, pending, or incomplete state.
- `RED` — lane claims blocked, failed, rejected, or unsafe state.
- `NULL` — no lane status claim is made.

`STATUS` alone is never admissible.

## STATUS_SOURCE Semantics

- `VERIFIED_RECEIPT` — replay validated, hash-bound, admissible.
- `REPORTED` — human or system claim without verified receipt.
- `INFERRED` — derived from architecture, continuity graph, or neighboring state.
- `NULL` — no claim, no inference, no provenance.

## RECEIPT_PTR Semantics

`RECEIPT_PTR` must be content-addressed or replay-resolvable.

Allowed forms:

- `sha256:<64hex>` — content hash for commit, artifact, or frozen receipt.
- `tx:<0xhash>` — on-chain transaction hash.
- `eas:<uid>` — EAS attestation UID.
- `pr:<number>` — GitHub PR identifier after merge.
- `NULL` — no receipt pointer exists.

Rejected forms:

- symbolic labels such as `RENDER_BUILD_05_26`
- informal names
- unstamped local filenames
- mutable URLs without digest or replay binding
- unmerged PR labels represented as admissible receipts

## Derived Field: AUDITOR_VIEW

`AUDITOR_VIEW` is computed deterministically.

```text
if STATUS == GREEN and STATUS_SOURCE == VERIFIED_RECEIPT:
  AUDITOR_VIEW = VERIFIED_GREEN
elif STATUS == GREEN and STATUS_SOURCE != VERIFIED_RECEIPT:
  AUDITOR_VIEW = REPORTED_UNVERIFIED
elif STATUS_SOURCE == INFERRED:
  AUDITOR_VIEW = INFERRED_UNVERIFIED
elif STATUS == NULL:
  AUDITOR_VIEW = NO_STATUS
else:
  AUDITOR_VIEW = NON_GREEN_REPORTED
```

Downstream systems must consume `AUDITOR_VIEW` rather than raw `STATUS`.

## GREEN_PENDING Rule

UX may display green for operator ergonomics, but the audit layer must classify:

```text
STATUS=GREEN
STATUS_SOURCE!=VERIFIED_RECEIPT
```

as:

```text
AUDITOR_VIEW=REPORTED_UNVERIFIED
UX_ALIAS=GREEN_PENDING
```

This preserves usability without promoting reported status into verified status.

## ZTVS Chain

The schema enforces:

```text
Origin -> not proof
Claim -> not proof
Receipt -> not proof until replay
Replay -> only admissible validator
```

## Replay Loop

1. Pointer check
   - If `RECEIPT_PTR=NULL`, classify as `REPORTED_UNVERIFIED` unless `STATUS=NULL`.

2. Fetch
   - Resolve pointer to bytes or replay-resolvable record.
   - Fail if pointer is symbolic or mutable without binding.

3. Hash-bind
   - Recompute digest when applicable.
   - Mismatch becomes `TAMPERED`.

4. Replay
   - Execute oracle or receipt validation rules.
   - Derive admissible state.

5. Drift detection
   - Compare `STATUS` against computed `AUDITOR_VIEW`.
   - Flag delta as `DELTA_H`.

## CI Validation Rules

A lane file fails validation if:

- `STATUS` is outside the allowed enum.
- `STATUS_SOURCE` is outside the allowed enum.
- `RECEIPT_PTR` is symbolic when `STATUS_SOURCE=VERIFIED_RECEIPT`.
- `STATUS_SOURCE=VERIFIED_RECEIPT` and `RECEIPT_PTR=NULL`.
- `STATUS=GREEN` is consumed directly by downstream code without `AUDITOR_VIEW`.
- `authority=true` appears anywhere in the lane object.
- `AUDITOR_VIEW` is manually supplied instead of computed.
- `RECEIPT_PTR` claims `pr:<number>` before merge confirmation.

## Example Lanes

```text
LANE: prc-jrn-ext-001
STATUS: GREEN
STATUS_SOURCE: REPORTED
RECEIPT_PTR: NULL
```

Computed:

```text
AUDITOR_VIEW: REPORTED_UNVERIFIED
UX_ALIAS: GREEN_PENDING
```

```text
LANE: bootstrap-runtime
STATUS: GREEN
STATUS_SOURCE: VERIFIED_RECEIPT
RECEIPT_PTR: sha256:1f39208fe9aa948dde45cbea325719ea44885c66aaaaaaaaaaaaaaaaaaaaaaaa
```

Computed:

```text
AUDITOR_VIEW: VERIFIED_GREEN
```

```text
LANE: inferred-continuity-graph
STATUS: YELLOW
STATUS_SOURCE: INFERRED
RECEIPT_PTR: NULL
```

Computed:

```text
AUDITOR_VIEW: INFERRED_UNVERIFIED
```

## Replay Plane Requirement

ACTIVE_LANES.md v2 must itself be hashable, diffable, replayable, drift-checkable, and continuity-verifiable.

No reported lane state becomes admissible until a replay engine verifies the receipt pointer.

Authority remains false.
