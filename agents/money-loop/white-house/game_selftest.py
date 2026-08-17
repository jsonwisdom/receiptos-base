#!/usr/bin/env python3

from game import GAME_ID, ReplayRound


def main() -> None:
    ready = ReplayRound(
        round_id="SYNTHETIC_READY",
        source_pointer_bound=True,
        source_bytes_replayed=True,
        identity_provenance_replayed=True,
        delta_classified=True,
        semantic_rendering_bounded=True,
        exact_head_executed=True,
        bypass_surfaces_blocked=True,
    )
    ready_receipt = ready.to_receipt()
    assert ready_receipt["game"] == GAME_ID
    assert ready_receipt["mechanics_points"] == 7
    assert ready_receipt["round_state"] == "REPLAY_READY"
    assert ready_receipt["claim_truth_proven"] is False
    assert ready_receipt["human_guilt_determined"] is False
    assert ready_receipt["score_proves_truth"] is False
    assert ready_receipt["win_determines_guilt"] is False
    assert ready_receipt["authority_created"] is False

    held = ReplayRound(
        round_id="SYNTHETIC_HOLD",
        source_pointer_bound=True,
        source_bytes_replayed=True,
        identity_provenance_replayed=True,
        delta_classified=True,
        semantic_rendering_bounded=True,
        exact_head_executed=False,
        bypass_surfaces_blocked=True,
    )
    held_receipt = held.to_receipt()
    assert held_receipt["mechanics_points"] == 6
    assert held_receipt["round_state"] == "HOLD"
    assert "EXACT_HEAD_EXECUTED" not in held_receipt["badges"]

    for forbidden in (
        {"claim_truth_proven": True},
        {"human_guilt_determined": True},
        {"authority_created": True},
    ):
        kwargs = dict(
            round_id="NEGATIVE",
            source_pointer_bound=True,
            source_bytes_replayed=True,
            identity_provenance_replayed=True,
            delta_classified=True,
            semantic_rendering_bounded=True,
            exact_head_executed=True,
            bypass_surfaces_blocked=True,
        )
        kwargs.update(forbidden)
        try:
            ReplayRound(**kwargs).to_receipt()
        except ValueError:
            pass
        else:
            raise AssertionError(f"forbidden promotion accepted: {forbidden}")

    print("PASS: White House Replay Arena mechanics-only scoring")


if __name__ == "__main__":
    main()
