# Lesson 022 Migration Guide v0.1

Migration guide for moving existing mock VA claim arena fixtures to the Evidence Pointer Schema v0.1.

Authority: false.
No fake green.
Mock-only migration.
No raw record migration.

## Migration Rule

Existing mock cases may upgrade fictional evidence placeholders into schema-shaped mock pointers.

Real records must not be imported.

## Before

fictional_evidence_pointers may be loose text placeholders.

## After

fictional_evidence_pointers should use:

- pointer
- case_ref
- timestamp

## Example

{
  "pointer": "mock://MOCK-VA-CASE-001/evidence/service-context",
  "case_ref": "MOCK-VA-CASE-001",
  "timestamp": "2026-07-09T00:00:00Z"
}

## Final State

Migration preserves mock-only witness posture.

Final state: migration guide surface only.
