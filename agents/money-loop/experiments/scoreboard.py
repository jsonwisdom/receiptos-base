from __future__ import annotations

from collections import defaultdict
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


def _mean(values: List[int]) -> float:
    return sum(values) / len(values) if values else 0.0


def aggregate_effects(receipts: Iterable[ExperimentReceipt]) -> Dict[str, object]:
    """Descriptive aggregation only; this does not establish causal attribution."""
    model_scores = defaultdict(list)
    harness_scores = defaultdict(list)
    interactions = defaultdict(list)
    rows = list(receipts)
    for receipt in rows:
        value = score(receipt)
        model_scores[receipt.model_id].append(value)
        harness_scores[receipt.harness_id].append(value)
        interactions[(receipt.model_id, receipt.harness_id)].append(value)

    return {
        "model_mean_score_cents": {k: _mean(v) for k, v in sorted(model_scores.items())},
        "harness_mean_score_cents": {k: _mean(v) for k, v in sorted(harness_scores.items())},
        "interaction_mean_score_cents": {
            f"{model_id} x {harness_id}": _mean(v)
            for (model_id, harness_id), v in sorted(interactions.items())
        },
        "causal_attribution_status": "NOT_ESTABLISHED_DESCRIPTIVE_AGGREGATION",
        "authority_created": False,
    }
