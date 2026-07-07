# ReceiptOS Provenance Boundary v0.1

## Purpose

This document defines the boundary between cryptographically bound repository artifacts and mutable contextual metadata for ReceiptOS Base.

The goal is to prevent provenance drift by ensuring that only content included in the Git object graph is treated as commit-bound evidence.

## Core Invariant

```text
Repo metadata != README.md
README.md is SHA-bound.
GitHub description is mutable context only.
```

## Boundary Rule

A claim is commit-bound only if the claimed content is present inside the repository tree at the referenced commit SHA.

Examples of commit-bound evidence include:

- README.md content
- manifest.json content
- files under constitution/
- files under schemas/
- files under receipts/
- files under replay/
- files under engine/
- Git-tracked test fixtures

Examples of mutable contextual metadata include:

- GitHub repository description
- GitHub topics
- GitHub social preview image
- GitHub branch protection settings
- GitHub stars, forks, watchers, and issue counts
- External summaries from third-party systems

Mutable metadata may be cited as context, but it must not be promoted into cryptographic proof unless separately captured, hashed, and committed as a receipt.

## Receipt Classification

ReceiptOS distinguishes between three claim surfaces:

### 1. Commit-bound claim

A claim about repository content at a specific commit SHA.

Required evidence:

- Repository identifier
- Commit SHA
- File path
- File content or content hash
- Verification timestamp or witness note

### 2. Mutable metadata claim

A claim about GitHub-hosted metadata that is not part of the Git tree.

Required treatment:

- Label as mutable context
- Do not treat as SHA-bound
- Do not use as proof of repository content

### 3. External witness claim

A claim made by an outside verifier, model, user, or service.

Required treatment:

- Preserve the witness text separately
- Record what was verified
- Record what was not verified
- Keep authority=false unless a separate authority layer is explicitly defined

## Authority Boundary

ReceiptOS provenance receipts prove process integrity, not legal truth or institutional authority.

A valid receipt may establish that:

- a file existed at a commit SHA
- a replay produced a deterministic output
- a hash matched an expected value
- multiple witnesses reported the same observable state

A valid receipt does not establish that:

- a claim is legally true
- a market classification is authoritative
- an external institution endorses the result
- mutable metadata is cryptographically bound to a commit

## No Scope Bleed Rule

Do not merge mutable context into commit-bound proof language.

Incorrect:

```text
The repository proves it is an onchain receipt engine because the GitHub description says so.
```

Correct:

```text
The README.md at commit <sha> identifies the project as ReceiptOS Base. The GitHub description separately describes the repository as an onchain receipt engine, but that description is mutable metadata and is not commit-bound proof.
```

## Verification Language

Use precise language:

- Verified: file content matches the referenced commit.
- Observed: mutable metadata was visible at the time of review.
- Witnessed: an external verifier reported a result.
- Not confirmed: evidence was not available or was outside the commit-bound surface.

Avoid overclaiming terms such as:

- proves truth
- confirms authority
- legally validates
- establishes official status

## ReceiptOS Base Status

```json
{
  "boundary_id": "RECEIPTOS_PROVENANCE_BOUNDARY_V0_1",
  "authority": false,
  "core_invariant": "Repo metadata != README.md; README.md is SHA-bound; GitHub description is mutable context only.",
  "status": "active"
}
```

## Summary

ReceiptOS Base treats Git-tracked content as the cryptographic evidence surface and treats repository metadata as mutable context.

No mutable metadata becomes proof unless it is independently captured, hashed, committed, and replayable.
