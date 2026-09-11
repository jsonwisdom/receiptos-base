# CEG Release Process

**Version:** 1.0  
**Status:** Specification (awaiting independent verification)  
**Last Updated:** 2026-07-26

---

## 1. Purpose

This document defines the release process for the Constitutional Evidence Graph (CEG) protocol. It establishes:

- Release structure and versioning
- Conformance bundle requirements
- Release gate checklist
- Supported implementations
- Known limitations and superseded versions

---

## 2. Release Structure

### 2.1 Versioning

CEG uses Semantic Versioning (SemVer 2.0.0):

- **Major** (x.0.0): Breaking changes to invariants, stage definitions, or transition rules
- **Minor** (x.y.0): New checkpoints, expanded taxonomy, non-breaking extensions
- **Patch** (x.y.z): Clarifications, typos, non-substantive changes

### 2.2 Release Identifier

Each release has a unique identifier:

```
ceg-v{major}.{minor}.{patch}-{status}
```

Example: `ceg-v1.0.0-rc1`

---

## 3. Release Artifacts

### 3.1 Required Artifacts

A release MUST include:

| Artifact | Description |
|----------|-------------|
| `specification/` | Normative specification (EVIDENCE_GRAPH.md) |
| `conformance/` | Conformance bundle (manifest + fixtures) |
| `manifest.json` | Cryptographic hashes of all artifacts |
| `SHA256SUMS` | Canonical checksum file for bundle verification |
| `release.json` | Release metadata (date, commit, supported implementations) |

### 3.2 Optional Artifacts

A release MAY include:

| Artifact | Description |
|----------|-------------|
| `examples/` | Example implementations |
| `schemas/` | JSON schemas for validation |
| `tests/` | Conformance test suite |

---

## 4. Release Gate Checklist

| Gate | Required | Status |
|------|----------|--------|
| Specification frozen | ✅ | Design complete |
| Conformance bundle frozen | ✅ | Fixtures fixed |
| Manifest validated | ✅ | Hashes consistent |
| Reference replay | ✅ | Reference implementation passes |
| Independent replay | ⏳ | At least one independent implementation |
| Governance approval | ⏳ | Steward approval |
| Public release | ⏳ | Published for general use |

**Note:** Independent replay is the only gate that provides empirical evidence of conformance. All other gates are design or governance decisions.

---

## 5. Release Entry Template

Each release entry SHALL include:

```json
{
  "version": "1.0.0",
  "status": "stable",
  "specification_hash": "a1b2c3d4e5f6...",
  "conformance_bundle_version": "1.0",
  "manifest_hash": "b2c3d4e5f6a7...",
  "release_date": "2026-07-26",
  "supported_implementations": [
    {
      "name": "ceg-reference",
      "version": "0.9.0",
      "verified": true
    }
  ],
  "known_limitations": [],
  "supersedes": ["0.9.0"]
}
```

---

## 6. Release Lifecycle

### 6.1 Pre-Release

- `-alpha`: Early development, not yet stable
- `-beta`: Feature-complete, undergoing validation
- `-rc`: Release candidate, awaiting final approval

### 6.2 Stable Release

- No suffix
- Fully validated and governed

### 6.3 Deprecation

- `-deprecated`: Superseded, but still available
- Sunset date provided

---

## 7. Independent Replay Requirements

A conforming implementation MUST derive all protocol outputs solely from:

1. The published conformance bundle
2. The normative specification

**Permitted:**

- External runtime dependencies (Python, JSON, crypto libraries)
- Clean environment without shared state

**Forbidden:**

- Protocol-specific state from previous runs
- Cached artifacts from reference implementation
- Implementation-specific shortcuts that alter outputs

---

## 8. Bundle Verification

### Option A: Canonical Checksum File

```
SHA256SUMS
-----------
<sha256>  conformance/ledger.json
<sha256>  conformance/canonicalization/output.json
<sha256>  conformance/provenance/output.json
<sha256>  conformance/graph_integrity/output.json
<sha256>  conformance/promotion/output.json
<sha256>  conformance/final/graph.json
<sha256>  conformance/final/explanations.json
```

### Option B: Manifest Extraction

Implementations read `manifest.json`, extract hashes, and verify each file against the listed checksum.

---

## 9. Supported Implementations

| Implementation | Version | Status | Verified |
|----------------|---------|--------|----------|
| ceg-reference | 0.9.0 | Reference | ✅ |
| ceg-independent | 0.9.0 | Independent | ⏳ Pending |

---

## 10. Known Limitations

| ID | Description | Target Version |
|----|-------------|----------------|
| CEG-001 | No support for external graph databases | v1.1 |
| CEG-002 | Limited performance for >10,000 artifacts | v1.2 |

---

## 11. Superseded Versions

| Version | Superseded By | Date | Reason |
|---------|---------------|------|--------|
| 0.9.0 | 1.0.0 | TBD | Promotion to stable |

---

## 12. Security Considerations

- All hashes are derived from canonical representations
- No operational metadata influences identity
- All invariants are machine-verifiable
- Replay reports preserve audit trail

---

This document is part of the CEG v1.0 specification. It is normative and versioned.
