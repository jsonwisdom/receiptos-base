# Move 2 Weld Stability Report

Date: 2026-07-08 12:00 UTC  
Mode: external/manual observation  
Source PR: #129  
Merge commit: `42ddc09cd2a94d90beac5ed8d307a719a01d6d4a`  
Witness commit: `9f926559b2899efbe0c8188144819b6137f1c05d`

## Baseline

The Move 2 DeerFlow to ReceiptOS weld was merged to mainline through PR #129.

```text
base_sha: 86550e7c461220847b5e2d48cc33012b51e23efb
head_sha: 9ea79d26403040bcbd5dec38be99cdd414bb8c55
merge_commit_sha: 42ddc09cd2a94d90beac5ed8d307a719a01d6d4a
```

## Payload binding

Canonical payload text:

```text
DeerFlow:v1.0:receiptos-weld:86550e7c461220847b5e2d48cc33012b51e23efb:authority=false
```

Canonical SHA-256:

```text
8bedf2e76c14ead78453e91c7532639b7c4bb234f3fa79100c0ec45a6f460805
```

## Governance state

```text
move_2_weld: MAINLINE_MERGED
observation_layer: EXTERNAL_MANUAL
authority: false
fake_green: forbidden
```

## Result

The repository now contains a manual observation witness for the Move 2 weld baseline. This report does not claim automated monitoring or autonomous execution.

No fake green.
