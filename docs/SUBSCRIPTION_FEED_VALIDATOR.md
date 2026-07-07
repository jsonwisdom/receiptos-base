# Subscription Feed Validator

Issue: #38

## Purpose

Validate the read-only root subscription feed before any later timeline layer.

## Command

```bash
python audit/validate_subscription_feed.py audit/fixtures/root-subscription-manifest-002.example.json
```

## Fixture

```text
audit/fixtures/root-subscription-validate-002.example.json
```

## Checks

- top-level allowed fields
- entry allowed fields
- storage sequence continuity
- root hash shape
- manifest hash shape
- duplicate root detection
- sticky false fields

## Boundary

Storage sequence only.

No timeline meaning is added.

## Post-validation target

Timeline readiness gate.