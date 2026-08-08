"""Decision Receipt Validator V0.1 — implementation stub.

Required behavior when implemented:
- validate ECONOMIC_DECISION_RECEIPT_V0_1 structure;
- recompute all seven expected cost components, profit, and margin;
- verify the exact limits_evaluated policy snapshot and policy hash;
- verify expected_slippage_bps and failure probability predicates;
- reject stored arithmetic or decision drift;
- preserve ECONOMICALLY_ELIGIBLE != EXECUTION_AUTHORIZED.

Exit-code contract for future CLI surface:
0 = semantic PASS
1 = semantic/schema FAIL
2 = malformed/missing input
3 = schema-pin failure
4 = internal evaluator failure

Error taxonomy: SCHEMA_INVALID, ARITHMETIC_MISMATCH, POLICY_SNAPSHOT_MISMATCH,
POLICY_HASH_MISMATCH, DECISION_MISMATCH, AUTHORITY_BOUNDARY_VIOLATION.
"""

EXIT_PASS = 0
EXIT_VALIDATION_FAIL = 1
EXIT_INPUT_ERROR = 2
EXIT_SCHEMA_PIN_FAIL = 3
EXIT_INTERNAL_ERROR = 4


def validate_decision_receipt(*args, **kwargs):
    """Validate one decision receipt; intentionally unimplemented in scaffold."""
    raise NotImplementedError("Decision Receipt Validator V0.1 is a scaffold only")
