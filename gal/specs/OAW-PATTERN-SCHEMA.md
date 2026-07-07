# OAW Pattern Schema

**Lineage:** GAL-SPEC-003  
**Status:** ACTIVE  
**Scope:** Structural wallet-behavior classification only

## Boundary

OAW classes describe transaction-flow patterns. They do not assert identity, ownership, motive, compromise, illegality, or intent.

## Global Constraints

```text
NO_OWNERSHIP_INFERENCE = TRUE
NO_MOTIVE_INFERENCE = TRUE
NO_COMPROMISE_FINDING_WITHOUT_EVIDENCE = TRUE
CSV_REQUIRED_FOR_FINALIZATION = TRUE
```

## Classes

### OAW-1: Low-Value Gas-Only Anomaly
Repeated transactions where gas is the dominant measurable output and economic transfers are minimal or absent.

### OAW-2: Repeated Approval Pattern
Multiple token approvals without clear matching downstream transfers in the provided ledger.

### OAW-3: Execute / Approve Loop With Low Net Output
High-frequency `Execute` and/or `Approve` calls with low or unclear economic output, especially where repeated calls target the same counterparty or router-like contract.

### OAW-4: Reverted Burst Pattern
Dense clusters of reverted or failed transactions over a short time window.

### OAW-5: Counterparty-Dominant Interaction Cluster
A transaction set dominated by one contract, router, or counterparty address.

## Finalization Requirements

An OAW classification may be marked FINAL only when:

1. The raw CSV export is available for deterministic replay.
2. The CSV is fingerprinted with SHA-256.
3. Deduplication and normalization are complete under GAL-SPEC-003.
4. Successful and reverted transactions are separated.
5. Gas, method, and counterparty totals are computed.

Until those conditions are met, classifications remain PRELIMINARY.
