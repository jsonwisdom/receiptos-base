"""
Verification Gatekeeper

Hard invariant: a failed verification MUST never produce an attestation
envelope or any downstream witness.  This module is the single enforcement
point for that rule.
"""

from __future__ import annotations

from typing import Any, Dict, Protocol


class VerificationLike(Protocol):
    """Minimal structural type accepted by the gatekeeper."""
    valid: bool


class GatekeeperError(RuntimeError):
    """Raised when attestation is attempted after a failed verification."""
    pass


def enforce_attestation_gate(verification: VerificationLike | Dict[str, Any]) -> None:
    """
    Refuse to proceed if verification did not succeed.

    Accepts either a VerificationResult-like object or a plain dict
    (e.g. the JSON emitted by the verifier CLI).
    """
    if isinstance(verification, dict):
        ok = bool(verification.get("valid", False))
    else:
        ok = bool(getattr(verification, "valid", False))

    if not ok:
        raise GatekeeperError(
            "CRITICAL: Verification failed. Refusing to generate attestation envelope."
        )
