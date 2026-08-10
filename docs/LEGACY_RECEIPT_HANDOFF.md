# Legacy Receipt Handoff v0.1

## Purpose

Legacy receipt handoff is a quarantine-first preservation lane.

It preserves out-of-scope receipt artifacts without admitting them into `ALMS_WITNESS_LEDGER`.

## Protocol

```text
LEGACY_RECEIPT_HANDOFF_V0_1
```

## Core rule

```text
LEGACY_RECEIPT_ROUTER is not a trust lane.
It is a quarantine and preservation lane.
```

## Handoff behavior

For receipts outside `FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2`, the router creates a sidecar record:

```text
legacy-handoffs/<source_sha256>.handoff.json
```

The source receipt is not changed.

## Required handoff posture

```text
authority=false
memory_safe=false
mutation_performed=false
alms_witness_indexed=false
admissibility=OUT_OF_SCOPE
route=LEGACY_RECEIPT_ROUTER
```

## Allowed actions

```text
review under legacy policy
define separate receipt-family schema
migrate only with observed evidence
```

## Forbidden actions

```text
mutate source receipt
auto-upgrade legacy receipt type
invent missing evidence
index legacy artifact as ALMS witness memory
```

## Migration invariant

Legacy receipt admission requires a separate receipt-family schema.

Do not force old shapes into the free-only three-surface schema.

## CLI

Dry run:

```bash
python3 router/legacy_receipt_handoff.py --dry-run receipts/
```

Write handoff sidecars:

```bash
python3 router/legacy_receipt_handoff.py receipts/
```

## Final boundary

```text
authority=false
no_fake_green=true
```
