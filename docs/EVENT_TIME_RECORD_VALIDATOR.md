# Event-Time Record Validator

Issue: #42

## Purpose

Validate EventTimeRecord v0 before normalization exists.

## Validate parser output

```bash
python audit/validate_event_time_record.py event_time/fixtures/claimed-time-record.example.json
```

## Matrix

```bash
python audit/event_time_record_conformance_matrix.py --repo-root .
```

## Fixtures

- `event_time/fixtures/claimed-time-record.example.json`
- `event_time/fixtures/event-time-record-negative-source.example.json`
- `event_time/fixtures/event-time-record-negative-storage-field.example.json`
- `event_time/fixtures/event-time-record-negative-sticky-expected.json`

## Boundary

Requires external source.

Rejects storage-time fields.

Rejects missing or changed sticky false fields.

No normalization, storage comparison, sorting, or consumer is added here.
