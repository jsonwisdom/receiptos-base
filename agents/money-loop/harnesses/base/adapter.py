from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class MissionEnvelope:
    mission_id: str
    model_id: str
    harness_id: str
    input_root: str
    budget_cents: int
    time_limit_seconds: int
    authority_created: bool = False


class HarnessAdapter(ABC):
    """Common Money Loop harness boundary.

    Harness execution may produce artifacts and observations. It may not promote
    economic claims or create authority. Promotion belongs to the receipt layer.
    """

    adapter_id: str

    @abstractmethod
    def available(self) -> Dict[str, Any]:
        """Return an evidence-shaped availability observation."""

    @abstractmethod
    def execute(self, mission: MissionEnvelope) -> Dict[str, Any]:
        """Execute one mission and return an observation envelope only."""
