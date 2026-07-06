# GAL-SPEC-003: Ledger Consolidation & Provenance Pipeline

**Spec ID:** GAL-SPEC-003  
**Name:** Ledger Consolidation & Provenance Pipeline  
**Status:** RATIFIED  
**Date:** 2026-07-05  

## Purpose

Define the canonical schema and deterministic pipeline for consolidating transaction CSV exports into a replayable ledger artifact.

## Canonical Schema Fields

- `tx_hash`
- `timestamp`
- `block_number`
- `chain`
- `source_wallet`
- `from`
- `to`
- `method`
- `asset`
- `amount`
- `gas_fee`
- `status`
- `tags`

## Pipeline Passes

1. Ingestion & Deduplication
2. Explicit Mapping & Internal Detection
3. Normalization & Sorting
4. Enrichment & Tagging
5. Statistical Aggregation
6. Manifest Generation

## Internal Transfer Logic

```text
flag = (from in registry) AND (to in registry)
```

The wallet registry is static and externally provided. No ownership inference is permitted beyond the explicit registry.

## Manifest Fingerprint

The final ledger artifact must be fingerprinted with SHA-256.

## Execution State

```text
EXECUTION_STATE=BLOCKED_ON_RAW_CSV
NO_OWNERSHIP_INFERENCE=true
INTERNAL_TRANSFER_RULE=registry_only
```

## Compatibility

- Compatible with GAL-SPEC-002 as raw edge-list input for Layer 1 graph generation.
- GAL-PROC-003 identity resolution remains a separate verification step before ledger ingestion.
