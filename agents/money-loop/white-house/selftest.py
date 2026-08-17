#!/usr/bin/env python3

from agents.money_loop.white_house.characterization_delta import build_audit, classify_response


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

    print("PASS: characterization delta != deception/fraud/intent/guilt")


if __name__ == "__main__":
    main()
