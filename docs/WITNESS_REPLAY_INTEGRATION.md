# Witness Replay Integration

Issue: #35

## Purpose

Witness replay consumes ReceiptOS / ESG-001 frames as representation artifacts and emits deterministic replay reports.

Witness replay does not interpret claims. It does not promote authority. It does not mutate graph state.

## Runner

```bash
python witness/replay_receiptos_frame.py fixtures/rp-001-receiptos-frame.example.json --disable-timestamp
```

With EAS profile composition:

```bash
python witness/replay_receiptos_frame.py fixtures/rp-002-eas-frame.example.json --profile eas-v1 --disable-timestamp
```

## Output contract

Replay reports may include:

- frame loaded
- frame type
- base conformance
- optional profile conformance
- payload hash match
- nonce well-formedness
- timestamp status
- signature envelope validity
- `authority: false`
- `truth_claim: false`
- `inference_performed: false`
- `state_mutated: false`

Replay reports must not include:

- proposition truth
- evidence sufficiency
- legal meaning
- causal inference
- confidence promotion
- graph-derived state mutation
- EAS attestation truth
- on-chain finality

## Example reports

- `witness/reports/rp-001-witness-replay.example.json`
- `witness/reports/rp-002-eas-witness-replay.example.json`

## Boundary

Witness replay is a consumer of ReceiptOS representation frames. It is not an inference engine.

The integration line is:

```text
ReceiptOS frame -> base validator -> optional profile validator -> witness replay report
```

The forbidden line is:

```text
ReceiptOS frame -> truth / authority / causation / legal conclusion
```

## Invariants

- Identical frame + identical flags produce identical report fields, except for production-time freshness checks.
- `--disable-timestamp` is for deterministic fixture replay only.
- Base validation remains strict and unchanged.
- Profile validation composes above base validation.
- No replay result may promote `authority` or `truth_claim`.
