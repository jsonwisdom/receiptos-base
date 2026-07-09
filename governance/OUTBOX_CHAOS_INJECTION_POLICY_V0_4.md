# Outbox Chaos-Injection Policy v0.4

## Purpose

Outbox chaos-injection is a constitutional gate for ReceiptOS v0.4.

The outbox is the final egress membrane. If an artifact can leave the system without a complete lineage receipt, parent canon reference, and completeness-gate pass, the replay engine cannot claim deterministic export behavior.

## Governing rule

No v0.4 rail may advance until the outbox membrane survives chaos-injection.

This includes, but is not limited to:

- Scale Gate activation
- Shard Proof integration
- Replay Board automation
- Dynamic batch promotion
- Downstream determinism claims

## Required criteria

Chaos-injection must verify all of the following:

1. Partial lineage rejection is enforced.
2. Storm-batch abort semantics are verified.
3. Write-lock enforcement is confirmed.
4. The pre-outbox hook is non-bypassable.
5. Completeness-gate invariants hold under stress.

## Failure action

Any failure is a hard halt.

A hard halt means:

- No promotion to green.
- No scale rail activation.
- No downstream determinism claim.
- No silent bypass.
- A red witness must be recorded to the Replay Board.

## Pass witness

A pass requires an explicit witness artifact:

```text
v0.4-CHAOS-PASS
```

The witness must include:

- Test command
- Commit SHA
- Test result
- Failed conditions, if any
- Outbox hook version
- Completeness gate version
- Authority flag
- Witness-only flag

## Doctrine

```text
NO_FAKE_GREEN: true
WITNESS_ONLY: true
AUTHORITY: false
```

## Human summary

The canon can be green while the outbox is still unsafe.

The system is not allowed to scale until the outbox proves that bad artifacts cannot escape under adversarial conditions.
