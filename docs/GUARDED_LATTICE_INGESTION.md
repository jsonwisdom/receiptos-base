# Guarded Lattice Ingestion

Issue: #37

## Purpose

This layer is an admission gate for Witness replay reports.

It accepts only reports that pass the Serialization Delta Guard.

## Pipeline

```text
ReceiptOS frame -> Witness replay report -> Serialization Delta Guard -> Lattice admission gate
```

## Commands

```bash
python lattice/ingest_guarded_report.py witness/reports/rp-001-witness-replay.example.json --expect-file witness/reports/rp-001-witness-replay.hash
```

```bash
python lattice/ingest_guarded_report.py witness/reports/rp-002-eas-witness-replay.example.json --expect-file witness/reports/rp-002-eas-witness-replay.hash.json
```

## Acceptance fields

```json
{
  "lattice_ingestion": true,
  "ingestion_accepted": true,
  "guard_consumer_safe": true,
  "guard_hash_match": true,
  "authority": false,
  "truth_claim": false,
  "inference_performed": false,
  "state_mutated": false,
  "reason_codes": []
}
```

## Fixtures

- `lattice/fixtures/rp-001-lattice-ingest.example.json`
- `lattice/fixtures/rp-002-eas-lattice-ingest.example.json`

## Boundary

The admission gate reports source path, source hash, guard result, accepted/rejected status, and reason codes.

It does not score, cluster, simulate, mutate graph state, or promote authority/truth.

## Next safe pattern

The next consumer can be an indexer that records only accepted report hashes and sticky false flags.
