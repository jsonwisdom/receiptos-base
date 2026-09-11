# Divergence Classification (CEG v1.0)

**Status:** Non-normative operational vocabulary  
**Audience:** Reviewers and implementers analyzing replay failures  
**Depends on:** `spec/CONFORMANCE.md`

This document provides a shared vocabulary for describing mismatches observed during independent replay. It does not change pass/fail criteria or introduce new protocol rules.

---

## Classification Table

| Class | Meaning | Typical Cause |
|-------|---------|---------------|
| **Manifest mismatch** | Bundle integrity problem. A file listed in `manifest.json` or `SHA256SUMS` is missing, has the wrong digest, or an unexpected file is present. | Incomplete publication, corruption in transit, incorrect packaging |
| **Canonicalization mismatch** | Serialization or canonicalization difference. The same logical object produces a different canonical JSON (or hash) than the published artifact. | Key ordering, whitespace, Unicode normalization, numeric representation, insertion-order sensitivity |
| **Graph mismatch** | Structural output difference. Nodes, edges, or graph-level invariants differ from the published final graph. | Different observation extraction, missing negative evidence, cycle-policy violation, identity collision |
| **Promotion mismatch** | Different promotion result. A concept was promoted (or not promoted) differently than the published explanations. | Independence judgment, threshold application, conflicting-evidence handling, invalid-evidence isolation |
| **Replay execution failure** | Replay could not complete. The implementation crashed, timed out, or otherwise failed to produce a full set of outputs. | Missing dependency, resource limit, unhandled exception, incorrect invocation |
| **Other** | Any divergence that does not fit the classes above. Must be accompanied by a clear note. | — |

---

## Usage Rules

1. Every recorded divergence SHOULD carry exactly one primary class.
2. If multiple classes apply, choose the earliest failure in the pipeline (manifest → canonicalization → graph → promotion).
3. `replay_execution_failure` is used only when the process did not produce comparable outputs.
4. Classification is for human review and triage. It does not alter the normative requirement that any non-empty divergences list causes the replay to FAIL.

---

## Relation to the Replay Report

The machine-readable replay report defined in `CONFORMANCE.md` already requires a `divergences` array. Implementations and reviewers are encouraged to populate the `class` field (or equivalent) using the vocabulary in this document so that independent submissions remain comparable.

---

## What This Document Does Not Do

- It does not define new failure modes.
- It does not soften or strengthen pass/fail criteria.
- It does not authorize silent correction of any divergence.
- It is not part of the normative specification.
