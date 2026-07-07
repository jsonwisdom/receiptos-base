# Serialization Delta Guard

Issue: #36

## Purpose

The Serialization Delta Guard protects Witness replay reports before downstream consumers read them.

It prevents silent drift caused by:

```text
normalize -> reorder -> omit -> enrich -> reinterpret -> mutate
```

## Pipeline

```text
ReceiptOS frame -> Witness replay report -> Serialization Delta Guard -> downstream consumer
```

No downstream consumer should receive a replay report unless the guard reports `consumer_safe: true`.

## Canonicalization

The guard hashes reports using deterministic JSON:

```python
json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
```

The hash algorithm is SHA-256.

## Commands

RP-001:

```bash
python witness/guard_replay_report.py witness/reports/rp-001-witness-replay.example.json --expect-file witness/reports/rp-001-witness-replay.hash
```

RP-002 EAS:

```bash
python witness/guard_replay_report.py witness/reports/rp-002-eas-witness-replay.example.json --expect-file witness/reports/rp-002-eas-witness-replay.hash.json
```

## Expected result shape

```json
{
  "serialization_guard": true,
  "report_loaded": true,
  "hash_match": true,
  "authority": false,
  "truth_claim": false,
  "inference_performed": false,
  "state_mutated": false,
  "consumer_safe": true,
  "errors": []
}
```

## Sticky false fields

The guard fails closed if any of these fields are not explicitly false:

- `authority`
- `truth_claim`
- `inference_performed`
- `state_mutated`

## Hash manifests

- `witness/reports/rp-001-witness-replay.hash`
- `witness/reports/rp-002-eas-witness-replay.hash.json`

The RP-002 manifest is JSON metadata because the connector blocked the bare hash-file write. The guard supports both plain hash files and JSON hash manifests.

## Forbidden behavior

The guard must not:

- infer truth
- adjudicate evidence
- promote confidence
- mutate replay reports
- validate domain semantics
- perform on-chain lookup
- run multi-agent simulation
- normalize report meaning beyond canonical JSON bytes

## Consumer handoff rule

Future consumers must preserve the guard result next to their own output.

No consumer may claim authority or truth from a replay report.
