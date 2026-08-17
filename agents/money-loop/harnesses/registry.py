from __future__ import annotations

from typing import Dict, Type

from harnesses.base.adapter import HarnessAdapter
from harnesses.deepseek_dsh.adapter_001 import DeepSeekDSHAdapter001


HARNESS_REGISTRY: Dict[str, Type[HarnessAdapter]] = {
    DeepSeekDSHAdapter001.adapter_id: DeepSeekDSHAdapter001,
}


def get_harness(adapter_id: str) -> HarnessAdapter:
    try:
        cls = HARNESS_REGISTRY[adapter_id]
    except KeyError as exc:
        raise KeyError(f"unknown harness adapter: {adapter_id}") from exc
    return cls()
