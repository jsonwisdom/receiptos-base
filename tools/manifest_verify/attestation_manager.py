"""
AttestationManager — pure orchestrator.

Takes one AttestationEnvelope, routes it through every registered
AttestationAdapter, and returns a list of standardized AttestationResult
contracts. Does not publish or anchor.
"""

from __future__ import annotations

from typing import Dict, List

from attestation_adapter import AttestationAdapter
from attestation_schema import AttestationEnvelope, AttestationResult


class AttestationManager:
    """
    Orchestrates multiple attestation adapters against a single envelope.
    Strictly coordinates packaging; publication and anchoring are orthogonal.
    """

    def __init__(self) -> None:
        self._adapters: Dict[str, AttestationAdapter] = {}

    def register_adapter(self, name: str, adapter: AttestationAdapter) -> None:
        self._adapters[name] = adapter

    def unregister_adapter(self, name: str) -> None:
        self._adapters.pop(name, None)

    @property
    def registered_adapters(self) -> List[str]:
        return list(self._adapters.keys())

    def create_attestations(self, envelope: AttestationEnvelope) -> List[AttestationResult]:
        results: List[AttestationResult] = []
        for name, adapter in self._adapters.items():
            try:
                result = adapter.create(envelope)
                if not result.adapter_name:
                    result.adapter_name = name
                results.append(result)
            except Exception as e:
                results.append(
                    AttestationResult(
                        adapter_name=name,
                        success=False,
                        envelope_digest="",
                        errors=[f"Adapter execution failed: {type(e).__name__}: {e}"],
                    )
                )
        return results
