# Storage View External Conformance Gate

Issue: #40

## Purpose

Validate the exported storage-time view surface.

## Command

```bash
python audit/conformance_gate_storage_view.py audit/fixtures/root-subscription-anchor-readiness.example.json --repo-root .
```

## Fixture

```text
audit/fixtures/storage-view-conformance-gate.example.json
```

## Checks

- export is ready
- allowed fields only
- storage timestamps sorted
- storage-time anchor semantics only
- sticky false fields

## Boundary

Storage-time order only.

No event-time order is added.
