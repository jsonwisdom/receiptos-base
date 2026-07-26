# Constitutional Evidence Graph (CEG) — Specification

**Version:** 1.0.0-rc1
**Status:** Release Candidate (awaiting independent verification)
**Last Updated:** 2026-07-26
**Editor:** Jason

---

## 1. Scope

The Constitutional Evidence Graph (CEG) is a protocol for representing, validating, and replaying evidence-based graphs. It defines:

- A deterministic observation ledger
- Canonical serialization and hashing
- Provenance tracking with verification
- Graph validation invariants
- Promotion rules for concept emergence
- Replayability and conformance guarantees

CEG is **content-neutral**. It applies equally to governance documents, creative works, software artifacts, and scientific observations. The protocol only cares about evidence — it does not care about the domain.

---

## 2. Terminology

| Term | Definition |
|------|------------|
| **Artifact** | Any evidence ingested into the ledger. An artifact has an ID, title, date, source, kind, provenance, verification, and optional metadata. |
| **Observation** | A verbatim record from an artifact. Observations are typed as lexeme, structural_feature, or explicit_reference. |
| **ObservationLedger** | An immutable collection of artifacts and observations. The ledger preserves raw evidence exactly as observed. |
| **Provenance** | Metadata describing how an observation was obtained. Consists of four booleans: observed, artist_asserted, external_metadata, algorithmic. |
| **Verification** | Confirmation status of an observation. Structured as status (verified, unverified, not_applicable), reason_code, and optional note. |
| **EvidenceKind** | The role of an artifact in the protocol: normative_definition, implementation_observation, external_observation, or historical_record. |
| **Negative Evidence** | An explicit record that a concept was not observed in an artifact. Distinct from "unknown" (no information). |
| **Concept** | A derived node representing recurring evidence. Concepts emerge from observations, not from design. |
| **Promotion** | The process by which a concept becomes canonical. Promotion depends on independent supporting evidence. |
| **Canonicalization** | Deterministic serialization of any CEG object to UTF-8 JSON with sorted keys, no whitespace, and stable ordering. |
| **Replay** | Reproducing all outputs from a frozen fixture bundle. Replay is the primary conformance test. |
| **Conformance Bundle** | The frozen set of artifacts used to test implementation conformance. Contains ledger, canonicalization outputs, provenance outputs, graph outputs, and promotion outputs. |

---

## 3. Normative Invariants

### GSI-001 — Stage Isolation
A stage MAY consume outputs from preceding stages but SHALL NOT produce outputs assigned to subsequent stages.

### GSI-002 — Artifact Integrity
Retrieved artifacts SHALL be preserved without modification before any observations are recorded.

### GSI-003 — Observation Integrity
Every observation SHALL reference one or more retrieved artifacts and SHALL record only information directly supported by those artifacts.

### GSI-004 — Traceable Decisions
Every classification, inference, decision, and remediation SHALL reference the supporting outputs of earlier stages.

### GSI-005 — Deterministic Replay
Given the same preserved artifacts and protocol version, the same permitted stage outputs SHALL be reproducible by an independent reviewer.

### GSI-006 — Evidence Basis Declaration
Every protocol output SHALL declare its evidence basis.

### GSI-007 — Epistemic Integrity
An implementation SHALL NOT claim external state verification for an artifact unless the reviewer has independently confirmed correspondence.

### GSI-008 — Provenance Preservation
The provenance of every protocol output SHALL be retained throughout the investigation. Updates to evidence basis, artifact references, or stage outputs SHALL preserve prior records rather than overwrite them.

---

## 4. Canonicalization

### 4.1 Canonical Serialization

CEG uses deterministic JSON serialization:

```python
json.dumps(
    obj,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False
)
```

### 4.2 Canonical Policies

| Policy | Decision | Constitutional Statement |
|--------|----------|--------------------------|
| Unicode | Byte-strict | NFC ≠ NFD; no normalization. Visual identities with different Unicode forms are distinct. |
| Case | Ledger neutral, promotion decides | Case is preserved at observation layer. Case normalization, if any, is a promotion decision. |
| Numeric | Strict | 1 ≠ 1.0; no numeric normalization. Numeric representations are preserved exactly as observed. |
| Newline | Observation preserves, output normalizes | Raw text fidelity at observation layer; canonical JSON output normalized to LF. |
| Insertion Order | Hash invariant | Identical data with different insertion order yields identical canonical hashes. |

