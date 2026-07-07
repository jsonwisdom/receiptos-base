# Real Load Runner Adapter v0.1

## Purpose

Defines the seam between the witness harness and a future authorized JOY replay load runner.

This version is adapter-only.

## Inputs

```text
transform_version
target_qps
duration_min
replay_target
telemetry_sink
```

## Outputs

```text
REAL_LOAD_RESULT_V0_1
status = LOAD_CANDIDATE | GOVERNANCE_GAP
metrics
failed_conditions
output_hash
```

## v0.1 rule

The adapter fails closed with `GOVERNANCE_GAP` until an authorized runner is connected.

## Doctrine

```text
authority=false
no_fake_green=true
no promotion claim from adapter output alone
```
