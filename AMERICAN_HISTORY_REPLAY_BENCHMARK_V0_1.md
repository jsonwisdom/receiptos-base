# AMERICAN HISTORY REPLAY BENCHMARK V0.1

Status: **PRE-CONTRACT-SEAL**  
Authority: **FALSE**

## Purpose

Replay historical claims against identical sealed evidence bytes and measure model agreement only after semantic validation. Structured output is not verified output.

## Sole execution path

```text
IDENTICAL EVIDENCE BYTES
        ↓
MULTI_MODEL
        ↓
SEMANTIC VALIDATION
        ↓
CONSENSUS METRICS
```

This is the only valid evaluation route.

## Prohibited routes

The following are invalid and fail closed:

- model-specific evidence or tuning;
- external citations or browsing during an evaluation run;
- post-hoc narrative adjustment of a model answer;
- partial scoring after a detected hazard;
- treating token ownership, model confidence, formatting, or consensus as proof;
- promoting `audit_verified=true` before `semantic_validation=PASS`.

Outside sources are forbidden unless the new bytes are added to `EVIDENCE_MANIFEST_V0_1`, hashed, the manifest is re-sealed, and the replay is restarted from the new sealed evidence set.

## Round structure

### Round 0 — discovery

Purpose: identify failure modes, missing receipt fields, ambiguous rules, and semantic hazards. Round 0 may change the benchmark contract. Its outputs are not comparable final scores.

### Round 1+ — replay

Every participating model receives identical evidence bytes. No model-specific source additions are allowed. Any change to evidence bytes creates a new manifest/seal and invalidates cross-round comparison with the prior evidence set.

## Receipt chain

Every replay object must preserve:

```text
FACT → EVIDENCE → RULE → AUTHORITY → ACTION → OUTCOME
```

The schema separately records `semantic_validation` and `audit_verified`.

Invariant:

```text
semantic_validation != PASS  => audit_verified = false
```

## Closed-world evidence

Replay citation fields contain manifest entry IDs only. Draft-07 JSON Schema validates the citation-ID format but cannot enforce a data-dependent foreign-key constraint against `manifest.entries[*].id`. Therefore the semantic validator MUST check membership before scoring.

If any citation ID is absent from the sealed manifest:

```text
hazard = OUTSIDE_SOURCE_USE
semantic_validation = FAIL
scoring = HALT
all metrics = INVALID / null
```

No URL, model memory, browser result, or unsealed side material may substitute for a manifest ID.

## Quantitative normalization

For any quantitative field:

```text
status ∈ {not_attempted, not_observed}
    => value = 0
    => unit = "none"
```

This normalization is schema-enforced.

## Fail-closed hazards

The scoring contract halts on:

- `LANGUAGE_DRIFT`
- `RECEIPT_INCOMPLETE`
- `QUANTITATIVE_ELISION`
- `LEGISLATIVE_MISATTRIBUTION`
- `OUTSIDE_SOURCE_USE`

No partial metric survives a hazard.

## JAYWISDOM token utility boundary

The Base token may be used only as replay-access eligibility under `JAYWISDOM_TOKEN_UTILITY_V0_1.json`.

```text
TOKEN BALANCE → ACCESS ELIGIBILITY
TOKEN BALANCE ≠ EVIDENCE
TOKEN BALANCE ≠ SEMANTIC PASS
TOKEN BALANCE ≠ SCORE
TOKEN BALANCE ≠ AUTHORITY
```

Public verification of receipts remains permissionless.

## Authority lifecycle

`AUTHORITY=FALSE` throughout benchmark definition, discovery, replay, scoring, and token eligibility. No model output, token holding, metric, or consensus creates authority.

Only an explicit future `CONTRACT_SEAL` may change the authority state, and that seal must be independently receipted. Until then:

```text
AUTHORITY_CREATED = FALSE
```

## Next benchmark fixture

`GI_BILL_1944` is not authorized for Round 1 scoring until the four V0.1 contract files and the semantic closed-world validator pass validation.
