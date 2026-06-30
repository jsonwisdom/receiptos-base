# Event-Time Comparison v0

Issue: #42

## Purpose

Compare normalized claimed event-time records by claimed timestamp only.

## Compare

```bash
python event_time/compare_claimed_times.py event_time/fixtures/claimed-time-normalized-records.example.json
```

## Validate

```bash
python audit/validate_event_time_comparison.py <comparison.json>
```

## Matrix

```bash
python audit/event_time_comparison_conformance_matrix.py --repo-root .
```

## Fixtures

- `event_time/fixtures/claimed-time-normalized-records.example.json`
- `event_time/fixtures/claimed-time-comparison-negative-claims.example.json`
- `event_time/fixtures/claimed-time-comparison-negative-storage-compare.example.json`

## Boundary

Comparison type is claimed-time order only.

No causation claim.

No priority claim.

No storage-time comparison.

No truth upgrade.

Sticky false fields remain false.
