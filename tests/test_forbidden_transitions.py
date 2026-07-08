"""
ReceiptOS forbidden transition scaffold.

Status: scaffold only.
Issue: #119.

This file intentionally contains no passing implementation test yet.
The next implementation phase must validate state_machine/transitions.yaml.

Required future negative cases:
- CAPTURED -> APPROVED rejects
- ATTESTED -> VARIANT_GENERATED rejects
- PUBLISHED -> VARIANT_GENERATED rejects
- PUBLISHED -> ARCHIVED rejects
- ARCHIVED -> any state rejects
- REJECTED -> APPROVED rejects unless routed through EVIDENCE_REVIEW
"""
