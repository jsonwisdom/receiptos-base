"""Anchor contract and reference implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from attestation_schema import AttestationResult


class Anchor(ABC):
    @abstractmethod
    def anchor(self, result: AttestationResult) -> bool:
        ...


class NoOpAnchor(Anchor):
    def anchor(self, result: AttestationResult) -> bool:
        return True
