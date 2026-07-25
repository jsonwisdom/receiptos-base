"""
AttestationAdapter contract.

Adapters are responsible only for packaging an AttestationEnvelope
into a concrete format. They do not publish or anchor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from attestation_schema import AttestationEnvelope, AttestationResult


class AttestationAdapter(ABC):
    """
    Contract: turn an AttestationEnvelope into a packaged AttestationResult.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable adapter identifier used by the manager and results."""
        ...

    @abstractmethod
    def create(self, envelope: AttestationEnvelope) -> AttestationResult:
        """
        Package the envelope.

        Must never raise for ordinary packaging failures; instead return
        an AttestationResult with success=False and populated errors.
        Unexpected infrastructure errors may still raise.
        """
        ...