### 4.3 Canonical Hash

The canonical hash is SHA-256 over the canonical JSON representation:

```
hash = SHA-256(canonical_json(obj))
```

### 4.4 Operational Metadata Exclusion

Operational metadata (generated_at, generated_by, environment) MUST NOT participate in canonical hashing. This ensures replay stability.

---

## 5. Observation Ledger

### 5.1 Structure

```python
ObservationLedger:
  artifacts: List[Artifact]
  observations: List[Observation]
  created_at: str  # descriptive only, not used in hashing
```

### 5.2 Artifact

```python
Artifact:
  id: str              # unique identifier
  title: str           # human-readable title
  date: str            # ISO 8601 date
  source: str          # where the artifact came from
  kind: EvidenceKind   # normative_definition, implementation_observation, external_observation, historical_record
  provenance: Provenance
  verification: Verification
  metadata: dict       # optional, descriptive only
```

### 5.3 Observation

```python
Observation:
  artifact_id: str                              # reference to artifact
  observation_type: Literal["lexeme", "structural_feature", "explicit_reference"]
  value: str                                    # verbatim observed value
  count: Optional[int]                          # for structural features, count of occurrences
  note: str                                     # optional, descriptive only
```

### 5.4 Provenance

```python
Provenance:
  observed: bool              # directly observed
  artist_asserted: bool       # artist claimed it
  external_metadata: bool     # from external system
  algorithmic: bool           # detected algorithmically
```

**Allowed State Table:**

| Observed | Artist Asserted | External Metadata | Algorithmic | Valid |
|----------|-----------------|-------------------|-------------|-------|
| ✅ | ❌ | ❌ | ❌ | ✅ |
| ✅ | ✅ | ❌ | ❌ | ✅ |
| ✅ | ❌ | ✅ | ❌ | ✅ |
| ✅ | ❌ | ❌ | ✅ | ✅ |
| ❌ | ✅ | ❌ | ❌ | ✅ |
| ❌ | ❌ | ✅ | ❌ | ✅ |
| ❌ | ❌ | ❌ | ✅ | ✅ |
| ❌ | ✅ | ✅ | ❌ | ✅ |
| ❌ | ✅ | ❌ | ✅ | ✅ |
| ❌ | ❌ | ✅ | ✅ | ✅ |
| ❌ | ✅ | ✅ | ✅ | ✅ |
| ❌ | ❌ | ❌ | ❌ | ❌ |

### 5.5 Verification

```python
Verification:
  status: Literal["verified", "unverified", "not_applicable"]
  reason_code: str  # SOURCE_CONFIRMED, ARTIST_CONFIRMED, EXTERNAL_CONFIRMED, ALGORITHMIC_CONFIRMED, NEEDS_CONFIRMATION, PENDING_REVIEW, NOT_REQUIRED
  note: str         # human-readable, informational only, not parsed
```

**Valid Status + Reason Code Pairs:**

| Status | Valid Reason Codes |
|--------|--------------------|
| verified | SOURCE_CONFIRMED, ARTIST_CONFIRMED, EXTERNAL_CONFIRMED, ALGORITHMIC_CONFIRMED |
| unverified | NEEDS_CONFIRMATION, PENDING_REVIEW |
| not_applicable | NOT_REQUIRED |

### 5.6 Negative Evidence

Negative evidence is recorded explicitly:

```python
NegativeObservation:
  concept_id: str        # concept that was searched for
  artifact_id: str       # artifact where it was not found
  status: Literal["not_observed", "unknown"]
  provenance: Provenance
  verification: Verification
  note: str              # optional, descriptive only
```

**Distinction:**

· **not_observed**: The system explicitly looked for the concept and did not find it.
· **unknown**: The system has no information about the concept in this artifact.

---

## 6. Evidence Graph Model

### 6.1 Node Types

