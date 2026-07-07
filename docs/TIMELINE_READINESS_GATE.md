# Timeline Readiness Gate

Issue: #39

## Purpose

Optional storage-time anchor.

This is readiness only.

## Append option

```bash
python audit/append_batch_root.py --log audit/logs/batch-roots.jsonl --manifest <manifest.json> --storage-time-utc 2026-06-30T13:00:42Z
```

## Anchor shape

```json
{
  "anchor_type": "storage_time_only",
  "timestamp_utc": "2026-06-30T13:00:42Z",
  "semantics": "log_storage_time_only"
}
```

## Fixtures

- `audit/fixtures/root-subscription-anchor-readiness.example.json`
- `audit/fixtures/root-subscription-anchor-validate.example.json`

## Validate

```bash
python audit/validate_subscription_feed.py audit/fixtures/root-subscription-anchor-readiness.example.json
```

## Boundary

Storage time only. No extra meaning is added.
