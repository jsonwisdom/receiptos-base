#!/usr/bin/env python3

from agents.money_loop.experiments.receipt import build_receipt
from agents.money_loop.experiments.scoreboard import rank
from agents.money_loop.harnesses.base.adapter import MissionEnvelope
from agents.money_loop.harnesses.registry import get_harness


def main() -> None:
    harness = get_harness("deepseek/dsh-001")
    mission = MissionEnvelope(
        mission_id="ML-TEST-0001",
        model_id="deepseek/test-model",
        harness_id="deepseek/dsh-001",
        input_root="sha256:test-input",
        budget_cents=1000,
        time_limit_seconds=3600,
        authority_created=False,
    )
    observation = harness.execute(mission)
    assert observation["money_made"] is False
    assert observation["mission_completed"] is False
    assert observation["authority_created"] is False

    receipt = build_receipt(
        mission_id=mission.mission_id,
        model_id=mission.model_id,
        harness_id=mission.harness_id,
        input_root=mission.input_root,
        budget_cents=mission.budget_cents,
        time_limit_seconds=mission.time_limit_seconds,
        artifact_root="sha256:synthetic-artifact",
        gross_revenue_cents=1000,
        direct_cost_cents=300,
        infra_cost_cents=200,
        profit_verified=True,
    )
    receipt.validate()
    assert receipt.contribution_margin_cents == 700
    assert receipt.experiment_profit_cents == 500
    assert receipt.profit_caused_by_agent is False
    assert rank([receipt])[0]["economic_score_cents"] == 500

    print("PASS: harness boundary + profit accounting + causality membrane")


if __name__ == "__main__":
    main()
