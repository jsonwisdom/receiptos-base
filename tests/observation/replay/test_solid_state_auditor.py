from dataclasses import FrozenInstanceError

import pytest

from solid_state_auditor import (
    EvidenceStatus,
    ReplayStatus,
    ReverseReplayStatus,
    SolidStateAuditor,
    canonical_bytes,
)


def _rubric():
    return {
        "all_verified": lambda state: all(
            item["verified"] for item in state["evidence_items"]
        ),
        "has_evidence": lambda state: state["evidence_count"] > 0,
    }


def test_receipt_is_deterministic_with_explicit_time():
    auditor = SolidStateAuditor(_rubric())
    auditor.submit_evidence("doc", {"x": 1}, verified=True)

    def replay(state):
        return {"state_sha256": __import__("hashlib").sha256(canonical_bytes(state)).hexdigest()}

    def reverse(state, output):
        return {"reconstructed_input": state}

    first = auditor.audit(
        claim="X",
        observed_at="2026-08-04T22:00:00Z",
        replay_fn=replay,
        reverse_replay_fn=reverse,
    )
    second = auditor.audit(
        claim="X",
        observed_at="2026-08-04T22:00:00Z",
        replay_fn=replay,
        reverse_replay_fn=reverse,
    )
    assert first == second
    assert first.receipt_sha256 == second.receipt_sha256


def test_authority_is_permanently_false_and_receipt_frozen():
    auditor = SolidStateAuditor(_rubric())
    receipt = auditor.audit(
        claim="X",
        observed_at="2026-08-04T22:00:00Z",
        replay_fn=lambda state: {},
        reverse_replay_fn=lambda state, output: {"reconstructed_input": state},
    )
    assert receipt.authority_created is False
    assert receipt.operator_required is True
    with pytest.raises(FrozenInstanceError):
        receipt.authority_created = True


def test_empty_evidence_is_missing_not_nonexistent():
    auditor = SolidStateAuditor(_rubric())
    receipt = auditor.audit(
        claim="X",
        observed_at="2026-08-04T22:00:00Z",
        replay_fn=lambda state: {},
        reverse_replay_fn=lambda state, output: {"reconstructed_input": state},
    )
    assert receipt.evidence_status is EvidenceStatus.MISSING
    assert "non-existence" not in " ".join(receipt.reflection_notes).lower()


def test_unverified_is_not_counted_as_conflict():
    auditor = SolidStateAuditor(_rubric())
    auditor.submit_evidence("doc", {"x": 1}, verified=False)
    receipt = auditor.audit(
        claim="X",
        observed_at="2026-08-04T22:00:00Z",
        replay_fn=lambda state: {},
        reverse_replay_fn=lambda state, output: {"reconstructed_input": state},
    )
    assert receipt.conflicts == 0
    assert receipt.unverified_receipts == 1
    assert receipt.evidence_status is EvidenceStatus.MISSING


def test_conflicts_require_explicit_conflict_function():
    auditor = SolidStateAuditor(_rubric())
    auditor.submit_evidence("a", {"value": 1}, verified=True)
    auditor.submit_evidence("b", {"value": 2}, verified=True)
    receipt = auditor.audit(
        claim="X",
        observed_at="2026-08-04T22:00:00Z",
        replay_fn=lambda state: {},
        reverse_replay_fn=lambda state, output: {"reconstructed_input": state},
        conflict_fn=lambda evidence: ["same_subject_incompatible_value"],
    )
    assert receipt.conflicts == 1
    assert receipt.evidence_status is EvidenceStatus.CONFLICTING


def test_reverse_replay_mismatch_is_not_verified():
    auditor = SolidStateAuditor(_rubric())
    auditor.submit_evidence("doc", {"x": 1}, verified=True)
    receipt = auditor.audit(
        claim="X",
        observed_at="2026-08-04T22:00:00Z",
        replay_fn=lambda state: {"ok": True},
        reverse_replay_fn=lambda state, output: {"reconstructed_input": {"wrong": True}},
    )
    assert receipt.replay_status is ReplayStatus.PASS
    assert receipt.reverse_replay_status is ReverseReplayStatus.MISMATCH


def test_replay_exception_is_structured():
    auditor = SolidStateAuditor(_rubric())

    def explode(state):
        raise ValueError("boom")

    receipt = auditor.audit(
        claim="X",
        observed_at="2026-08-04T22:00:00Z",
        replay_fn=explode,
        reverse_replay_fn=lambda state, output: {},
    )
    assert receipt.replay_status is ReplayStatus.FAIL
    assert receipt.replay_output == {"error_type": "ValueError", "error": "boom"}
    assert receipt.reverse_replay_status is ReverseReplayStatus.NOT_RUN
