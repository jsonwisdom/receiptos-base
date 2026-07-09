# Lesson 016 Import Schema v0.1

Witness-only import schema for the Lessons 010-015 kids-safe training spine.

Authority: false.
No fake green.
No diagnosis.
No legal conclusion.
No benefits prediction.
No wallet or payment claim.
No child financialization.
No raw private records.
No inference from imported rows.
No aggregation from imported rows.

## Purpose

Lesson 016 defines a safe import surface that allows previously exported review rows to be re-ingested for human inspection only.

This closes the loop:

Story -> Functional Impact Grid -> Evidence Pointers -> Consistency Check -> Batch Template -> Review Packet -> Import Schema

## Allowed Import Fields

- row_id
- story_summary
- symptom_language
- frequency
- duration
- functional_impact
- reference_pointer
- mirror_check
- runtime_receipt_id
- reviewer_note

## Blocked Import Fields

- diagnosis
- legal conclusion
- benefits prediction
- medical authority
- wallet address as proof
- payment link
- raw private record
- child financialization signal
- cross-row inference
- aggregate score
- eligibility claim

## Import Review Rules

- Imported rows remain witness-only.
- Reference pointers remain reference-only.
- Mirror checks detect wording drift only.
- Review notes cannot become claims.
- Import does not prove truth.
- Import does not authorize action.
- Import does not create entitlement.
- Import does not validate identity, wallet control, or payment authority.

## Final State

Lesson 016 creates a bidirectional import/export review loop while preserving the kids-safe membrane.

Final state: witness-only import surface.
