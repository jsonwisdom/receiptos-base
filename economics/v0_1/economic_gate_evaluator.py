"""Economic Gate Evaluator V0.1 — implementation stub.

Deterministic target semantics:
- hard predicate failure or incomplete forecast -> REJECT;
- hard predicates pass + human_override_required -> HUMAN_REVIEW;
- hard predicates pass + no human override -> ECONOMICALLY_ELIGIBLE;
- ECONOMICALLY_ELIGIBLE never means EXECUTION_AUTHORIZED.

Exit-code contract:
0 = gate evaluation completed and semantically consistent
1 = gate/schema/policy validation failure
2 = malformed/missing input
3 = schema-pin failure
4 = internal evaluator failure

Error taxonomy: FORECAST_INCOMPLETE, HARD_LIMIT_VIOLATION, POLICY_INVALID,
AUTHORITY_INPUT_INVALID, SPEND_POLICY_INPUT_INVALID, DECISION_MISMATCH.
"""

DECISIONS = ("ECONOMICALLY_ELIGIBLE", "REJECT", "HUMAN_REVIEW")

EXIT_PASS = 0
EXIT_VALIDATION_FAIL = 1
EXIT_INPUT_ERROR = 2
EXIT_SCHEMA_PIN_FAIL = 3
EXIT_INTERNAL_ERROR = 4


def evaluate_economic_gate(*args, **kwargs):
    """Evaluate economic eligibility; intentionally unimplemented in scaffold."""
    raise NotImplementedError("Economic Gate Evaluator V0.1 is a scaffold only")
