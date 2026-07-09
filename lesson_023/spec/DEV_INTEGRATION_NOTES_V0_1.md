# Developer Integration Notes v0.1

Claimlandia Chat: AI Developer Edition is a mock-only webpage fixture.

## Suggested Stack

Frontend:

- Next.js
- React
- static JSON fixtures

Backend:

- FastAPI or Node
- schema validator
- blocked vector scanner
- receipt emitter

Schema:

- lesson_022/schema/evidence-pointer-v1.json

## Required Runtime Guards

- reject non-mock pointers
- reject raw records
- reject PII
- reject PHI
- reject real VA system references
- reject legal advice
- reject medical advice
- reject diagnosis
- reject benefits prediction
- reject rating estimate
- reject eligibility claim
- reject service-connection conclusion
- reject VA outcome prediction

## Output Surfaces

- mock_review_packet.json
- blocked_vector_scan.json
- receipt.json

## Final State

Developer integration notes only.
