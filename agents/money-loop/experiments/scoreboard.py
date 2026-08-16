from __future__ import annotations

from typing import Iterable, List, Dict

from agents.money_loop.experiments.receipt import ExperimentReceipt


def score(receipt: ExperimentReceipt) -> int:
    receipt.validate()
    if not receipt.profit_verified:
        return 0
    return receipt.experiment_profit_cents


def rank(receipts: Iterable[ExperimentReceipt]) -> List[Dict[str, object]]:
    rows = []
    for receipt in receipts:
        rows.append({
            "mission_id": receipt.mission_id,
            "model_id": receipt.model_id,
            "harness_id": receipt.harness_id,
            "economic_score_cents": score(receipt),
            "profit_verified": receipt.profit_verified,
            "profit_caused_by_agent": receipt.profit_caused_by_agent,
            "causal_attribution_status": receipt.causal_attribution_status,
            "authority_created": receipt.authority_created,
        })
    return sorted(rows, key=lambda r: r["economic_score_cents"], reverse=True)
