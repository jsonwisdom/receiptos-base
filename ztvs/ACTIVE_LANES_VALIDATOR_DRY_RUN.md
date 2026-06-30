# ACTIVE_LANES v2 Validator Dry-Run

Status: deterministic reference
Authority: false
Validator: `ztvs/active_lanes_validator.py`
Lane file: `ACTIVE_LANES.md`

This dry-run defines expected validator behavior for rejection and admissible cases.

## 1. authority=true rejection

```text
LANE: TEST_AUTH
STATUS: YELLOW
STATUS_SOURCE: REPORTED
RECEIPT_PTR: NULL
authority: true
```

Expected:

```text
FAIL:
  - [TEST_AUTH] authority must be 'false', got 'true'
```

## 2. Symbolic RECEIPT_PTR rejection

```text
LANE: TEST_SYMBOLIC
STATUS: RED
STATUS_SOURCE: REPORTED
RECEIPT_PTR: RENDER_BUILD_05_26
authority: false
```

Expected:

```text
FAIL:
  - [TEST_SYMBOLIC] Symbolic or invalid RECEIPT_PTR: RENDER_BUILD_05_26
```

## 3. GREEN without verified receipt

```text
LANE: TEST_GREEN
STATUS: GREEN
STATUS_SOURCE: REPORTED
RECEIPT_PTR: NULL
authority: false
```

Expected:

```text
FAIL:
  - [TEST_GREEN] STATUS=GREEN requires STATUS_SOURCE=VERIFIED_RECEIPT; got STATUS_SOURCE=REPORTED
```

## 4. Manual AUDITOR_VIEW rejection

```text
LANE: TEST_AUDITOR_VIEW
STATUS: YELLOW
STATUS_SOURCE: INFERRED
RECEIPT_PTR: NULL
AUDITOR_VIEW: REPORTED_UNVERIFIED
authority: false
```

Expected:

```text
FAIL:
  - [TEST_AUDITOR_VIEW] Manual AUDITOR_VIEW present; must be derived, not declared
  - [TEST_AUDITOR_VIEW] Unknown field 'AUDITOR_VIEW' not in EXT-001 schema
```

Note: current validator emits both errors because `AUDITOR_VIEW` is prohibited directly and also rejected by the strict unknown-field membrane.

## 5. Valid lane should PASS

```text
LANE: TEST_VALID
STATUS: GREEN
STATUS_SOURCE: VERIFIED_RECEIPT
RECEIPT_PTR: sha256:22b00da22b00da22b00da22b00da22b00da22b00da22b00da22b00da22b00da
authority: false
```

Expected:

```text
PASS
```

## Proof

The validator rejects:

- symbolic provenance
- authority drift
- premature GREEN
- manual AUDITOR_VIEW
- unknown lane fields
- VERIFIED_RECEIPT without a non-NULL receipt pointer

The validator accepts only lane entries that can be consumed mechanically by the replay plane.

Authority remains false.
