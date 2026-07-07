# Batch Root Audit Log

Issue: #38

## Purpose

Append-only record of accepted batch roots.

The audit log records opaque batch commitments. It does not add timeline semantics, causation, priority, evidentiary strength, authority, or truth.

## Pipeline

```text
ReceiptOS frame -> Witness report -> Guard -> Lattice gate -> Catalog -> Merkle -> Batch root -> Audit log
```

## Command

```bash
python audit/append_batch_root.py --log audit/logs/batch-roots.jsonl --manifest lattice/fixtures/batch-root-manifest-rp001-rp002.example.json
```

## First entry

```text
batch-root-entry-000001
```

Batch root:

```text
sha256:6ffc207fe8fb31296c27fc1457e233af771dca3800ce299cd262777fef790dad
```

Manifest hash:

```text
sha256:bbf12d63597b7c5a09bcb44bda68e8da3883c2a73a8e775eb6e394291a8a276a
```

## Files

- `audit/append_batch_root.py`
- `audit/logs/batch-roots.jsonl`
- `audit/fixtures/batch-root-audit-entry-001.example.json`

## Sequence semantics

`entry_sequence` means append order only.

It does not mean event time, causation, priority, truth progression, or evidentiary strength.

## Sticky fields

Every entry preserves:

```json
{
  "authority": false,
  "truth_claim": false,
  "inference_performed": false,
  "state_mutated": false
}
```

## Next safe layer

An audit-log verifier can check JSONL sequence continuity and manifest hash consistency without interpreting batch meaning.
