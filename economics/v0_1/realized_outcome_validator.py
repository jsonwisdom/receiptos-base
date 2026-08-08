"""Realized Economic Outcome Validator V0.1 — implementation stub.

Required behavior when implemented:
- validate REALIZED_ECONOMIC_OUTCOME_RECEIPT_V0_1 structure;
- recompute all seven realized cost components, profit, and margin;
- recompute forecast variances against the referenced decision receipt;
- enforce not_attempted -> revenue=0 and settlement_status=none;
- validate evidence/witness references without promoting them into authority;
- reject any stored arithmetic or variance drift.

Exit-code contract:
0 = semantic PASS
1 = semantic/schema FAIL
2 = malformed/missing input
3 = schema-pin failure
4 = internal evaluator failure

Error taxonomy: SCHEMA_INVALID, ARITHMETIC_MISMATCH, VARIANCE_MISMATCH,
DECISION_LINK_MISMATCH, ACTION_LINK_MISMATCH, NON_ATTEMPTED_INVARIANT_VIOLATION,
AUTHORITY_BOUNDARY_VIOLATION.
"""

EXIT_PASS = 0
EXIT_VALIDATION_FAIL = 1
EXIT_INPUT_ERROR = 2
EXIT_SCHEMA_PIN_FAIL = 3
EXIT_INTERNAL_ERROR = 4


def validate_realized_outcome(*args, **kwargs):
    """Validate one realized outcome; intentionally unimplemented in scaffold."""
    raise NotImplementedError("Realized Outcome Validator V0.1 is a scaffold only")
