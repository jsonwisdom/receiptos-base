# Verified Root Exporter

Issue: #38

## Purpose

Read-only export of batch roots from a verified audit log.

The exporter calls the log verifier first. If the verifier fails, the export is empty.

## Command

```bash
python audit/export_verified_roots.py --log audit/logs/batch-roots.jsonl --repo-root .
```

## Fixture

```text
audit/fixtures/verified-root-export-001.example.json
```

## Output

The export includes the entry id, storage sequence, batch root, manifest path, manifest hash, leaf count, and sticky false fields.

## Boundary

Read-only. Verifier-gated. Storage sequence only.

No extra meaning is added.

## Next layer

Multi-batch append.