# Storage Anchor Consumer

Issue: #39

## Purpose

Anchor-only consumer for storage-time readiness.

It reads a validated feed and exports storage-time anchors only.

## Command

```bash
python audit/consume_storage_anchors.py audit/fixtures/root-subscription-anchor-readiness.example.json
```

## Fixture

```text
audit/fixtures/storage-anchor-consume-001.example.json
```

## Boundary

No sorting by timestamp.

No timeline semantics.

Storage sequence only.

Storage time only.
