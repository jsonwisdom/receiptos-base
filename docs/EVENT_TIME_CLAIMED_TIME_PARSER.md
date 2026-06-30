# Event-Time Claimed-Time Parser v0

Issue: #42

## Purpose

Parse one externally claimed timestamp from an untrusted payload.

## Command

```bash
python event_time/parse_claimed_time.py event_time/fixtures/claimed-time-input.example.json
```

## Fixtures

```text
event_time/fixtures/claimed-time-input.example.json
event_time/fixtures/claimed-time-record.example.json
audit/fixtures/event-time-parser-negative-storage-import.example.json
```

## Boundary

External source only.

No storage-time imports.

No timezone normalization.

No storage-time comparison.

No sorting.

No consumer.

Sticky false fields remain false.
