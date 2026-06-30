# Event-Time Conformance Gate

Issue: #42

## Purpose

Code firewall before any event-time parser or extractor exists.

## Command

```bash
python audit/event_time_conformance_gate.py audit/fixtures/event-time-boundary-proposal.example.json
```

## Positive fixture

```text
audit/fixtures/event-time-boundary-proposal.example.json
```

## Expected pass

```text
audit/fixtures/event-time-conformance-pass.example.json
```

## Negative fixture

```text
audit/fixtures/event-time-boundary-negative-storage-import.example.json
```

## Boundary

Fails on closed storage-time file edits.

Fails on storage-time imports.

Requires external event-time source.

Requires sticky false fields.

No parser, extractor, sorter, or consumer is added here.
