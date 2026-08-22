from reflection_skill import (
    CANONICAL_REPLAY_CORE_SHA256,
    reflect_on_verdicts,
)


def test_empty_input_is_fail_closed_and_non_authoritative():
    receipt = reflect_on_verdicts([])
    assert receipt["creates_authority"] is False
    assert receipt["epistemic_status"] == "NO_OBSERVATIONS"
    assert receipt["confidence"] == 0.0
    assert receipt["sample_size"] == 0
    assert receipt["verdict_counts"] == {
        "PASS": 0,
        "FAIL": 0,
        "INDETERMINATE": 0,
    }


def test_all_pass_is_counted_without_promotion():
    verdicts = [
        {
            "verdict": "PASS",
            "reason": "replay_verified",
            "tainted": False,
            "warnings": [],
            "policy_failures": [],
        }
        for _ in range(3)
    ]
    receipt = reflect_on_verdicts(verdicts)
    assert receipt["creates_authority"] is False
    assert receipt["verdict_counts"]["PASS"] == 3
    assert receipt["recommended_next_action"] == (
        "Preserve the receipt and continue observation."
    )


def test_fail_indeterminate_taint_and_policy_are_preserved():
    receipt = reflect_on_verdicts(
        [
            {
                "verdict": "FAIL",
                "reason": "collector_invalid",
                "tainted": True,
                "warnings": ["taint_propagation_enforced"],
                "policy_failures": ["collector_invalid"],
            },
            {
                "verdict": "INDETERMINATE",
                "reason": "missing_expected_hash",
                "tainted": False,
                "warnings": ["missing_expected_hash"],
                "policy_failures": [],
            },
        ]
    )
    assert receipt["verdict_counts"]["FAIL"] == 1
    assert receipt["verdict_counts"]["INDETERMINATE"] == 1
    assert receipt["tainted_count"] == 1
    assert receipt["policy_failure_counts"] == {"collector_invalid": 1}
    assert receipt["warning_counts"] == {
        "missing_expected_hash": 1,
        "taint_propagation_enforced": 1,
    }


def test_input_order_is_recorded_deterministically():
    verdicts = [
        {
            "verdict": "PASS",
            "reason": "hash_verified",
            "tainted": False,
            "warnings": ["b", "a"],
            "policy_failures": [],
        }
    ]
    first = reflect_on_verdicts(verdicts)
    second = reflect_on_verdicts(verdicts)
    assert first == second
    assert first["evidence_receipts"][0]["observation"]["warnings"] == ["a", "b"]


def test_unknown_verdict_becomes_indeterminate_not_invented():
    receipt = reflect_on_verdicts([{"verdict": "UNKNOWN"}])
    assert receipt["verdict_counts"]["INDETERMINATE"] == 1
    assert receipt["reason_counts"] == {"missing_reason": 1}


def test_receipt_is_bound_to_verified_core_hash():
    receipt = reflect_on_verdicts([])
    assert receipt["canonical_replay_core_sha256"] == CANONICAL_REPLAY_CORE_SHA256
    assert CANONICAL_REPLAY_CORE_SHA256 == (
        "f9eb7daffc6bf16a52668716a0cf60c76c011b1a7dd55e695e3d56372a759c27"
    )
