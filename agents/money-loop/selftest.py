#!/usr/bin/env python3
"""Synthetic deterministic tests. A PASS is not evidence of income."""

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from engine import GameError, apply_event  # noqa: E402

def ev(i, typ, verified=True, amount=None):
    item = {
        "event_id": f"SYN-{i:02d}-{typ}",
        "type": typ,
        "authority": False,
        "evidence": {
            "ref": f"synthetic://fixture/{i}",
            "kind": "SYNTHETIC_TEST_FIXTURE",
            "verified": verified,
        },
    }
    if amount is not None:
        item["amount_cents"] = amount
    return item

def main():
    state = json.loads((HERE / "state.genesis.json").read_text())

    # Anti-hype gate: revenue cannot jump directly from IDEA.
    try:
        apply_event(state, ev(0, "REVENUE_VERIFIED", amount=10000))
    except GameError:
        pass
    else:
        raise AssertionError("revenue transition skipped evidence ladder")

    # Synthetic receipts cannot cross into production/real-money mode.
    production_state = dict(state)
    production_state["production_runtime"] = True
    try:
        apply_event(production_state, ev(99, "ASSET_CREATED"))
    except GameError:
        pass
    else:
        raise AssertionError("synthetic evidence crossed production membrane")

    sequence = [
        ev(1, "ASSET_CREATED"),
        ev(2, "PUBLISHED"),
        ev(3, "COST_VERIFIED", amount=250),
        ev(4, "SETTLEMENT_SEEN", verified=False),
        ev(5, "REVENUE_VERIFIED", amount=1000),
        ev(6, "PROFIT_VERIFIED"),
    ]
    for event in sequence:
        state = apply_event(state, event)["state"]

    assert state["stage"] == "PROFIT_VERIFIED"
    assert state["score"]["revenue_verified_cents"] == 1000
    assert state["score"]["cost_verified_cents"] == 250
    assert state["score"]["profit_verified_cents"] == 750
    assert state["authority"] is False
    assert state["flags"]["profit_verified"] is True

    print(json.dumps({
        "status": "PASS",
        "test_mode": "SYNTHETIC_ONLY",
        "final_stage": state["stage"],
        "synthetic_profit_cents": state["score"]["profit_verified_cents"],
        "money_made_proven": False,
        "authority_created": False,
    }, sort_keys=True))

if __name__ == "__main__":
    main()