| Node Type | Definition | Example |
|-----------|------------|---------|
| Artifact | An ingested evidence artifact | R-001, R-002, R-003 |
| Document | A normative document | EVIDENCE_GRAPH.md, CONFORMANCE.md |
| Concept | A recurring idea or theme | Governance, Evidence, Provenance |
| Symbol | A recurring visual or textual motif | Mirror, Blueprint, Checkpoint C1 |
| Style | A recurring formal tendency | Protocol-driven, Minimalist |
| Collection | A long arc of meaning | ReceiptOS, Gray Baby |
| Influence | A cited external source | Gödel, Maxwell |

### 6.2 Edge Types

| Edge Type | Definition | Example |
|-----------|------------|---------|
| OBSERVES | Artifact observes a concept | R-001 OBSERVES Governance |
| DEFINES | Document defines a concept | EVIDENCE_GRAPH.md DEFINES Stage Isolation |
| REFERENCES | Artifact references a concept | R-003 REFERENCES GOVERNANCE.md |
| CO_OCCURS_WITH | Concepts that appear together | Governance CO_OCCURS_WITH Evidence |
| REALIZES | Implementation realizes a specification | Validator REALIZES Stage Isolation |
| APPLIES | Application applies a specification | R-001 APPLIES GOVERNANCE.md |

### 6.3 Graph Validation

The graph MUST satisfy the following invariants:

**G-1: Node Identity**

· Every node ID is unique.
· No empty IDs.
· IDs are stable across replay.

**G-2: Edge Integrity**

· Every edge's source and target must exist as nodes.
· Edge identity (source, type, target) must be unique.
· Self-loops are allowed only in reference edges.

**G-3: Explanation Integrity**

· Every promoted concept has exactly one explanation.
· All referenced artifacts exist.
· All referenced observations exist.
· All referenced provenance records exist.

**G-4: Canonical Graph Serialization**

· Equivalent graphs serialize identically.
· Node insertion order does not affect canonical representation.
· Edge insertion order does not affect canonical representation.

**G-5: Graph Closure**

· Every referenced object is reachable in the graph.
· No orphan concepts, explanations, or evidence records.

**G-6: Validation Idempotence**

· Calling graph.validate() multiple times produces identical results.
· Validation mutates nothing.

**G-7: Cycle Policy**

· Cycles are allowed in reference edges only.
· All other edge types must form a DAG.

---

## 7. Promotion

### 7.1 Promotion as a Pure Function

```
PromotionDecision = F(observations, provenance, graph, policy)
```

**Properties:**

· No hidden state.
· No execution-order dependence.
· No implementation-specific heuristics.

### 7.2 Promotion Rules

A concept is promoted when:

1. ≥2 independent artifacts support it, OR
2. 1 normative definition + 1 independent application support it.

**Independence means:**

· Artifacts are not derived from the same source.
· Artifacts are not repeated boilerplate.
· Artifacts are not copied definitions.

### 7.3 Threshold Boundary

| Evidence Count | Status |
|----------------|--------|
| 0 | ❌ Not promoted |
| 1 | ❌ Not promoted |
| 2 | ✅ Promoted |
| 3+ | ✅ Promoted |

### 7.4 Promotion Explanation

Every promoted concept SHALL have a deterministic explanation including:

· Promotion rule applied
· Supporting artifacts (by ID)
· Supporting observations (by ID)
· Provenance basis
· Threshold satisfied

### 7.5 Invalid Evidence Isolation

· Invalid provenance → excluded from promotion.
· Malformed artifact → excluded from promotion.
· One bad artifact does not poison unrelated evidence.
· Conflicting evidence → handled per policy (block promotion, flag, or create conflict node).

### 7.6 Conflicting Evidence

When two artifacts conflict (e.g., one says Concept X is present, another says it is absent):

· The conflict SHALL be recorded in the validation report.
· Promotion SHALL NOT proceed unless the conflict is resolved.
· The policy for conflict handling SHALL be documented in the conformance bundle.

---

## 8. Replay and Conformance

### 8.1 Independent Replay Requirements

A conforming implementation MUST derive all protocol outputs solely from:

1. The published conformance bundle
2. The normative specification

**Permitted:**

· External runtime dependencies (Python, JSON, crypto libraries)
· Clean environment without shared state

**Forbidden:**

