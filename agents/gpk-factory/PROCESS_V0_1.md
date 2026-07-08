# GPK Factory Process v0.1

**Factory:** Jay's GitHub Garbage Pail Kids Factory  
**Mode:** text-only  
**Authority:** false  
**Canon mutation:** forbidden unless canon-freeze workflow authorizes it  
**Delivery methods:** forbidden  
**Image output:** forbidden  
**Image prompts:** forbidden

## 1. Purpose of the Process

This process turns evidence-backed observations into structured, text-only satirical card packets.

It is not a media generator.  
It is not a publisher.  
It is not a minting system.  
It is not a truth authority.

It is a governed factory pipeline for building receipt-backed card artifacts that can be reviewed, validated, hashed, and traced through GitHub.

## 2. Process Law

```text
NO_RECEIPT_NO_CARD
NO_IMAGE
NO_IMAGE_PROMPT
NO_DELIVERY_METHODS
NO_SILENT_CANON_MUTATION
AUTHORITY_FALSE
```

## 3. Standard Flow

```text
DRAFT_INPUT
  -> RECEIPT_RICKY_INTAKE
  -> CANON_CARRIE_READINESS_CHECK
  -> LORE_LARRY_DRIFT_AUDIT
  -> PRESS_PATTY_TEXT_PACKET
  -> HUMAN_REVIEW_REQUIRED
```

Correction branch:

```text
CANON_CARRIE_BLOCKER or LORE_LARRY_DRIFT
  -> OVERRIDE_OLLIE_QUARANTINE_REVIEW
  -> CORRECTION_BUNDLE_REQUIRED
```

## 4. Agent Responsibilities

### Receipt Ricky

Collects the evidence packet.

Must verify:

- evidence anchor exists
- observation is separated from claim
- no private secret is included
- authority remains false

Output:

```text
GPK_EVIDENCE_PACKET
```

### Canon Carrie

Checks readiness for canon review.

Must verify:

- schema fields exist
- hashes are present or computable
- card id is unique within test lane
- no direct canon promotion occurs
- authority remains false

Output:

```text
GPK_CANON_READINESS_REPORT
```

### Lore Larry

Checks narrative consistency.

Must verify:

- no overclaiming
- no retcon without supersession
- satire remains bounded by evidence
- no contradictory lore state exists

Output:

```text
GPK_LORE_DRIFT_REPORT
```

### Press Patty

Packages the text-only review packet.

Must verify:

- upstream reports exist
- no blocking issues remain
- no delivery method is invoked
- no image or image prompt exists
- authority remains false

Output:

```text
GPK_RELEASE_PACKET
```

### Override Ollie

Handles correction, quarantine, and supersession.

Must verify:

- quarantine happens before override
- target canon hash is referenced
- original canon remains untouched
- correction bundle is append-only

Output:

```text
GPK_OVERRIDE_ARTIFACT
```

## 5. Disposable Test Rule

First target:

```text
gpk-card-test-001
```

Allowed write path:

```text
agents/gpk-factory/outbox/gpk-card-test-001/**
```

Forbidden write paths:

```text
canon/**
quarantine/**
```

## 6. Batch Rule v0.3

A governed batch run must satisfy:

```text
parallel: true
anchored: true
sealed: true
lineage_verified: true
headless: true
batch_size: 16
storage_anchored: true
tool_boundaries: quarantined
authority: false
```

Current v0.3 summary anchor:

```text
3a531ef6a4002b6f1597524994d6d61f6b89e410d95e7ff6b76b963f24d45a15
```

## 7. Receipt Outputs

A successful disposable factory run emits:

```text
agents/gpk-factory/outbox/gpk-card-test-001/factory_test_summary.json
```

A successful batch run emits:

```text
receipts/gpk-factory/batches/<batch_id>/summary.json
receipts/gpk-factory/batches/<batch_id>/summary_hash.txt
```

## 8. Failure Rule

The process fails closed if any condition appears:

```text
missing_evidence
schema_error
authority_true
image_output_detected
image_prompt_detected
delivery_method_detected
canon_mutation_detected
quarantine_mutation_without_ollie
summary_hash_mismatch
lineage_check_missing
unknown_tool_invoked
```

## 9. Review Rule

No artifact becomes canon merely because the factory generated it.

Every output remains:

```text
TEXT_PACKET_FOR_REVIEW
AUTHORITY_FALSE
```

until a separate canon workflow accepts it.

## 10. Process Status

```text
PROCESS_DEFINED: true
REAL_CANON_TOUCHED: false
QUARANTINE_TOUCHED: false
AUTHORITY: false
TEXT_ONLY_MEMBRANE: locked
```
