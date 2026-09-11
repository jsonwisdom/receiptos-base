# Independent Replay Guide (CEG v1.0)

**Status:** Non-normative operational guidance  
**Audience:** Third-party implementers and independent reviewers  
**Depends on:** `spec/EVIDENCE_GRAPH.md`, `spec/CONFORMANCE.md`

This document is procedural. It does not define or alter protocol semantics. All normative requirements remain in the specification documents.

---

## 1. Prerequisites

- A clean environment with no prior CEG state or caches
- Access to a published frozen conformance bundle (once available under `conformance/v1.0/`)
- The normative specification files:
  - `spec/EVIDENCE_GRAPH.md`
  - `spec/CONFORMANCE.md`
- Runtime dependencies required by your implementation (language, JSON library, cryptographic library)

---

## 2. Obtaining the Bundle

1. Clone or download the repository at the commit or tag that publishes the frozen bundle.
2. Locate the bundle root (canonical path: `conformance/v1.0/`).
3. Confirm the presence of:
   - `manifest.json`
   - `SHA256SUMS`
   - The expected subdirectories (`ledger/`, `canonicalization/`, `provenance/`, `graph_integrity/`, `promotion/`, `replay/`, `final/`)

Until a frozen bundle is published, independent replay cannot be performed. The layout may exist; the artifacts may not.

---

## 3. Verifying Checksums

### Option A — SHA256SUMS

```bash
cd conformance/v1.0
sha256sum -c SHA256SUMS
```

All entries must report `OK`.

### Option B — Manifest

1. Parse `manifest.json`.
2. For each listed file, compute its SHA-256 digest.
3. Compare against the digest recorded in the manifest.

Any mismatch is a **Manifest mismatch** (see Divergence Classification).

---

## 4. Running Replay

A conforming implementation must derive all outputs solely from:

1. The published conformance bundle, and
2. The normative specification.

Recommended invocation pattern (example only):

```bash
export CEG_REPLAY_CMD="your-implementation replay --bundle conformance/v1.0"
./ci/run-replay.sh
```

Or invoke your implementation directly. The CI helper is a convenience; it is not required for conformance.

**Permitted:** external runtime libraries, clean environment.  
**Forbidden:** cached state from previous runs, artifacts obtained from a reference implementation, shortcuts that alter outputs.

---

## 5. Interpreting PASS / FAIL

| Result | Meaning |
|--------|---------|
| **PASS** | Every required artifact matches the published bundle (byte-for-byte or by canonical hash). Replay report status is `ALL_MATCH`. Divergences list is empty. |
| **FAIL** | Any required artifact differs, or the replay report contains divergences, or divergences were silently fixed. |
| **SKIP** | No frozen bundle is present yet, or the replay command was not supplied. Not a conformance claim. |

Silent correction of divergences is itself a conformance failure.

---

## 6. Submitting Replay Evidence

Use the schema defined in `docs/REPLAY_SUBMISSION_TEMPLATE.json` (or an equivalent structured report).

Minimum required fields:

- implementation name and version
- platform / OS
- runtime version
- bundle version (or commit / tag)
- replay status (`ALL_MATCH` or `DIVERGENCE`)
- divergence count
- manifest verification result
- timestamp (UTC)
- optional notes

Submit the report through the process defined by the project maintainers (issue, PR, or designated submission path). The submission itself becomes part of the evidence record.

---

## 7. What This Guide Does Not Do

- It does not define promotion rules, canonicalization, or graph validation.
- It does not replace `CONFORMANCE.md`.
- It does not certify any implementation.
- It does not create a frozen bundle.

Independent replay is the normative basis for a conformance claim. This guide only helps you perform it cleanly.
