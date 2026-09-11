from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List

from experiments.receipt import ExperimentReceipt, build_receipt


@dataclass(frozen=True)
class MatrixCell:
    run_id: str
    model_id: str
    harness_id: str


@dataclass(frozen=True)
class FrozenMission:
    mission_id: str
    input_root: str
    budget_cents: int
    time_limit_seconds: int
    authority_created: bool = False

    def validate(self) -> None:
        if self.authority_created:
            raise ValueError("authority_created must remain false")
        if self.budget_cents < 0 or self.time_limit_seconds < 0:
            raise ValueError("mission limits must be non-negative")
        if not self.input_root.startswith("sha256:"):
            raise ValueError("input_root must be content-addressed")


MODELS = ("openai/model-a", "deepseek/model-a", "local/model-a")
HARNESSES = ("harness/a", "deepseek/dsh-001", "harness/b")


def canonical_grid() -> List[MatrixCell]:
    cells: List[MatrixCell] = []
    n = 1
    for model_id in MODELS:
        for harness_id in HARNESSES:
            cells.append(MatrixCell(f"R{n:02d}", model_id, harness_id))
            n += 1
    return cells


def run_matrix(
    mission: FrozenMission,
    execute_cell: Callable[[MatrixCell, FrozenMission], ExperimentReceipt],
    cells: Iterable[MatrixCell] | None = None,
) -> List[ExperimentReceipt]:
    mission.validate()
    selected = list(cells or canonical_grid())
    receipts: List[ExperimentReceipt] = []
    for cell in selected:
        receipt = execute_cell(cell, mission)
        receipt.validate()
        if receipt.mission_id != mission.mission_id:
            raise ValueError("mission_id drift across matrix")
        if receipt.input_root != mission.input_root:
            raise ValueError("input_root drift across matrix")
        if receipt.budget_cents != mission.budget_cents:
            raise ValueError("budget drift across matrix")
        if receipt.time_limit_seconds != mission.time_limit_seconds:
            raise ValueError("time-limit drift across matrix")
        if receipt.model_id != cell.model_id or receipt.harness_id != cell.harness_id:
            raise ValueError("cell identity mismatch")
        receipts.append(receipt)
    return receipts


def synthetic_executor(cell: MatrixCell, mission: FrozenMission) -> ExperimentReceipt:
    """Deterministic fixture only. It proves orchestration, never real execution or revenue."""
    ordinal = int(cell.run_id[1:])
    gross = 1000 + ordinal * 10
    direct = 300 + ordinal
    infra = 200
    return build_receipt(
        mission_id=mission.mission_id,
        model_id=cell.model_id,
        harness_id=cell.harness_id,
        input_root=mission.input_root,
        budget_cents=mission.budget_cents,
        time_limit_seconds=mission.time_limit_seconds,
        artifact_root=f"sha256:synthetic-{cell.run_id.lower()}",
        gross_revenue_cents=gross,
        direct_cost_cents=direct,
        infra_cost_cents=infra,
        profit_verified=False,
    )
