# External Subscriber Validator

Issue: #41

## Purpose

Validate consumers of the storage-view subscription feed.

## Positive validator

```bash
python audit/external_subscriber_validator.py audit/fixtures/root-subscription-anchor-readiness.example.json audit/fixtures/subscriber-contract-valid.example.json --repo-root .
```

## Matrix

```bash
python audit/external_subscriber_conformance_matrix.py audit/fixtures/root-subscription-anchor-readiness.example.json --repo-root .
```

## Coverage

- valid read-only subscriber
- rejected write method
- rejected non-storage ordering

## Boundary

Subscriber must use storage-time cursor only.

Subscriber must preserve sticky false fields.

Subscriber must not add extra meaning.
