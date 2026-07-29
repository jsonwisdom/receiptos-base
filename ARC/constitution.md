# ARC Constitution

## ARC-001 — Canonical Ownership

Every implementation artifact SHALL have one canonical repository owner.

## ARC-002 — No Project-Tree Duplication

A repository SHALL NOT contain a cloned or mirrored implementation tree owned
by another repository.

## ARC-003 — Local Discovery

Each participating repository SHALL expose `ARC/manifest.json` as its discovery
vector.

## ARC-004 — Explicit Entrypoints

The manifest SHALL explicitly identify repository identity and dependency
entrypoints.

## ARC-005 — Evidence Preservation

Observations, receipts, and rejects SHALL be preserved as separate artifact
classes. A rejection SHALL NOT be rewritten into a successful observation.

## ARC-006 — Deterministic Verification

Canonicalization and hashing contracts SHALL be explicitly named and versioned.

## ARC-007 — Unknown Is Valid

Missing, unavailable, and indeterminate states SHALL be recorded as such rather
than inferred as false or successful.

## ARC-008 — Minimal Build

Repositories SHALL prefer references, identities, and dependency edges over
duplicated content.
