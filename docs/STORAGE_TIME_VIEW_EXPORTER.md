# Storage-Time View Exporter

Issue: #40

## Purpose

Read-only export of the storage-time sorted view.

The exporter is gated by the storage view conformance matrix.

## Command

```bash
python audit/export_storage_time_view.py audit/fixtures/root-subscription-anchor-readiness.example.json --repo-root .
```

## Matrix

```bash
python audit/storage_view_conformance_matrix.py --repo-root .
```

## Boundary

Read-only.

Matrix-gated.

Storage-time order only.

No event-time order is added.

## Post-exporter target

Storage-view external conformance gate.