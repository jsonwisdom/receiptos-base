# ReceiptOS Base — Mathematical Model

**Version**: 0.2.0  
**Status**: Living Document  
**authority**: false  
**Last Updated**: 2026-07-08

## Core Principle

No evidence, no card.  
No CID, no drop.  
No replay, no claim.  
No fake green.

ReceiptOS is not a source of authority. ReceiptOS is a deterministic binder for evidence, identity anchors, hashes, transitions, and replayable publication surfaces.

## State Machine: Deterministic Lifecycle

### States

- **OBSERVED** — Raw incident, audit note, operator observation, or candidate evidence.
- **CAPTURED** — Evidence attached, such as logs, screenshots, EAS records, IPFS CIDs, or JSON outputs.
- **CLASSIFIED** — Evidence tagged by series, type, severity, surface, or failure mode.
- **PACKAGED** — Canonical JSON receipt packet created.
- **HASHED** — Deterministic `core_hash` computed from immutable receipt core.
- **PINNED** — Content-addressed CID minted and verified.
- **ATTESTED** — EAS or equivalent attestation anchored.
- **APPROVED** — Human operator or ApprovalGate review completed.
- **VARIANT_GENERATED** — Derived publication or social variants created from the approved core.
- **PUBLISHED** — Live publication surface created, such as Zora, X, GitHub release, or other target.
- **REPLAYED** — Receipt independently replayed or revalidated.
- **ARCHIVED** — Final record closed as immutable history.
- **REJECTED** — Evidence insufficient or malformed.
- **DISPUTED** — Counter-evidence raised.
- **EVIDENCE_REVIEW** — Disputed evidence under review before approval or rejection.

### Canonical Transition Path

```text
OBSERVED
→ CAPTURED
→ CLASSIFIED
→ PACKAGED
→ HASHED
→ PINNED
→ ATTESTED
→ APPROVED
→ VARIANT_GENERATED
→ PUBLISHED
→ REPLAYED
→ ARCHIVED
```

### Allowed Exception Transitions

```text
Any non-terminal state → REJECTED
Any non-terminal state → DISPUTED
DISPUTED → EVIDENCE_REVIEW
EVIDENCE_REVIEW → REJECTED
EVIDENCE_REVIEW → APPROVED
EVIDENCE_REVIEW → ARCHIVED
REJECTED → ARCHIVED
PUBLISHED → REPLAYED
REPLAYED → ARCHIVED
```

### Forbidden Transitions

- `PUBLISHED` without `PINNED` and `ATTESTED`.
- `VARIANT_GENERATED` before `APPROVED`.
- `ATTESTED → VARIANT_GENERATED` without approval gate.
- Any mutation of receipt core fields after `ATTESTED`.
- Card creation without an evidence anchor.
- CID-free publication.
- `authority=true` at any point.
- Terminal state escape from `ARCHIVED`.

### Terminal States

- `ARCHIVED`

`REJECTED` is terminal for claim promotion but may transition to `ARCHIVED` for record closure.

## Invariants

- `authority` is always literal `false`.
- `receipt_id` is a deterministic SHA-256 hash of canonical receipt core.
- Immutable receipt core is separated from mutable publication metadata.
- Every transition must emit, reference, or preserve a receipt.
- Variants may not introduce new claims beyond anchored evidence.
- UI observations are evidence, not authority.
- Assistant outputs are evidence candidates, not authority.
- GitHub records governance history but does not become truth.
- On-chain identity anchors bind identity but do not become unilateral authority.

## Hashing Rules

ReceiptOS v0.2 uses a restricted canonical JSON profile:

- Stable key ordering.
- Compact JSON separators.
- Unicode NFC normalization before canonical serialization.
- Deterministic hashing over immutable `receipt_core` only.
- Mutable publication metadata is excluded from core hash.

```text
receipt_id = sha256(canonical_json(receipt_core))
core_hash  = receipt_id
```

Excluded from receipt core unless explicitly versioned:

- `receipt_id`
- `core_hash`
- `hashes`
- `variants`
- `approval_status`
- `publish_targets`
- `replay_status`
- `created_at`
- `updated_at`
- `previous_receipt`
- `cid`
- publication URLs
- replay counters
- circular commitment fields such as `birth_witness.witness_hash` and `custody.chain_head`

## Agent Boundaries

All agents are narrow workers. No agent receives general authority.

Required agent classes:

- `IntakeAgent`
- `ClassifierAgent`
- `ReceiptPacketAgent`
- `HashAgent`
- `VariantAgent`
- `ApprovalGateAgent`
- `PublisherAgent`
- `ReplayAgent`
- `ArchiveAgent`

Each agent must define:

- Inputs
- Outputs
- Allowed actions
- Forbidden actions
- Failure modes
- Receipt emitted or referenced

## Phase 2: GCP Read-Only Rail

The GCP rail is an evidence intake membrane. It validates candidate Google Cloud observations without executing cloud commands in CI and without mutating cloud state.

Rules:

- Only explicitly allowlisted `gcloud` command paths are admissible.
- Commands must be tokenized as `Sequence[str]`.
- Raw shell strings are rejected.
- Shell metacharacters are rejected.
- `--format=json` is required.
- Mutating verbs are rejected.
- Key inventory reads are allowed only as `keys list`.
- Key creation, deletion, and rotation are forbidden.
- No credential creation.
- No IAM mutation.
- No API enablement.
- No deployment.
- No browser-only remediation.

Current GCP packet target:

```text
project_id: jaywisdom-boardroom
identity_anchor: jaywisdom.base.eth
operator_identity: jsonwisdom
```

The GCP rail may capture read-only JSON evidence such as:

- project metadata
- project IAM policy
- service account metadata
- service account key inventory
- enabled service inventory
- Cloud Run service inventory
- storage bucket metadata
- storage bucket IAM policy
- compute instance, disk, and network inventory

## Multifactor Attesting Rail

ReceiptOS may bind a receipt across multiple independent surfaces.

### 2FA: Two Factor Attesting

```text
Factor A: GitHub evidence surface
Factor B: jaywisdom.base.eth public identity surface
```

### 3FA: Three Factor Attesting

```text
Factor A: GitHub evidence surface
Factor B: jaywisdom.base.eth public identity surface
Factor C: Zora public publication/profile surface
```

A `THREE_FACTOR_ATTESTING_VERIFIED` packet requires GitHub, Base identity, and Zora surfaces to reference the same CID, EAS UID, receipt ID, core hash, or identity anchor.

No single surface becomes authority.

## Failure Classes

ReceiptOS should distinguish:

- `UI_FAILURE_NON_AUTHORITATIVE`
- `CLOUD_EVIDENCE_FAILURE`
- `OPERATOR_CONTEXT_FAILURE`
- `NON_DETERMINISTIC_OUTPUT_FAILURE`
- `MEMBRANE_VIOLATION_FAILURE`
- `SCHEMA_VALIDATION_FAILURE`
- `HASH_MISMATCH_FAILURE`
- `TRANSITION_VIOLATION_FAILURE`

## Future Connection

This model governs safe read-only Cloud Shell and `gcloud` audit prompts for projects such as `jaywisdom-boardroom`.

Future work:

- GCP packet validator.
- Packet binder.
- Dedicated Phase 2 CI workflow.
- Multifactor attestation schema.
- Additional replay receipts.

---

**authority=false**  
**No fake green.**  
**Evidence > narrative.**
