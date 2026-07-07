# LOAD_VERIFICATION_WITNESS_V0_1

## Purpose

This witness schema prevents public or runtime promotion to `LOAD_VERIFIED` from an incomplete harness summary.

A harness summary is not enough.

## Required surfaces

A valid load verification witness must include:

- `receipt_integrity`
- `transparency_continuity`
- `transform_version_pinned`
- `doctrine_guards`
- `membrane_unchanged`
- `failed_conditions`

## Promotion rule

`gate_result.status = LOAD_VERIFIED` is admissible only when:

```text
failed_conditions = []
receipt_integrity.jcs_canonical = true
receipt_integrity.signature_verified = true
transform_version_pinned = true
doctrine_guards.authority_false = true
doctrine_guards.no_fake_green = true
doctrine_guards.no_synthetic_pass = true
membrane_unchanged = true
```

## Default classification

Incomplete claimed load witnesses must be treated as:

```text
GOVERNANCE_GAP
```

not `LOAD_VERIFIED`.
