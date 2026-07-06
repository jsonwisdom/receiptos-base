# Round 3 Replay Protection

Round 3 adds replay-window and idempotency controls to the Observation Protocol replay validator. The goal is to prevent stale, future-issued, duplicated, or replayed packets from being promoted while preserving the existing verdict vocabulary:

```text
PASS
FAIL
INDETERMINATE
```

`REAL-WORLD` remains a fixture category only. It is not a validator verdict.

## Status

Canonical anchor: `b8e5726`

Later cleanup migrated the Round 3 replay protection checks into the core validator while preserving the deterministic fixture gate.

## Replay-window semantics

A replay-protected packet may include these root fields:

```text
packet_id
nonce
issued_at
expires_at
replay_window_seconds
```

Replay protection is conditional. If no replay fields are present, the packet is evaluated using Round 2 byte-truth rules. If any replay field is present, the full replay field set is required.

Validator behavior:

| Condition | Verdict | Reason | Tainted |
|---|---:|---|---:|
| All byte-truth and replay-window checks pass | PASS | replay_verified | false |
| Missing replay field | INDETERMINATE | missing_<field> | false |
| Invalid replay timestamp fields | INDETERMINATE | invalid_replay_time_fields | false |
| issued_at is beyond allowed future window | INDETERMINATE | future_issued_at | false |
| expires_at + replay_window_seconds is before now | FAIL | replay_window_exceeded | false |
| packet_id reused in one validation batch | FAIL | duplicate_packet_id | false |
| nonce reused in one validation batch | FAIL | duplicate_nonce | false |

Replay-window failures do not imply authority taint. They are temporal or idempotency failures, not collector-contract violations.

## Deterministic `--now`

The validator and test runner support deterministic temporal evaluation through a frozen `now` value:

```bash
python3 tests/observation/test_replay_validator.py --now 2026-07-06T14:30:00Z
```

This prevents CI drift. Fixtures do not depend on wall-clock time. A packet that passes today should pass tomorrow if evaluated against the same deterministic `--now` timestamp.

The core validator also supports `--now` for direct packet validation:

```bash
python3 tests/observation/replay/validate_replay_packet_v1.py \
  --fixture tests/observation/replay/fixtures/round3/pass_valid_window.packet.json \
  --now 2026-07-06T14:30:00Z
```

## Packet and nonce uniqueness

The core validator accepts optional caller-managed sets:

```python
determine_verdict(
    packet,
    now=now,
    seen_packet_ids=seen_packet_ids,
    seen_nonces=seen_nonces,
)
```

This keeps the core validator stateless while allowing batch orchestration to enforce uniqueness. The test runner owns those sets during fixture execution.

## Byte-truth continuity

Round 3 does not weaken Round 2. The validator still enforces:

```text
sha256(base64decode(raw_payload)) == raw_payload_sha256
byte_length == len(base64decode(raw_payload))
sha256(manifest.content as UTF-8) == manifest.manifest_sha256
expected_hash == sha256(base64decode(raw_payload))
recomputed_hash == sha256(base64decode(raw_payload))
```

Collector-contract failures remain authority taint:

```text
collector_identity.contract_valid == false
→ verdict: FAIL
→ reason: collector_invalid
→ tainted: true
```

## Expected fixture layout

Round 2 fixtures live at:

```text
tests/observation/replay/fixtures/*.packet.json
```

Round 3 replay-protection fixtures live at:

```text
tests/observation/replay/fixtures/round3/*.packet.json
```

The canonical Round 3 fixture set includes:

```text
pass_valid_window.packet.json
fail_time_expired.packet.json
indeterminate_future_issued_at.packet.json
indeterminate_missing_nonce.packet.json
duplicate_a.packet.json
duplicate_b.packet.json
```

The expected CI success message is:

```text
All Round 2 + Round 3 replay fixtures passed.
```

## Promotion boundary

A packet should not be promoted if any of these are true:

```text
verdict == FAIL
verdict == INDETERMINATE
tainted == true
reason in [duplicate_packet_id, duplicate_nonce, replay_window_exceeded]
```

Round 3 protects the replay membrane before live ZoraFactory ingestion by ensuring that evidence packets are not stale, future-issued, or reused within a validation batch.
