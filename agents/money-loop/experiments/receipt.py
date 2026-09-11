from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict


@dataclass(frozen=True)
class ExperimentReceipt:
    mission_id: str
    model_id: str
    harness_id: str
    input_root: str
    budget_cents: int
    time_limit_seconds: int
    artifact_root: str
    gross_revenue_cents: int
    direct_cost_cents: int
    infra_cost_cents: int
    contribution_margin_cents: int
    experiment_profit_cents: int
    profit_verified: bool
    profit_caused_by_agent: bool
    causal_attribution_status: str
    authority_created: bool = False

    def validate(self) -> None:
        if self.authority_created:
            raise ValueError("authority_created must remain false")
        if min(
            self.budget_cents,
            self.time_limit_seconds,
            self.gross_revenue_cents,
            self.direct_cost_cents,
            self.infra_cost_cents,
        ) < 0:
            raise ValueError("economic and limit fields must be non-negative")
        expected_cm = self.gross_revenue_cents - self.direct_cost_cents
        expected_profit = expected_cm - self.infra_cost_cents
        if self.contribution_margin_cents != expected_cm:
            raise ValueError("contribution margin mismatch")
        if self.experiment_profit_cents != expected_profit:
            raise ValueError("experiment profit mismatch")
        if self.profit_caused_by_agent and self.causal_attribution_status != "ESTABLISHED_BY_CONTROLLED_ANALYSIS":
            raise ValueError("causal attribution cannot be asserted without controlled analysis")

    def to_dict(self) -> Dict[str, object]:
        self.validate()
        return asdict(self)


def build_receipt(
    *,
    mission_id: str,
    model_id: str,
    harness_id: str,
    input_root: str,
    budget_cents: int,
    time_limit_seconds: int,
    artifact_root: str,
    gross_revenue_cents: int,
    direct_cost_cents: int,
    infra_cost_cents: int,
    profit_verified: bool,
) -> ExperimentReceipt:
    contribution_margin = gross_revenue_cents - direct_cost_cents
    experiment_profit = contribution_margin - infra_cost_cents
    return ExperimentReceipt(
        mission_id=mission_id,
        model_id=model_id,
        harness_id=harness_id,
        input_root=input_root,
        budget_cents=budget_cents,
        time_limit_seconds=time_limit_seconds,
        artifact_root=artifact_root,
        gross_revenue_cents=gross_revenue_cents,
        direct_cost_cents=direct_cost_cents,
        infra_cost_cents=infra_cost_cents,
        contribution_margin_cents=contribution_margin,
        experiment_profit_cents=experiment_profit,
        profit_verified=profit_verified,
        profit_caused_by_agent=False,
        causal_attribution_status="NOT_ESTABLISHED_SINGLE_RUN",
        authority_created=False,
    )
