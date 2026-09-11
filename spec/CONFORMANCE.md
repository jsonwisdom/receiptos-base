# CEG Conformance Requirements

**Version:** 1.0.0-rc1  
**Status:** Release Candidate (awaiting independent verification)  
**Last Updated:** 2026-07-26  
**Depends on:** `spec/EVIDENCE_GRAPH.md` (CEG v1.0)

---

## 1. Purpose

This document defines the normative requirements for claiming conformance to the Constitutional Evidence Graph (CEG) protocol.

It specifies:

- Required artifacts that must be produced
- The independent replay procedure
- Pass/fail criteria
- Implementation obligations
- Evidence boundaries for conformance claims

This document does **not** redefine any protocol semantics. All behavioral rules are defined solely in `EVIDENCE_GRAPH.md`. This document only defines how implementations are tested and judged against those rules.

---

## 2. Required Artifacts

A complete conformance claim requires a frozen **conformance bundle** that contains the following artifacts (or their equivalent under a documented layout):

```
conformance/v1.0/
├── manifest.json              # Cryptographic inventory of all artifacts
├── SHA256SUMS                 # Canonical checksum file
├── ledger/
│   ├── ledger.json            # Canonical ObservationLedger
│   └── ledger.sha256
├── canonicalization/
│   └── canonical_hashes.json  # Expected canonicalization outputs
├── provenance/
│   └── provenance_hashes.json # Expected provenance outputs
├── graph_integrity/
│   └── graph_hashes.json      # Expected graph validation outputs
├── promotion/
│   └── promotion_hashes.json  # Expected promotion outputs
├── replay/
│   └── replay_report.json     # Expected replay report structure
└── final/
    ├── graph.json             # Expected final graph
    ├── graph.sha256
    └── explanations.json      # Expected promotion explanations
```

The layout above is the canonical reference layout. Implementations may use equivalent structures provided the same information is present and cryptographically inventoried.

**Note:** No frozen bundle is published in this repository at the time of this document. The first frozen bundle will be introduced in a subsequent release candidate (PR-5).

---

## 3. Replay Procedure

A conforming implementation MUST be able to reproduce every required artifact solely from:

1. The published conformance bundle, and
2. The normative specification (`EVIDENCE_GRAPH.md`).

### 3.1 Permitted

- External runtime dependencies (language standard libraries, JSON parsers, cryptographic libraries)
- A clean environment with no shared state from previous runs

### 3.2 Forbidden

- Protocol-specific state or caches from previous runs
- Artifacts or intermediate results obtained from a reference implementation
- Implementation-specific shortcuts that alter any output relative to the published bundle

### 3.3 Replay Report

Every replay SHALL produce a machine-readable report that includes at minimum:

```json
{
  "status": "ALL_MATCH" | "DIVERGENCE",
  "protocol_version": "1.0.0-rc1",
  "bundle_manifest_hash": "...",
  "divergences": []
}
```

If any divergence exists, the report MUST list every divergence with sufficient detail to locate the mismatch (layer, expected value, actual value, optional note).

---

## 4. Pass/Fail Criteria

### 4.1 Passing Conditions

A replay PASSES if and only if:

- Every required artifact is byte-for-byte identical to the corresponding artifact in the published bundle, **or** the implementation produces an equivalent artifact whose canonical hash matches the published hash.
- The replay report status is `"ALL_MATCH"`.
- The divergences array is empty.

### 4.2 Failing Conditions

A replay FAILS if:

- Any required artifact differs from the published bundle (or its published hash).
- The replay report status is `"DIVERGENCE"`.
- Any divergence is silently corrected or omitted from the report.

Silent fixing of divergences is itself a conformance violation.

---

## 5. Implementation Obligations

A conforming implementation MUST:

1. Start from only the published conformance bundle and the normative specification.
2. Produce outputs that match the published artifacts (byte-for-byte or by canonical hash).
3. Record every divergence explicitly in the replay report.
4. Never silently fix or suppress divergences.
5. Preserve the audit trail: replay reports are immutable evidence once generated.

---

## 6. Version Compatibility

Conformance claims are versioned with the protocol.

- A claim of conformance to CEG 1.0.0-rc1 is valid only against a bundle published for that exact version (or an explicitly compatible later patch).
- Major-version changes may invalidate previous conformance claims.
- Minor and patch versions remain backward-compatible unless the release notes explicitly state otherwise.

---

## 7. Evidence Boundary

Successful independent replay against the published conformance bundle is the **normative basis** for claiming protocol conformance. Other forms of evidence (design documents, implementation reports, or self-reported test results) may inform review but do not, by themselves, establish conformance.

Direct observation of the published bundle and independent reproduction of its outputs are required. Reported or derived evidence may be used as supporting material during review but carries lower epistemic weight.

---

## 8. Governance Interaction

This document defines *what* must be demonstrated for conformance. The processes for:

- publishing a frozen bundle,
- collecting independent replay evidence,
- promoting a release candidate to stable,
- handling ambiguity or security disclosures,

are defined in `GOVERNANCE.md` and `RELEASE.md`.

Those documents may reference this specification; they do not override its pass/fail criteria.

---

This document is part of the CEG v1.0 specification. It is normative for conformance claims and is versioned together with `EVIDENCE_GRAPH.md`.
