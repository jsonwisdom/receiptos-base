# Event-Time Feature Conformance Matrix

Issue: #42

## Purpose

One umbrella matrix for the current event-time lane.

This must pass before comparison semantics are introduced.

## Command

```bash
python audit/event_time_feature_conformance_matrix.py --repo-root .
```

## Fixture

```text
audit/fixtures/event-time-feature-conformance-matrix.example.json
```

## Coverage

- boundary proposal passes
- storage import proposals fail
- parser record matrix passes
- normalized record matrix passes

## Boundary

No storage-time imports.

No storage-time comparison.

No sorting.

No consumer.

Sticky false fields remain false.

## Next allowed feature

```text
event_time/compare_claimed_times.py
```
