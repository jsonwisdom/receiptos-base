# Replay Invariants v0.1

## Purpose

Defines canonical invariant IDs for ReceiptOS Replay Engine v0.1.

Receipts must cite one or more of these IDs in `replay_invariants`.

## Canonical Invariants

- INV_READ_ONLY_WORKSPACE
- INV_COMMIT_RESOLVABLE
- INV_TREE_HASH_MATCH
- INV_SCHEMA_VALID
- INV_CANONICAL_SURFACES_PRESENT
- INV_DETERMINISTIC_OUTPUT
- INV_NON_AUTHORITY
- INV_FAILURE_EXPLICIT

## Rules

- Invariant IDs are stable for v0.1.
- Receipts must cite valid invariant IDs.
- Failure must be explicit.
- Authority remains false.
- Replay must be deterministic.
- Source receipts must not be mutated.

End of Invariants v0.1
