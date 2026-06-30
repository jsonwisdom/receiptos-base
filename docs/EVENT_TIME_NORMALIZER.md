# Event-Time Normalizer v0

Issue: #42

## Purpose

Normalize a claimed external timestamp to UTC after EventTimeRecord validation exists.

## Normalize

```bash
python event_time/normalize_claimed_time.py event_time/fixtures/claimed-time-record.example.json
```

## Validate normalized record

```bash
python audit/validate_normalized_event_time_record.py event_time/fixtures/claimed-time-normalized-record.example.json
```

## Matrix

```bash
python audit/normalized_event_time_conformance_matrix.py --repo-root .
```

## Fixtures

- `event_time/fixtures/claimed-time-normalized-record.example.json`
- `event_time/fixtures/claimed-time-normalize-negative-malformed.example.json`

## Boundary

External source only.

No storage-time imports.

No storage-time comparison.

No sorting.

No consumer.

No truth upgrade.

Sticky false fields remain false.
