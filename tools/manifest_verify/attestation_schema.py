"""
ReplayOS Attestation contracts.

These types form the stable boundary between verification output and
any packaging / distribution / anchoring mechanism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SubjectRef:
    """Identifies the artifact that is the subject of the attestation."""
    type: str
    uri: str
    root_digest: str


@dataclass(frozen=True)
class VerificationSummary:
    """Minimal summary of a VerificationResult safe to embed in an envelope."""
    valid: bool
    integrity_ok: bool
    artifacts_ok: bool
    algorithm: str = "sha256"
    error_count: int = 0


@dataclass
class AttestationEnvelope:
    """Canonical unsigned payload that adapters package into concrete formats."""
    schema_version: str
    subject: SubjectRef
    verification: VerificationSummary
    signer_id: str
    timestamp_utc: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "subject": {
                "type": self.subject.type,
                "uri": self.subject.uri,
                "root_digest": self.subject.root_digest,
            },
            "verification": {
                "valid": self.verification.valid,
                "integrity_ok": self.verification.integrity_ok,
                "artifacts_ok": self.verification.artifacts_ok,
                "algorithm": self.verification.algorithm,
                "error_count": self.verification.error_count,
            },
            "signer_id": self.signer_id,
            "timestamp_utc": self.timestamp_utc,
            "metadata": self.metadata,
        }


@dataclass
class AttestationResult:
    """Standardized outcome produced by every AttestationAdapter."""
    adapter_name: str
    success: bool
    envelope_digest: str = ""
    reference: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
