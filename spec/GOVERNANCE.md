# CEG Governance

**Version:** 1.0  
**Status:** Specification (awaiting independent verification)  
**Last Updated:** 2026-07-26

---

## 1. Scope

This document defines the governance model for the Constitutional Evidence Graph (CEG) protocol. It establishes:

- Roles and responsibilities
- Release lifecycle
- Version promotion criteria
- Deprecation policy
- Handling ambiguities
- Security disclosures
- Conformance evidence requirements

---

## 2. Roles

| Role | Responsibilities |
|------|------------------|
| **Editor** | Maintains the specification, reviews proposals, publishes updates |
| **Implementer** | Builds conforming implementations, reports divergences |
| **Reviewer** | Validates conformance bundles, verifies independent replay |
| **Steward** | Oversees the governance process, mediates disputes, approves promotions |

---

## 3. Release Lifecycle

### 3.1 Lifecycle States

| State | Meaning |
|-------|---------|
| **Designed** | Specification written, not yet validated |
| **Reference Validated** | Reference implementation reproduced expected outputs |
| **Independently Reproduced** | At least one independent implementation matched |
| **Stable** | Governance approved, published for general use |

### 3.2 Version Categories

| Category | Meaning | Examples |
|----------|---------|----------|
| **Major** | Breaking changes to invariants, stage definitions, or transition rules | v1.0 → v2.0 |
| **Minor** | New checkpoints, expanded taxonomy, non-breaking extensions | v1.0 → v1.1 |
| **Patch** | Clarifications, typos, non-substantive changes | v1.0.1 → v1.0.2 |

---

## 4. Version Promotion Criteria

### 4.1 From Designed to Reference Validated

- Reference implementation exists
- All tests pass against the reference implementation
- Conformance bundle is frozen

### 4.2 From Reference Validated to Independently Reproduced

- At least one independent implementation reproduces the published conformance bundle without divergence
- Replay report is submitted and verified

### 4.3 From Independently Reproduced to Stable

- Governance review period (minimum 7 days)
- No unresolved objections
- Steward approval
- Published as normative specification

---

## 5. Deprecation Policy

### 5.1 Deprecation Process

1. Announce deprecation with a target sunset date (minimum 6 months)
2. Provide migration guidance
3. Maintain compatibility during the deprecation period
4. Remove after sunset date

### 5.2 Deprecation Triggers

- Security vulnerabilities
- Fundamental incompatibilities with ecosystem
- Superseded by newer version
- Lack of adoption

---

## 6. Handling Ambiguities

### 6.1 Ambiguity Resolution Process

1. File an issue describing the ambiguity
2. Editor proposes clarification
3. Review period (minimum 7 days)
4. If consensus: adopt clarification as normative
5. If no consensus: escalate to Steward for decision

### 6.2 Types of Ambiguities

| Type | Resolution |
|------|------------|
| **Editorial** | Clarification with no normative change |
| **Interpretive** | Normative clarification requiring governance review |
| **Structural** | Protocol change requiring new conformance bundle |

---

## 7. Security Disclosures

### 7.1 Reporting

- Report security issues to security@ceg.dev
- Do not disclose publicly until resolved

### 7.2 Response

- Acknowledgment within 48 hours
- Assessment within 7 days
- Patch timeline communicated

### 7.3 Disclosure

- Public disclosure after patch is available
- CVE assignment if applicable

---

## 8. Conformance Evidence Requirements

### 8.1 Evidence Types

| Type | Description | Acceptable? |
|------|-------------|-------------|
| **Direct** | Artifacts independently observed by the reviewer | ✅ Yes |
| **Reported** | Artifacts observed by another party | ⚠️ Provisional only |
| **Derived** | Produced by protocol rules from earlier outputs | ✅ Yes, if traceable |

### 8.2 Evidence Chain

Every decision, classification, inference, and remediation SHALL be traceable to supporting artifacts:

```
Remediation → Inference → Classification → Observation → Artifact
```

### 8.3 Conformance Bundle

The conformance bundle is the authoritative set of artifacts for conformance testing. It SHALL include:

- Full ObservationLedger
- Canonical hashes for all layers
- Expected graph outputs
- Replay report template
- Provenance and verification metadata

---

## 9. Governance Artifacts

| Artifact | Purpose | Location |
|----------|---------|----------|
| `EVIDENCE_GRAPH.md` | Normative specification | spec/ |
| `GOVERNANCE.md` | Governance rules | spec/ |
| `CONFORMANCE.md` | Conformance requirements | spec/ |
| `RELEASE.md` | Release process | spec/ |
| `manifest.json` | Conformance bundle hashes | conformance/v1.0/ |
| `replay_report.json` | Independent replay evidence | submissions/ |

---

## 10. Versioning and Compatibility

### 10.1 Version Compatibility

| Version | Release Date | Status | Conformance Bundle |
|---------|--------------|--------|-------------------|
| v0.9 | 2026-07-25 | Implementation Candidate | `conformance-v0.9/` |
| v1.0 | TBD | Stable | `conformance-v1.0/` (pending verification) |

### 10.2 Compatibility Guarantees

- Major versions: May break compatibility
- Minor versions: Backward compatible
- Patch versions: Fully compatible

---

## 11. Amendment Process

### 11.1 Proposal

- Submit a proposal via issue or PR
- Include rationale and impact assessment

### 11.2 Review

- Minimum review period: 7 days
- Open to all stakeholders

### 11.3 Approval

- Consensus among editors
- Steward approval for major changes
- New conformance bundle for normative changes

### 11.4 Ratification

- Published as new version
- Recorded in governance history

---

*This document is part of the CEG v1.0 specification. It is normative and versioned.*
