# Move 2 — DeerFlow → ReceiptOS Weld Implementation

Issue: #128
Base merge commit: `86550e7c461220847b5e2d48cc33012b51e23efb`

## Objective

Implement the first governed weld demo showing an external execution harness output being adjudicated by ReceiptOS.

Execution harnesses may run. ReceiptOS decides admissibility.

## Scope

This implementation lane is limited to:

1. Accepting a `cloud_observation` packet from an external worker or harness.
2. Binding it through the GCP read-only packet path.
3. Producing either an admissible receipt or a deterministic rejection.
4. Preserving `authority=false` and human-controlled action authority throughout.

## Required demo cases

### Case A — truthful read-only observation

Expected result:

```text
validator: PASS
receipt: emitted
state: ADMISSIBLE_READONLY_OBSERVATION
authority: false
```

### Case B — lied or mutating observation

Expected result:

```text
validator: REJECT
receipt: not emitted
state: DISALLOWED_COMMAND_OR_SCHEMA_FAILURE
authority: false
```

## Boundary

- no runtime cloud execution
- no credential use
- no wallet signing
- no autonomous action authority
- no fake green

Gate > stars.