· Protocol-specific state from previous runs
· Cached artifacts from reference implementation
· Implementation-specific shortcuts that alter outputs

### 8.2 Conformance Bundle

The conformance bundle SHALL include:

```
conformance/
    manifest.json                    # Cryptographic hashes of all outputs
    SHA256SUMS                       # Canonical checksum file
    ledger/
        ledger.json                  # Canonical ObservationLedger
        ledger.sha256                # SHA-256 of ledger.json
    canonicalization/
        canonical_hashes.json        # Expected canonicalization outputs
    provenance/
        provenance_hashes.json       # Expected provenance outputs
    graph_integrity/
        graph_hashes.json            # Expected graph validation outputs
    promotion/
        promotion_hashes.json        # Expected promotion outputs
    replay/
        replay_report.json           # Expected replay report structure
    final/
        graph.json                   # Expected final graph
        graph.sha256                 # SHA-256 of graph.json
        explanations.json            # Expected promotion explanations
```

### 8.3 Pass/Fail Criteria

**Passing Conditions:**

· All outputs are byte-for-byte identical to the bundle.
· The replay report indicates status: "ALL_MATCH".
· The divergences list is empty.

**Failing Conditions:**

· Any output differs from the bundle.
· The replay report indicates status: "DIVERGENCE".
· Any divergence is silently fixed rather than recorded.

### 8.4 Divergence Reporting

All divergences SHALL be recorded in the replay report:

```json
{
  "divergences": [
    {
      "layer": "canonicalization",
      "expected": "a1b2c3...",
      "actual": "d4e5f6...",
      "note": "Hash mismatch in canonicalization output"
    }
  ]
}
```

---

## 9. Versioning and Compatibility

### 9.1 Version Categories

| Category | Meaning | Examples |
|----------|---------|----------|
| Major | Breaking changes to invariants, stage definitions, or transition rules | v1.0 → v2.0 |
| Minor | New checkpoints, expanded taxonomy, non-breaking extensions | v1.0 → v1.1 |
| Patch | Clarifications, typos, non-substantive changes | v1.0.1 → v1.0.2 |

### 9.2 Compatibility Guarantees

· Major versions: May break compatibility.
· Minor versions: Backward compatible.
· Patch versions: Fully compatible.

### 9.3 Release Lifecycle

| State | Meaning |
|-------|---------|
| Designed | Specification written, not yet validated |
| Reference Validated | Reference implementation reproduced expected outputs |
| Independently Reproduced | At least one independent implementation matched |
| Stable | Governance approved, published for general use |

### 9.4 Version Promotion Criteria

| Transition | Requirement |
|------------|-------------|
| Designed → Reference Validated | Reference implementation exists and passes all tests |
| Reference Validated → Independently Reproduced | Independent implementation reproduces the conformance bundle |
| Independently Reproduced → Stable | Governance review, Steward approval |

---

## 10. Security Considerations

· **Hash Integrity**: All hashes are derived from canonical representations. Tampering with any output changes the hash.
· **Operational Metadata**: Operational metadata (generated_at, generated_by, environment) is excluded from identity. It cannot be used to counterfeit evidence.
· **Provenance Integrity**: Provenance is part of identity. Two artifacts with identical observations but different provenance produce different hashes.
· **Replayability**: Independent replay is the only evidence that qualifies an implementation as conformant. Design documents and claimed results are not evidence until independently reproduced.

---

## 11. Conformance Requirements

### 11.1 Implementation Obligations

A conforming implementation MUST:

1. Start from only the published conformance bundle.
2. Produce byte-for-byte identical outputs.
3. Record all divergences explicitly.
4. Never silently fix divergences.
5. Preserve the audit trail — replay reports are immutable evidence.

### 11.2 Conformance Evidence

· **Direct Evidence**: Artifacts independently observed by the reviewer.
· **Reported Evidence**: Artifacts observed by another party (provisional only).
· **Derived Evidence**: Produced by protocol rules from earlier outputs (acceptable, if traceable).

### 11.3 Evidence Chain

Every decision, classification, inference, and remediation SHALL be traceable to supporting artifacts:

```
Remediation → Inference → Classification → Observation → Artifact
```

---

This document is part of the CEG v1.0 specification. It is normative and versioned.
