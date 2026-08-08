"""Agent Economics Replay Engine V0.1 — implementation stub.

Target replay chain:
policy -> decision receipt -> Base MCP action/authorization evidence -> realized outcome.

Required behavior when implemented:
- verify schema pins before replay;
- validate decision arithmetic and deterministic gate result;
- preserve separate execution-authorization boundary;
- validate realized arithmetic and forecast variance;
- emit replay evidence without mutating source receipts;
- never promote witness existence into payment, settlement, or execution authority.

Exit-code contract:
0 = replay PASS
1 = replay/semantic FAIL
2 = malformed/missing referenced artifact
3 = schema-pin failure
4 = internal replay failure

Error taxonomy: BROKEN_LINEAGE, DECISION_INVALID, AUTHORIZATION_MISSING,
OUTCOME_INVALID, WITNESS_MISMATCH, REPLAY_DIVERGENCE, AUTHORITY_BOUNDARY_VIOLATION.
"""

EXIT_PASS = 0
EXIT_REPLAY_FAIL = 1
EXIT_INPUT_ERROR = 2
EXIT_SCHEMA_PIN_FAIL = 3
EXIT_INTERNAL_ERROR = 4


def replay_economic_outcome(*args, **kwargs):
    """Replay one economic outcome chain; intentionally unimplemented."""
    raise NotImplementedError("Agent Economics Replay Engine V0.1 is a scaffold only")
