# Storage-View Subscription Feed v0

Issue: #41

## Purpose

Read-only feed for the gated storage-time view.

## Build feed

```bash
python audit/storage_view_subscription_feed.py audit/fixtures/root-subscription-anchor-readiness.example.json --repo-root .
```

## Validate feed

```bash
python audit/validate_storage_view_subscription.py audit/fixtures/root-subscription-anchor-readiness.example.json --repo-root .
```

## Cursor

```text
cursor_type: storage_timestamp_utc
```

## Fixture

```text
audit/fixtures/storage-view-subscription-validate.example.json
```

## Boundary

Read-only.

Gate-gated.

Storage-time order only.

No event-time order is added.

Sticky false fields remain false.
