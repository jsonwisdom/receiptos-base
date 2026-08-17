#!/usr/bin/env python3

from characterization_delta import build_audit, classify_response
from semantic_rendering import (
    ALLOWED_PROVEN_RENDERINGS,
    FORBIDDEN_RENDERINGS,
    SEMANTIC_TYPE,
    assert_no_forbidden_promotions,
    render_observer_result,
)


def main() -> None:
    match = build_audit("X", "X")
    match.validate()
    assert match.comparison_state == "MATCH"
    assert match.intent == "NOT_ASSERTED"
    assert match.deception == "NOT_ASSERTED"
    assert match.guilt == "NOT_ASSERTED"
    assert match.authority_created is False

    delta = build_audit("X", "Y")
    delta.validate()
    assert delta.comparison_state == "DELTA_OBSERVED"
    assert delta.claim_true == "NOT_ASSERTED"
    assert delta.which_characterization_is_correct == "NOT_ASSERTED"
    assert classify_response(answer_received=False, agrees=None) == "GAP"
    assert classify_response(answer_received=True, agrees=True) == "PASS"
    assert classify_response(answer_received=True, agrees=False) == "CONFLICT"

    # T16 — PROVEN_SEMANTIC_RENDERING_GUARD
    for wording in ALLOWED_PROVEN_RENDERINGS:
        rendered = render_observer_result("PROVEN", wording=wording)
        assert rendered.semantic_type == SEMANTIC_TYPE
        assert rendered.evidence_gate_proven is True
        assert rendered.claim_proven is False
        assert rendered.allegation_proven is False
        assert rendered.fraud_proven is False
        assert rendered.guilt_established is False
        assert rendered.doj_endorsement is False
        assert rendered.legal_finding is False
        assert rendered.fail_closed is True
        assert rendered.authority_created is False

    for wording in FORBIDDEN_RENDERINGS:
        try:
            render_observer_result("PROVEN", wording=wording)
        except ValueError:
            pass
        else:
            raise AssertionError(f"forbidden rendering was accepted: {wording}")

    try:
        assert_no_forbidden_promotions(["CLAIM_PROVEN"])
    except ValueError:
        pass
    else:
        raise AssertionError("semantic promotion was accepted")

    print("PASS: delta boundary + T16 PROVEN semantic rendering guard")


if __name__ == "__main__":
    main()
