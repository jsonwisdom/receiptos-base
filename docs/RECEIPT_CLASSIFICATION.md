# Receipt Classification v0.1

## Purpose

Classification is the bridge between validation and ALMS memory indexing.

The classifier does not decide truth. It decides routing.

It answers:

```text
Should this artifact enter ALMS memory?
If yes, under what witness-only scope?
If no, why not?
```

## Classification type

```text
RECEIPT_CLASSIFICATION_V0_1
```

## Routes

### ALMS_WITNESS_LEDGER

The receipt is admissible as witness-only ALMS memory input.

Allowed only when:

```text
receipt_type=FREE_ONLY_THREE_SURFACE_RECEIPT_V0_2
authority=false
free_only=true
no_fake_green=true
TX_RECEIPT_SURFACE=observed
LOG_SURFACE=observed
STATE_READ_SURFACE=observed
debug_traceTransaction=not_used
internal_calls_observed=false
```

### LEGACY_RECEIPT_ROUTER

The artifact is not part of this classifier's receipt family.

It is preserved and routed elsewhere.

It is not mutated into a three-surface receipt.

### REJECTED_INTAKE

The artifact is malformed or violates the free-only three-surface boundary.

It must not enter ALMS witness memory.

## Admissibility states

```text
ADMISSIBLE_WITNESS
OUT_OF_SCOPE
INVALID
```

## Surface levels

```text
THREE_SURFACE_V0_2
UNKNOWN
NONE
```

## Forbidden scope

The classifier keeps the following out of ALMS memory unless a separate receipt family explicitly supports them:

```text
wallet_control
creator_identity
token_authenticity
payment_or_sale
legal_ownership
trace_internal_calls
```

## Non-claims

Classification does not prove:

- ownership
- identity
- authenticity
- payment
- sale
- legality
- trace/internal calls
- real-world truth

## CLI

Pretty JSON:

```bash
python3 classifier/free_only_three_surface_classifier.py receipts/
```

JSON Lines:

```bash
python3 classifier/free_only_three_surface_classifier.py --jsonl receipts/
```

## Final boundary

```text
authority=false
no_fake_green=true
```
