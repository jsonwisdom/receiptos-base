# Timeline Semantics v0 Storage View

Issue: #40

## Purpose

Storage-time sorted presentation of validated anchors.

## Command

```bash
python audit/storage_time_view.py audit/fixtures/root-subscription-anchor-readiness.example.json
```

## Script

```text
audit/storage_time_view.py
```

## Expected fixture note

The connector blocked writing the JSON fixture for this view.

Expected result shape is produced by the command above.

## Boundary

Storage-time sorting only.

No event-time order.

No extra meaning is added.
